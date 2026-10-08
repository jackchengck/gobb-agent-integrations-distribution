---
name: gobb
description: Offer optional Gobb onboarding, follow verified context, and proactively maintain durable repository documentation. Use when a repository contains .gobb, Gobb context appears, Gobb installation or setup is relevant, or work must plan, propose, decide, implement, verify, resume, checkpoint, hand off, or preserve durable documentation, including in an unmanaged repository that could adopt Gobb.
---

# Gobb

Use the Gobb CLI as the only authority for Gobb repository, context, documentation, working-state, and structural completion facts. Verify the requested product behavior with that project's own commands: `gobb status` describes Gobb metadata, not the output of a project command with a similar name.

For every Gobb CLI command below, invoke the user's installed global `gobb` with an explicitly selected canonical folder: `gobb --cwd <canonical-folder> <Gobb arguments>`. Ordinary local commands do not require Desktop, a Desktop profile, a versioned plugin-cache script, or Hub login. Use the registered global installation; if `gobb` is unavailable or installation reports a conflicting PATH entry, stop with Update/Repair guidance. Never retry through a different plugin copy or unconfirmed executable. Preserve the exact-path Hub read-only limits below.

<!-- gobb:desktop-registered-entry -->
For a Desktop-managed installation, the installer must replace this paragraph with the shell-quoted stable global entry from its freshly validated runtime admission, and render that same entry into SessionStart. Until that binding is supplied, do not guess an absolute fallback or invoke it to self-attest. Other global installations retain the PATH behavior above. A supplied Desktop binding takes precedence over PATH for every Gobb command shown below; missing or changed registration requires Repair, not another executable. Use `gobb version --json` for version queries, never `gobb --version`.
<!-- /gobb:desktop-registered-entry -->

## Start

1. Use Gobb context for project decisions, rules, plans, findings, history, and documentation work. Reuse current trusted session-start facts for the same canonical repository and already-read context for the same subject while unchanged; otherwise refresh missing or stale facts, or a changed repository, with gobb --cwd <canonical-folder> agent-context --if-managed --phase start --json. Read safe CLI-required paths first, then the smallest routed category index and selected files needed for the task. Limit native reads/search to those selected exact files or the limited routed subtree; never substitute a whole-docs search for index-first routing. Code-only work makes zero optional documentation queries while retaining required context and guard checks. If required or selected context is missing or unsafe, follow existing failure/next_actions rules and stop the affected work.
2. If the CLI is missing and `.gobb` metadata exists or this task previously verified that the repository is managed, report one concise repair action immediately and do not claim Gobb validation. Otherwise use the missing-CLI onboarding rule when documentation becomes relevant; a request mentioning Gobb does not establish a managed repository. On a timeout or command error, stop Gobb calls and include one actionable repair in the response, such as checking the failing executable or hook environment before a later run. Do not retry, offer initialization, or claim Gobb validation.
3. If the command succeeds without output, treat the repository as unmanaged. Continue normally and use the onboarding rule below only when documentation becomes relevant.
4. If metadata is damaged or invalid, do not load referenced paths. Surface `issues` and `next_actions`; use `gobb doctor` only when more diagnosis is useful.
5. Require `contract_version: 1` and capability `proactive_documentation_workflow_v1` for checkpoint and finish behavior. Without them, report the incompatibility and use startup-only behavior.
6. Do not edit through a blocked guard or unsafe required context.
7. For valid output, read every safe `required_context` path before editing. Then use `documentation.indexes` to load only the smallest relevant category and task documents. Do not recursively load archives, reports, or old handoffs.
8. Measure optional selected files by repeating `--context-path` on a start call and use `context_footprint.selected` as the record.

## Desktop Hub Account and folder

