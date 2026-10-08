"""Build-time rendering only; caller must validate runtime custody before/after use."""

import copy
from pathlib import PurePosixPath
import shlex
import re
import uuid


START = "<!-- gobb:desktop-registered-entry -->"
END = "<!-- /gobb:desktop-registered-entry -->"
HOOK = "gobb agent-context --hook-input=session-start"


def code_span(value):
    delimiter = "`" * (max((len(run) for run in re.findall(r"`+", value)), default=0) + 1)
    padding = " " if value.startswith(("`", " ")) or value.endswith(("`", " ")) else ""
    return delimiter + padding + value + padding + delimiter


def render(skill, hooks, *, user_home, admission, expected_admission):
    # Equality retains the caller's reviewed epoch/hash/identity, not self-attestation.
    if not isinstance(admission, dict) or admission != expected_admission:
        raise ValueError("runtime_admission_changed")
    home = PurePosixPath(user_home)
    if (not home.is_absolute() or str(home) != user_home or ".." in home.parts
            or any(ord(c) < 32 or ord(c) == 127 for c in user_home)):
        raise ValueError("invalid_home")
    entry = str(home / ".local/bin/gobb")
    required = {"activation_epoch", "fixed_entry", "absolute_cli_path", "cli_version",
                "cli_source_commit", "cli_sha256", "file_identity"}
    if (set(admission) != required or admission["fixed_entry"] != entry
            or not all(admission[k] for k in required)):
        raise ValueError("runtime_admission_required")
    epoch = admission["activation_epoch"]
    try:
        valid_epoch = str(uuid.UUID(epoch)) == epoch
    except (ValueError, TypeError, AttributeError):
        valid_epoch = False
    identity = admission["file_identity"]
    if (not valid_epoch
            or admission["absolute_cli_path"] != str(home / ".gobb/runtime/activations" / epoch / "gobb")
            or not isinstance(admission["cli_version"], str)
            or any(ord(c) < 32 or ord(c) == 127 for c in admission["cli_version"])
            or not isinstance(admission["cli_source_commit"], str)
            or not re.fullmatch(r"[0-9a-f]{40}", admission["cli_source_commit"])
            or not isinstance(admission["cli_sha256"], str)
            or not re.fullmatch(r"[0-9a-f]{64}", admission["cli_sha256"])
            or not isinstance(identity, dict)
            or set(identity) != {"device", "inode", "size", "mtime_ns"}
            or any(not isinstance(value, str) or not re.fullmatch(r"[0-9]+", value)
                   for value in identity.values())
            or int(identity["inode"]) == 0 or int(identity["size"]) == 0):
        raise ValueError("runtime_admission_required")
    if skill.count(START) != 1 or skill.count(END) != 1:
        raise ValueError("skill_binding_marker")
    before, section = skill.split(START)
    _, after = section.split(END)
    quoted = shlex.quote(entry)
    executable = code_span(quoted)
    binding = (f"\nDesktop-managed registered global entry: {executable}. "
               f"For every Gobb command below, replace only the executable `gobb` "
               f"with {executable}; retain its arguments and canonical `--cwd`. "
               "SessionStart uses the same entry. Never select a PATH executable, "
               "activation payload, plugin-cache resolver or project launcher instead. "
               "Missing or changed registration requires Repair; do not retry. "
               f"Version query: {code_span(quoted + ' version --json')}.\n")
    rendered = copy.deepcopy(hooks)
    try:
        rows = rendered["hooks"]["SessionStart"]
        commands = rows[0]["hooks"]
        if (len(rows) != 1 or rows[0]["matcher"] != "startup|resume|clear|compact"
                or len(commands) != 1 or commands[0] != {
                    "type": "command", "command": HOOK, "timeout": 10}):
            raise ValueError("hook_binding_shape")
        commands[0]["command"] = quoted + " agent-context --hook-input=session-start"
    except (KeyError, IndexError, TypeError) as error:
        raise ValueError("hook_binding_shape") from error
    return before + START + binding + END + after, rendered
