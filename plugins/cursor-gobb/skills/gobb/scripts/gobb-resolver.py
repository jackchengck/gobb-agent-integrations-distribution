"""Run the owner-bound Gobb CLI from this installed Cursor Skill, never PATH."""

import hashlib
import json
import os
from pathlib import Path
import pwd
import stat
import sys
import uuid


MAX_PROFILE = 4096
SCRIPT_TAIL = (".cursor", "plugins", "local", "gobb", "skills", "gobb", "scripts", "gobb-resolver.py")


class Refusal(Exception):
    pass


def refuse():
    raise Refusal


def absolute(value):
    if not isinstance(value, str) or not os.path.isabs(value):
        refuse()
    path = Path(value)
    try:
        resolved = path.resolve()
    except (OSError, RuntimeError):
        refuse()
    if str(path) != value or resolved != path:
        refuse()
    return path


def directory(path):
    try:
        info = path.lstat()
    except OSError:
        refuse()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid not in (0, os.getuid()):
        refuse()
    if info.st_mode & 0o022 and not (info.st_uid == 0 and info.st_mode & stat.S_ISVTX):
        refuse()


def parents(path):
    for parent in reversed(path.parents):
        if parent != Path("/"):
            directory(parent)


def owned_json(path, expected):
    parents(path)
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        with os.fdopen(fd, "rb") as handle:
            info = os.fstat(handle.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o600:
                refuse()
            data = handle.read(MAX_PROFILE + 1)
    except OSError:
        refuse()
    if len(data) > MAX_PROFILE:
        refuse()
    try:
        value = json.loads(data)
    except (ValueError, UnicodeError):
        refuse()
    if not isinstance(value, dict) or set(value) != expected:
        refuse()
    return value


def verified_cli():
    script = absolute(os.path.abspath(__file__))
    if tuple(script.parts[-len(SCRIPT_TAIL):]) != SCRIPT_TAIL:
        refuse()
    parents(script)
    info = script.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o600:
        refuse()
    home = script.parents[7]
    try:
        account_home = absolute(pwd.getpwuid(os.geteuid()).pw_dir)
    except (KeyError, OSError, AttributeError):
        refuse()
    if home != account_home or home.lstat().st_mode & 0o022:
        refuse()
    locator = owned_json(home / ".gobb/desktop/locator-v1.json",
                         {"contract", "profile_id", "desktop_state_root"})
    if type(locator["contract"]) is not int or locator["contract"] != 1:
        refuse()
    if not isinstance(locator["profile_id"], str):
        refuse()
    try:
        if str(uuid.UUID(locator["profile_id"])) != locator["profile_id"]:
            refuse()
    except (TypeError, ValueError):
        refuse()
    state = absolute(locator["desktop_state_root"])
    profile = owned_json(state / "collaboration/profile-v2.json",
                         {"contract", "profile_id", "desktop_state_root", "absolute_cli_path",
                          "cli_version", "cli_source_commit", "cli_sha256", "file_identity"})
    if (type(profile["contract"]) is not int or profile["contract"] != 2 or
            profile["profile_id"] != locator["profile_id"] or
            profile["desktop_state_root"] != str(state) or
            not isinstance(profile["cli_version"], str) or not profile["cli_version"] or
            not isinstance(profile["cli_source_commit"], str) or not profile["cli_source_commit"]):
        refuse()
    binary = absolute(profile["absolute_cli_path"])
    parents(binary)
    identity = profile["file_identity"]
    if (not isinstance(identity, dict) or
            set(identity) != {"device", "inode", "size", "mtime_ns"} or
            any(type(identity[key]) is not int or identity[key] < 0 for key in identity)):
        refuse()
    digest = profile["cli_sha256"]
    if not isinstance(digest, str) or len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
        refuse()
    try:
        fd = os.open(binary, os.O_RDONLY | os.O_NOFOLLOW)
        with os.fdopen(fd, "rb") as handle:
            info = os.fstat(handle.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_uid not in (0, os.getuid()) or info.st_mode & 0o022:
                refuse()
            actual = {"device": info.st_dev, "inode": info.st_ino, "size": info.st_size,
                      "mtime_ns": info.st_mtime_ns}
            if identity != actual:
                refuse()
            hasher = hashlib.sha256()
            for chunk in iter(lambda: handle.read(65536), b""):
                hasher.update(chunk)
            if hasher.hexdigest() != digest:
                refuse()
        after = os.stat(binary, follow_symlinks=False)
        if (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns) != (
                info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns):
            refuse()
    except OSError:
        refuse()
    return binary, home


def main():
    args = sys.argv[1:]
    if not args or any(arg in ("--cwd", "--config") or arg.startswith(("--cwd=", "--config=")) for arg in args):
        refuse()
    binary, home = verified_cli()
    environment = os.environ.copy()
    environment["HOME"] = str(home)
    environment.pop("CODEX_HOME", None)
    environment.pop("GOBB_DESKTOP_STATE_ROOT", None)
    environment.pop("GOBB_HUB_TOKEN", None)
    os.execve(binary, [str(binary), *args], environment)


if __name__ == "__main__":
    try:
        main()
    except (Refusal, OSError):
        print('{"code":"unsafe_launcher","next_action":"repair_install"}', file=sys.stderr)
        sys.exit(1)