Consume `facts.desktop_hub` only with capability `desktop_hub_facts_v1` and `contract: 1`. Account status is `unavailable`, `recorded`, `expired`, `signed_out`, `pending`, or `unknown`; folder status is `unregistered`, `unlinked`, `linked`, `local`, `conflict`, or `unknown`. Require `grant_status: not_checked`; recorded identity has `verification: local_recorded` and a non-empty profile ID. Linked facts additionally require folder, organization and project IDs plus a positive association revision. `unavailable` requires `folder_status: unregistered`, `verification: not_checked`, and no recorded profile/folder/project identifiers. These are local records, not current remote authorization. If the capability is declared but facts are missing, malformed, unknown, conflicting, or have a non-empty reason, stop the affected Hub operation without legacy fallback; do not translate unknown into signed out.

With a recorded Account and linked folder, retain this exact Project and do not offer another login or project selection. A recorded Account with an unregistered or unlinked folder needs Desktop folder connection only. For expired or signed-out Account records, use Desktop Account recovery once while retaining the recorded association; pending requires completing the existing Desktop operation. Do not read profile files or Keychain, copy tokens, refresh sessions, restore consent, register a folder, or change bindings automatically. Local mode still prevents Hub work. With no Desktop capability, preserve legacy behavior; with valid unavailable facts, legacy onboarding remains available. Legacy `hub_connection` and `hub_project_selection` retain their original meaning and cannot override a linked Desktop Project.

## P6a Local Work Mode

Apply this section only when the start response includes capability `local_work_mode_v1`; otherwise preserve the existing behavior. Read `facts.work_mode` as a CLI fact. Suppress the Local/connect offer when valid Desktop facts record an Account or linked folder; use the Desktop guidance above instead:

- With `mode: local`, continue the local Gobb workflow. Do not use retained Hub facts or initiate or offer Hub or upload work.
- With `mode: unselected` and `next_action: continue_existing_work`, continue local work without claiming remote health, login, eligibility, organization, or destination.
- With `mode: unselected` and `next_action: choose_local_or_connect_hub`, offer `gobb hub local` once. State that Hub connection is unavailable unless a later CLI fact explicitly reports it.

## Hub Onboarding Guard

When Desktop capability is present, use the Desktop guidance first; only valid unavailable Desktop facts permit legacy onboarding. Consume Hub onboarding only when the start response includes `hub_onboarding_facts_v1`. Its nonsecret `facts.hub_connection` has `status`, `verification`, issuer/resource, organization/connection, consent scopes/allow-set, and expiry; `facts.hub_project_selection` has `status` (`unselected`, `selected`, or `inactive`) and connection/organization/project/revision identifiers. With `facts.work_mode.next_action: choose_local_or_connect_hub` and explicit no-profile/not-logged-in facts, offer Local or `gobb hub login --hub-origin <hub> --json`; after the user chooses Hub, treat that JSON as a one-turn receipt, then use `gobb hub connection --json`. Only `connection` JSON with `status: connected` and `verification: observed` may offer either `gobb hub select-project --project ID --json` for an existing project ID or Hub Web at `/app/organizations/<org>` for a new project; after Web creation, use `gobb hub login --replace`, then connection and explicit selection. A later `selected` project record is local-recorded continuity only: it may continue that local choice, while the eventual operation performs current server authorization. A consent allow-set is not a current grant; login is read scope only. Absent or malformed facts preserve current behavior. Never use an onboarding scope, API create, or legacy-token fallback.

## Hub read-only context

Only when start includes the existing `hub_onboarding_facts_v1`, `facts.hub_project_selection.status` is `selected` as local continuity rather than remote proof, and the user makes an exact active-task request naming one repository-relative literal path, that request authorizes its content into the current AI task/destination; a changed destination or scope requires a focused decision. Invoke `gobb hub read-file --path <literal-path> --json` as current server authorization. Require a returned non-empty exact commit and matching returned path; report only CLI-returned commit/tree/path/object identifiers. Stop once on failure, expiry, authorization failure, malformed output, or missing exact commit/path. Never list/enumerate paths, infer/normalize a path, manufacture connection, use MCP or a token, write/create/save/submit/upload, or retain/send the body outside the current authorized task; never invent a draft label.

