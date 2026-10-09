from pathlib import Path


skill = (Path(__file__).parents[1] / "skills/gobb/SKILL.md").read_text()
decision = next(line for line in skill.splitlines() if line.startswith("Never infer"))
exact_authority = decision.split(". Exact ", 1)[1].split(". Otherwise", 1)[0]
independent_gates = decision.split(". Independent ", 1)[1]

non_approved = {state for state in ("required", "stale", "unavailable") if f"`{state}`" in exact_authority}
exact_authority_writes = "active-task authorization for an existing target and role permits only that named write without another prompt" in exact_authority
changed_scope_prompts = "a changed target or role still requires a focused prompt" in exact_authority
separate_gates = {gate for gate in ("authority", "publication", "policy", "safety") if gate in independent_gates}
material_history = next(line for line in skill.splitlines() if line.startswith("Record material decisions"))

for contract in (
    "when they happen",
    "retain them in the smallest durable owner after completion",
    "do not limit retention to facts needed by a future task",
):
    assert contract in material_history, f"missing material-history contract: {contract}"


for contract in (
    "describes Gobb metadata, not the output of a project command with a similar name",
    "a request mentioning Gobb does not establish a managed repository",
    "stop Gobb calls and include one actionable repair",
    "ignore any workflow/auto-log fields in that response",
    "Stop documentation writes governed by that workflow",
    "Check required index authorization before a coupled document/index transition",
    "retain the observed cause, correction and verification result together",
    "Preserve any missing continuity in one permitted working-state record",
    "Structural readiness does not establish correct task meaning",
    "When the CLI reports `git_not_applicable`",
    "do not claim Git-derived ignored status, a clean working tree, change coverage or history",
    "Review the documentation impact of task-known changes",
    "no Git result does not waive that review or grant write authority",
):
    assert contract in skill, f"missing correction contract: {contract}"


for contract in (
    "## Hub read-only context",
    "existing `hub_onboarding_facts_v1`",
    "`facts.hub_project_selection.status` is `selected` as local continuity rather than remote proof",
    "exact active-task request naming one repository-relative literal path",
    "authorizes its content into the current AI task/destination",
    "changed destination or scope requires a focused decision",
    "`gobb hub read-file --path <literal-path> --json`",
    "current server authorization",
    "non-empty exact commit and matching returned path",
    "CLI-returned commit/tree/path/object identifiers",
    "Stop once on failure, expiry, authorization failure, malformed output, or missing exact commit/path",
    "Never list/enumerate paths, infer/normalize a path, manufacture connection, use MCP or a token",
    "write/create/save/submit/upload",
    "retain/send the body outside the current authorized task",
    "never invent a draft label",
):
    assert contract in skill, f"missing Hub read-only context contract: {contract}"


def outcome(state, changed_target=False, changed_role=False, gate=None):
    if gate:
        return "decision" if gate in separate_gates else "missing contract"
    if changed_target or changed_role:
        return "prompt" if changed_scope_prompts else "missing contract"
    return "write" if exact_authority_writes and state in non_approved else "missing contract"


cases = (
    ("exact-required", ("required",), "write"),
    ("exact-stale", ("stale",), "write"),
    ("exact-unavailable", ("unavailable",), "write"),
    ("changed-target", ("required", True), "prompt"),
    ("changed-role", ("required", False, True), "prompt"),
    ("authority-gate", ("required", False, False, "authority"), "decision"),
    ("publication-gate", ("required", False, False, "publication"), "decision"),
    ("policy-gate", ("required", False, False, "policy"), "decision"),
    ("safety-gate", ("required", False, False, "safety"), "decision"),
)

for name, inputs, expected in cases:
    actual = outcome(*inputs)
    assert actual == expected, f"{name}: expected {expected}, got {actual}"
    print(f"{name}: {actual}")
