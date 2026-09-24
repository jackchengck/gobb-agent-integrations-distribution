"""Use the CLI pinned to this installed Codex profile, without PATH lookup."""

import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import uuid


MAX_INPUT = 16_384
MAX_CONTEXT = 65_536
HOOK_TIMEOUT = 8
HEX64 = re.compile(r"[0-9a-f]{64}\Z")


class Refusal(Exception):
    def __init__(self, code, action):
        self.code = code
        self.action = action


def refuse(code="unsafe_launcher", action="repair_install"):
    raise Refusal(code, action)


def owned_regular(path, mode=None):
    try:
        info = path.lstat()
    except OSError:
        refuse()
    if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o022:
        refuse()
    if mode is not None and info.st_mode & 0o777 != mode:
        refuse()
    return info


def owned_directory(path):
    try:
        info = path.lstat()
    except OSError:
        refuse()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o022:
        refuse()


def read_object(path):
    owned_regular(path, 0o600)
    try:
        if path.stat().st_size > MAX_CONTEXT:
            refuse()
        value = json.loads(path.read_text())
    except (OSError, ValueError, UnicodeError):
        refuse()
    if not isinstance(value, dict):
        refuse()
    return value


def absolute_path(value):
    if not isinstance(value, str) or not value or not os.path.isabs(value):
        refuse()
    path = Path(value)
    if str(path.resolve()) != value:
        refuse()
    return path


def launcher():
    script = Path(__file__)
    if str(script.resolve()) != str(script):
        refuse()
    package = script.parent.parent
    # Installed layout: <CODEX_HOME>/plugins/cache/<marketplace>/<plugin>/<version>/.
    if (len(package.parts) < 7 or package.parent.parent.parent.name != "cache"
            or package.parent.parent.parent.parent.name != "plugins" or package.parent.name != "gobb"):
        refuse("upgrade_required", "update_plugin")
    home = package.parent.parent.parent.parent.parent
    for path in (home, home / "plugins", home / "plugins/cache", package.parent.parent,
                 package.parent, package, script.parent):
        owned_directory(path)
    owned_regular(script)
    manifest = read_object(home / "gobb/launcher.json")
    owned_directory(home / "gobb")
    state = absolute_path(manifest.get("desktop_state_root"))
    for path in (state, state / "collaboration"):
        owned_directory(path)
    profile = read_object(state / "collaboration/profile-v1.json")
    profile_id = manifest.get("profile_id")
    try:
        uuid.UUID(profile_id)
    except (TypeError, ValueError):
        refuse()
    if (manifest.get("contract") != 1 or profile.get("contract") != 1
            or manifest.get("codex_home") != str(home)
            or profile.get("codex_home") != str(home)
            or profile.get("desktop_state_root") != str(state)
            or profile.get("profile_id") != profile_id):
        refuse("upgrade_required", "update_plugin")
    binary = absolute_path(manifest.get("absolute_cli_path"))
    for path in reversed(binary.parents):
        if path == Path("/"):
            continue
        try:
            info = path.lstat()
        except OSError:
            refuse()
        if not stat.S_ISDIR(info.st_mode) or (info.st_uid not in (0, os.getuid())):
            refuse()
        if info.st_mode & 0o022 and not (info.st_uid == 0 and info.st_mode & stat.S_ISVTX):
            refuse()
    info = owned_regular(binary)
    identity = manifest.get("file_identity")
    if not isinstance(identity, dict) or any(type(identity.get(field)) is not int
            or identity[field] < 0 for field in ("device", "inode", "size", "mtime_ns")):
        refuse()
    if identity != dict(device=info.st_dev, inode=info.st_ino, size=info.st_size,
                        mtime_ns=info.st_mtime_ns):
        refuse()
    digest = manifest.get("cli_sha256")
    try:
        actual_digest = hashlib.sha256(binary.read_bytes()).hexdigest()
    except OSError:
        refuse()
    if (not isinstance(digest, str) or not HEX64.fullmatch(digest)
            or actual_digest != digest
            or not isinstance(manifest.get("cli_version"), str)
            or not manifest["cli_version"]
            or not isinstance(manifest.get("cli_source_commit"), str)
            or not manifest["cli_source_commit"]):
        refuse()
    return binary, home


def context_folder():
    raw = sys.stdin.buffer.read(MAX_INPUT + 1)
    if len(raw) > MAX_INPUT:
        refuse("invalid_input", "retry_with_valid_input")
    try:
        event = json.loads(raw)
    except (ValueError, UnicodeError):
        refuse("invalid_input", "retry_with_valid_input")
    if not isinstance(event, dict) or event.get("hook_event_name") != "SessionStart":
        refuse("invalid_input", "retry_with_valid_input")
    return absolute_path(event.get("cwd"))


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("--session-start", "--skill"):
        refuse("invalid_input", "retry_with_valid_input")
    if sys.argv[1] == "--session-start":
        if len(sys.argv) != 2:
            refuse("invalid_input", "retry_with_valid_input")
        folder = context_folder()
        args = ["agent-context", "--if-managed", "--phase", "start", "--json"]
    else:
        if len(sys.argv) < 6 or sys.argv[2] != "--cwd" or sys.argv[4] != "--":
            refuse("invalid_input", "retry_with_valid_input")
        folder = absolute_path(sys.argv[3])
        args = sys.argv[5:]
        if any(arg in ("--cwd", "--config") or arg.startswith(("--cwd=", "--config="))
               for arg in args):
            refuse("invalid_input", "retry_with_valid_input")
    binary, home = launcher()
    try:
        environment = os.environ.copy()
        environment["CODEX_HOME"] = str(home)
        environment.pop("GOBB_HUB_TOKEN", None)
        if sys.argv[1] == "--skill":
            result = subprocess.run([str(binary), "--cwd", str(folder), *args],
                                    check=False, env=environment)
            sys.exit(result.returncode if result.returncode >= 0 else 1)
        result = subprocess.run([str(binary), "--cwd", str(folder), *args],
                                capture_output=True, timeout=HOOK_TIMEOUT,
                                check=False, env=environment)
    except (OSError, subprocess.TimeoutExpired):
        refuse("cli_unavailable", "repair_install")
    if len(result.stdout) > MAX_CONTEXT:
        refuse("cli_unavailable", "repair_install")
    if result.returncode:
        refuse("cli_unavailable", "repair_install")
    if not result.stdout.strip():
        return
    try:
        data = json.loads(result.stdout)
    except (ValueError, UnicodeError):
        refuse("invalid_cli_result", "repair_install")
    if not isinstance(data, dict):
        refuse("invalid_cli_result", "repair_install")
    if data.get("contract_version") != 1 or data.get("managed") is not True:
        refuse("invalid_cli_result", "repair_install")
    context = json.dumps(data, separators=(",", ":"), ensure_ascii=True)
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart",
                                             "additionalContext": context}}))


if __name__ == "__main__":
    try:
        if sys.argv[1:] == ["--self-test"]:
            if sys.stdin.buffer.read(1):
                refuse("invalid_input", "retry_with_valid_input")
        else:
            main()
    except Refusal as error:
        print(json.dumps({"code": error.code, "next_action": error.action}), file=sys.stderr)
        sys.exit(1)