For the Desktop route, require both `desktop_hub_facts_v1` and `desktop_hub_read_file_v1`, valid Desktop facts with `account_status: recorded`, `folder_status: linked`, and no reason. The same exact active-task request naming one repository-relative literal path authorizes `gobb hub read-file --path <literal-path> --json` for this recorded Project. This route supports only `.md` within configured public/private documentation endpoints. The command validates the current Desktop grant and exact path without listing other files. Require the returned organization/project to match the recorded association, a non-empty exact commit and matching path. Apply all read-only context limits above; if the read capability is missing or the command fails, stop once with Update/Repair or Desktop recovery guidance. Never work around it with legacy login, direct MCP, credential copying, inventory, pull, or restore.

## Onboarding

Evaluate onboarding at the durable documentation moments listed below, not at every session start or message.

- Missing CLI with neither `.gobb` metadata nor prior verified managed state: ask directly once per active task whether to install Gobb for durable repository documentation. Repair-only guidance is not this offer. A task prohibition on actual installation or repair does not waive this optional offer: ask it and stop; an explicit user decline remains controlling. State that installation does not initialize the repository or approve writes. After explicit approval, use only a supported installation source available in the environment, then rerun start. If no supported source is available, report that blocker; do not invent one.
- Unmanaged repository: offer once per active task to initialize Gobb documentation management. Explain that setup non-destructively creates `.gobb` metadata, missing public workflow and style files, an ignored local continuity boundary, and a managed AI-instruction block; it does not grant auto-log approval. After explicit approval, run `gobb init --no-input --integrations none --documentation setup`, rerun start, and read every returned required-context path before another write.
- Declined offer: continue without Gobb and do not repeat the offer during the active task unless the user explicitly reopens setup.

An onboarding offer is a blocking decision point for the pending documentation write. Ask a direct setup question, end the turn, and make no repository change until the user replies. Conditional wording is not an offer, silence is not a decline, and the task must not continue past the offer in the same turn.

Never install software, initialize a repository, or grant documentation consent from silence, a general request to use Gobb, or approval of one documentation edit. Existing repository instructions remain authoritative.

## Documentation workflow

Use `documentation.workflow` only when capability `documentation_workflow_approval_v1` is present. Without it, report that documentation approval cannot be verified and ignore any workflow/auto-log fields in that response. Keep the supported start, checkpoint, and finish behavior. Before writing documentation, require explicit authorization for that target and role under the rule below; otherwise ask and stop. Do not scan for instructions or claim persistent approval.

When documentation becomes relevant:

1. `present`: load the reported workflow with `--context-path`; load a present style guide only before a documentation write.
2. `unconfigured`: ask once in the active session whether to adopt Gobb's preset, register a custom workflow, or continue for now. A missing style guide produces the same optional Gobb recommendation only when documentation will be written.
3. `missing`: report the configured missing path and request its restoration or correction before governed documentation writes; do not substitute Gobb's preset.
4. `ambiguous`: name the candidates and ask which governs; do not load all.
5. `unsafe`: do not read the unsafe path. Stop documentation writes governed by that workflow, including writes to an otherwise safe target, and report the boundary that needs repair. A named target or routine approval does not override this safety finding.

After explicit user approval, use these visible commands:

```bash
gobb documentation adopt --preset gobb --no-input --yes
gobb documentation use <workflow-path> --style-guide <optional-style-path>
gobb documentation approve-auto-log --no-input --yes
gobb documentation revoke-auto-log
```

Never infer or edit approval state. Exact active-task authorization for an existing target and role permits only that named write without another prompt, even when `auto_log.state` is `required`, `stale`, or `unavailable`; a changed target or role still requires a focused prompt. Otherwise, `auto_log.state: approved` permits routine documentation writes in the active authorized task without another prompt, while `required`, `stale`, or `unavailable` requires a focused prompt naming the durable fact, target path, and document role. Independent authority, publication, policy, and safety gates always remain separate.

Identify the suitable owner through safe routing; verify write authority before changing it. Routing does not grant permission. A generic request to record a decision does not authorize an inferred target and role when approval is absent; ask a focused question naming them and stop. Existing exact-task authorization must be honored without asking again. Check required index authorization before a coupled document/index transition so a completed plan is not left with an active index.

