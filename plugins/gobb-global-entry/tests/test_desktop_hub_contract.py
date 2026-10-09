"""Instruction contract cases; native agent behavior is a separate release gate."""
import json
import sys
from pathlib import Path

skill = (Path(__file__).parents[1] / "skills/gobb/SKILL.md").read_text()
for rule in (
    "only with capability `desktop_hub_facts_v1` and `contract: 1`",
    "stop the affected Hub operation without legacy fallback",
    "do not translate unknown into signed out",
    "do not offer another login or project selection",
    "Desktop folder connection only",
    "use Desktop Account recovery once while retaining the recorded association",
    "pending requires completing the existing Desktop operation",
    "grant_status: not_checked",
    "These are local records, not current remote authorization",
    "require both `desktop_hub_facts_v1` and `desktop_hub_read_file_v1`",
    "Require the returned organization/project to match the recorded association",
    "without listing other files",
    "Never work around it with legacy login",
):
    assert rule in skill, rule


def advice(capabilities, fact, exact_path=None):
    if "desktop_hub_facts_v1" not in capabilities:
        return "legacy", None
    if not isinstance(fact, dict) or fact.get("contract") != 1 or fact.get("grant_status") != "not_checked":
        return "stop", None
    account, folder = fact.get("account_status"), fact.get("folder_status")
    if account not in {"unavailable", "recorded", "expired", "signed_out", "pending", "unknown"} or folder not in {"unregistered", "unlinked", "linked", "local", "conflict", "unknown"}:
        return "stop", None
    if fact.get("reason") or account == "unknown" or folder in {"conflict", "unknown"}:
        return "stop", None
    if account == "unavailable":
        return ("legacy", None) if fact.get("verification") == "not_checked" and folder == "unregistered" and not any(fact.get(k) for k in ("profile_id", "folder_id", "organization_id", "project_id")) else ("stop", None)
    if not fact.get("profile_id") or fact.get("verification") != "local_recorded":
        return "stop", None
    if folder == "linked" and (not all(fact.get(k) for k in ("folder_id", "organization_id", "project_id")) or type(fact.get("association_revision")) is not int or fact["association_revision"] <= 0):
        return "stop", None
    if folder == "local":
        return "local", None
    if account in {"expired", "signed_out"}:
        return "desktop_recovery", None
    if account == "pending":
        return "complete_pending", None
    if folder in {"unregistered", "unlinked"}:
        return "desktop_folder_connection", None
    if exact_path is None:
        return "retain_project", None
    if "desktop_hub_read_file_v1" not in capabilities:
        return "update", None
    return "read", ["gobb", "hub", "read-file", "--path", exact_path, "--json"]


caps = ["desktop_hub_facts_v1", "desktop_hub_read_file_v1"]
linked = dict(contract=1, account_status="recorded", folder_status="linked", grant_status="not_checked", verification="local_recorded", profile_id="profile", folder_id="folder", organization_id="org", project_id="project", association_revision=1)
cases = [("linked", caps, linked, None, "retain_project"), ("exact_read", caps, linked, "docs/a.md", "read"), ("missing_read", caps[:1], linked, "docs/a.md", "update"), ("old_cli", [], None, None, "legacy"), ("missing_facts", caps, None, None, "stop")]
for account, action in (("expired", "desktop_recovery"), ("signed_out", "desktop_recovery"), ("pending", "complete_pending"), ("unknown", "stop")):
    cases.append((account, caps, dict(linked, account_status=account), None, action))
for folder, action in (("unregistered", "desktop_folder_connection"), ("unlinked", "desktop_folder_connection"), ("local", "local"), ("conflict", "stop"), ("unknown", "stop")):
    cases.append((folder, caps, dict(linked, folder_status=folder), None, action))
for name, delta in (("bad_contract", {"contract":2}), ("missing_project", {"project_id":""}), ("account_mismatch", {"reason":"account_mismatch"}), ("metadata_is_not_grant", {"grant_status":"authorized"})):
    cases.append((name, caps, dict(linked, **delta), "docs/a.md", "stop"))
cases.append(("absent_desktop", caps, dict(contract=1,account_status="unavailable",folder_status="unregistered",verification="not_checked",grant_status="not_checked"),None,"legacy"))
cases.append(("contradictory_absence", caps, dict(linked, account_status="unavailable", verification="not_checked"), None, "stop"))
for name, capabilities, fact, path, expected in cases:
    actual, command = advice(capabilities, fact, path)
    assert actual == expected, (name, actual)
    assert command is None or command == ["gobb", "hub", "read-file", "--path", path, "--json"]
    print(f"{name}: {actual}")

if len(sys.argv) == 2:
    response = json.loads(Path(sys.argv[1]).read_text())
    assert response["contract_version"] == 1
    actual, command = advice(response["capabilities"], response["facts"]["desktop_hub"], "docs/a.md")
    assert actual == "read" and command == ["gobb", "hub", "read-file", "--path", "docs/a.md", "--json"]
    print("shared CLI producer fixture: read exact recorded Project")
