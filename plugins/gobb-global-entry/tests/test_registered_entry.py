"""Fake executable only: no native Gobb, provider, installation or credentials."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile


root = Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location("registered_entry", root.parents[1] / "tools/render_registered_entry.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
skill = (root / "skills/gobb/SKILL.md").read_text()
hooks = json.loads((root / "hooks/hooks.json").read_text())

with tempfile.TemporaryDirectory(prefix="gobb-entry-fixture-") as temporary:
    home = Path(temporary) / "home with 'quote"
    entry = home / ".local/bin/gobb"
    entry.parent.mkdir(parents=True)
    entry.write_text("#!/bin/sh\nprintf '%s\\n' \"$@\"\n")
    entry.chmod(0o700)
    epoch = "00000000-0000-4000-8000-000000000001"
    admitted = dict(activation_epoch=epoch, fixed_entry=str(entry),
                    absolute_cli_path=str(home / ".gobb/runtime/activations" / epoch / "gobb"),
                    cli_version="fixture", cli_source_commit="a" * 40,
                    cli_sha256="b" * 64, file_identity=dict(device="1", inode="2", size="3", mtime_ns="4"))
    rendered_skill, rendered_hooks = module.render(
        skill, hooks, user_home=str(home), admission=admitted, expected_admission=admitted.copy())
    command = rendered_hooks["hooks"]["SessionStart"][0]["hooks"][0]["command"]
    quoted = module.shlex.quote(str(entry))
    assert quoted in rendered_skill and command.startswith(quoted + " ")
    assert hooks["hooks"]["SessionStart"][0]["hooks"][0]["command"] == module.HOOK
    tick_home = str(home) + " `one``two"
    tick_admission = {**admitted, "fixed_entry": tick_home + "/.local/bin/gobb",
                      "absolute_cli_path": tick_home + "/.gobb/runtime/activations/" + epoch + "/gobb"}
    tick_skill, tick_hooks = module.render(skill, hooks, user_home=tick_home,
                                          admission=tick_admission, expected_admission=tick_admission.copy())
    tick_quote = module.shlex.quote(tick_admission["fixed_entry"])
    assert "```" + tick_quote + "```" in tick_skill
    assert "```" + tick_quote + " version --json```" in tick_skill
    assert tick_hooks["hooks"]["SessionStart"][0]["hooks"][0]["command"] == tick_quote + " agent-context --hook-input=session-start"
    assert module.code_span("`edge``") == "``` `edge`` ```"
    result = subprocess.run(["/bin/sh", "-c", command], env={"PATH": "/nonexistent"},
                            capture_output=True, text=True, check=True)
    assert result.stdout.splitlines() == ["agent-context", "--hook-input=session-start"]
    conflicting = Path(temporary) / "conflicting-bin"
    conflicting.mkdir()
    other = conflicting / "gobb"
    other.write_text("#!/bin/sh\nexit 91\n")
    other.chmod(0o700)
    assert subprocess.run(["/bin/sh", "-c", command], env={"PATH": str(conflicting)},
                          capture_output=True).returncode == 0
    for change in ({"activation_epoch": "changed"}, {"cli_sha256": "c" * 64},
                   {"fixed_entry": "/unconfirmed/gobb"}):
        try:
            module.render(skill, hooks, user_home=str(home), admission={**admitted, **change},
                          expected_admission=admitted)
        except ValueError:
            pass
        else:
            raise AssertionError("changed admission accepted")
    malformed = {**admitted, "activation_epoch": "invalid"}
    try:
        module.render(skill, hooks, user_home=str(home), admission=malformed,
                      expected_admission=malformed)
    except ValueError:
        pass
    else:
        raise AssertionError("malformed admission accepted")
    entry.unlink()
    assert subprocess.run(["/bin/sh", "-c", command], env={"PATH": "/nonexistent"},
                          capture_output=True).returncode != 0
print("registered entry: PASS (offline fixture; admission custody remains caller-owned)")