Record material decisions, findings, corrections, and verification outcomes when they happen, and retain them in the smallest durable owner after completion; do not limit retention to facts needed by a future task. Evaluate documentation value after a plan or proposal is accepted or materially revised, a durable decision is made, a milestone completes, verification changes confidence, documented behavior changes, or work approaches handoff or context loss. Do not evaluate every message. Do not store greetings, repetition, unresolved brainstorming, obvious code facts, raw transcripts, chain-of-thought, terminal dumps, or secrets.

For a material defect correction, retain the observed cause, correction and verification result together. For a revised proposal, retain the earlier proposal as history with the revision reason and predecessor link. Preserve the target document's format and required header; proposing JSON product output does not convert its Markdown proposal into JSON.

Choose targets in this order: the existing subject owner, active plan, matching report or reference, local working state for temporary continuity, then one new indexed document only when no suitable file exists. Prefer the smallest accurate update.

Before each automatic write, refresh Gobb facts when the current result predates a repository change or user turn that could have changed the instructions. Update required indexes, rerun the relevant phase, and report changed documentation paths in the next concise update or final response.

Persistent routine approval never authorizes an authority transition, canonical product or architecture replacement, roadmap change, publication, public/private/local movement, secret capture, blocked-workflow override, or work outside the task. Request the specific decision when one applies. An explicit instruction not to log overrides approval immediately.

## Checkpoint

Before an intentional pause, handoff, provider switch, risky multi-stage change, or expected context loss, run:

```bash
gobb agent-context --if-managed --phase checkpoint --json
```

- If working state is unavailable, do not write it elsewhere; surface the finding and continue only when continuity remains safe.
- Before pausing, check whether the intent, decisions, progress, verification and next action are already recoverable without this conversation. A checkpoint command validates state; it does not save these facts. Preserve any missing continuity in one permitted working-state record. Do not create a duplicate when all five are already durable.
- Reuse an active file only when its intent clearly matches. Otherwise create one direct lowercase kebab-case `.md` child; append the smallest unused numeric suffix on collision.
- Follow the CLI-defined front matter, lifecycle values, and required headings. Never copy a transcript.
- Rerun checkpoint once after writing and resolve malformed, unsafe, or unknown entries before relying on it.

## Finish

Before the final response for a managed planning, proposal, implementation, verification, or other durable task, run:

```bash
gobb agent-context --if-managed --phase finish --json
```

Finish review never authorizes a documentation write. Before changing any document to resolve finish findings, require either explicit active-task approval for that exact target and role or `auto_log.state: approved`; otherwise ask and wait.

When the CLI reports `git_not_applicable`, do not claim Git-derived ignored status, a clean working tree, change coverage or history. Review the documentation impact of task-known changes and report the applicable disposition below; no Git result does not waive that review or grant write authority. Leave Git-dependent verification explicitly unavailable.

1. Resolve agent-actionable `documentation_review`, `working_state`, guard, and `completion` findings.
2. When `documentation_review.required` is true, choose exactly one allowed disposition:
   - `updated`: update the suitable existing document and every required index.
   - `created`: only when no suitable document can preserve durable information; create the smallest document and index it.
   - `proposed`: prepare a reviewable authority or publication change without promoting it.
   - `no_impact`: no durable documentation change is warranted.
   Report the disposition in the final response; the Phase 2.7 CLI does not accept or store it.
3. Use `proposed` for an authority or publication proposal even when editing an existing proposal file. For routine factual maintenance, prefer `updated` over `created`.
4. After any documentation or working-state change, rerun finish.
5. Claim Gobb completion validation only when the latest result is structurally ready, the guard is not blocked, and approval has not been implied or bypassed. Structural readiness does not establish correct task meaning, factual content, format or history; self-review those actual artifacts before claiming the task complete. Otherwise report the unresolved blocker.

Honor `next_actions` and `approval_required`. Never promote working state, change authority, publish, or override a boundary without explicit approval.

Do not infer context selection, freshness, integrity, lineage, or policy rules. Those belong to the Gobb CLI contract.
