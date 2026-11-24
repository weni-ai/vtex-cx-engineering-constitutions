---
description: Audit the feature's git diff against the repository constitution and active domain lenses (core, backend, frontend), appending actionable remediation tasks to tasks.md.
handoffs:
  - label: Implement Review Remediation Tasks
    agent: speckit.implement
    prompt: Implement the review remediation tasks appended to tasks.md
    send: false
scripts:
  sh: scripts/bash/resolve-review-context.sh --json
  ps: scripts/powershell/resolve-review-context.ps1 -Json
  py: scripts/python/resolve_review_context.py --json
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). Supported optional hints in `$ARGUMENTS`:
- `base=<git-ref>` or `--base <git-ref>` — override the base branch used to compute the merge-base diff (forward it to `{SCRIPT}` as `--base <git-ref>` for the `sh` and `py` scripts, or `-Base <git-ref>` for the `ps` script).
- `--allow-open-tasks` — bypass the open-task gate in **report-only** mode (never writes to `tasks.md`).

## Pre-Execution Checks

**Check for extension hooks (before adversarial review)**:

- Check if `.specify/extensions.yml` exists in the project root.
- If it exists, read it and look for entries under the `hooks.before_vtex_cx_review_run` key.
- If the YAML cannot be parsed or is invalid, do not skip silently: tell the user that `.specify/extensions.yml` could not be read (include the parser error) and that no hooks were checked, including any mandatory (`optional: false`) hooks registered there, then continue normally.
- Filter out hooks where `enabled` is explicitly `false`. Treat hooks without an `enabled` field as enabled by default.
- For each remaining hook, do **not** attempt to interpret or evaluate hook `condition` expressions:
  - If the hook has no `condition` field, or it is null/empty, treat the hook as executable.
  - If the hook defines a non-empty `condition`, skip the hook and leave condition evaluation to the HookExecutor implementation.
- When constructing command invocations from hook command names, replace dots (`.`) with hyphens (`-`). For example, `speckit.git.commit` → `/speckit-git-commit`.
- For each executable hook, output the following based on its `optional` flag:
  - **Optional hook** (`optional: true`):

    ```text
    ## Extension Hooks

    **Optional Pre-Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```

  - **Mandatory hook** (`optional: false`):

    ```text
    ## Extension Hooks

    **Automatic Pre-Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}

    Wait for the result of the hook command before proceeding to the Goal.
    ```
    After emitting the block above you MUST actually invoke the hook and wait for it to finish before continuing. Run it the same way you would run the command yourself in this agent/session (the invocation may differ from the literal `{command}` id shown above, e.g. a skills-mode agent runs it as `/skill:speckit-...` or `$speckit-...`). Emitting the block alone does not run the hook.

- If no hooks are registered or `.specify/extensions.yml` does not exist, skip silently.

## Goal

Run an **adversarial engineering review** on the actual git change set of the active feature after implementation and convergence.

`__SPECKIT_COMMAND_CONVERGE__` answers *"Did we build everything `spec.md`, `plan.md`, and `tasks.md` asked for?"* without inspecting git. This command answers the complementary question — *"Is everything changed in git secure, isolated across scopes, resilient, performant under peak load, properly bounded, and proven by non-tautological flow tests?"* — by combining `.specify/memory/constitution.md` with `lenses/core.md` and the active domain lens(es).

## Operating Constraints

1. **READ-ONLY ON APPLICATION CODE AND ARTIFACTS (EXCEPT `tasks.md` APPEND)**:
   - **Never** create, edit, format, or delete application source files, tests, migrations, CI files, `CHANGELOG*`, `spec.md`, `plan.md`, or `.specify/memory/constitution.md`. Completing remediation tasks is the job of `__SPECKIT_COMMAND_IMPLEMENT__`.
   - **Never** run mutating git commands (`git add`, `git commit`, `git push`, `git reset`, `git checkout`, `git restore`, `git stash`, `git clean`, `git rebase`) or auto-fixing linters/formatters (`--fix`, `--write`).
2. **APPEND-ONLY ON `tasks.md` (SDD Full)**:
   - When `CYCLE == "full"` (`tasks.md` exists) and `--allow-open-tasks` was not passed, the command's **only** permitted write is appending a single `## Phase N: Review` section to the bottom of `tasks.md` when one or more actionable findings (`CRITICAL`, `HIGH`, `MEDIUM`) exist.
   - Never rewrite, renumber, reorder, check off, or delete existing tasks (including tasks from prior `Convergence` or `Review` phases).
   - When zero actionable findings exist, leave `tasks.md` **byte-for-byte unchanged** (no empty `## Phase N: Review` header).
   - `LOW` observations are reported in-session only and MUST NOT be appended to `tasks.md`.
3. **REPORT-ONLY IN SDD LITE**:
   - When `CYCLE == "lite"` (`spec.md` exists without `tasks.md`), do **not** create `tasks.md`. Emit the full review report in-session with concrete remediation instructions so the developer or agent can apply fixes and re-run this command until clean.
4. **CONSTITUTION AUTHORITY (NO SHADOW RULES)**:
   - `.specify/memory/constitution.md` is the **sole normative source of rules** (`root > domain > project`). Lenses (`lenses/*.md`) only provide diff-inspection heuristics, structured evidence tables, and severity grading over those principles — never standalone obligations. Lenses add depth, not coverage: every principle in the constitution is reviewed whether or not a lens row cites it. Every finding MUST trace to a named principle in `.specify/memory/constitution.md`, while respecting any explicit departure documented in `spec.md` under `## Constitution Alignment`.

## Execution Steps

### 1. Resolve Context & Enforce Gates

Run `{SCRIPT}` once from the repository root (appending `--base <ref>` for `sh`/`py` or `-Base <ref>` for `ps` if the user supplied a base branch in `$ARGUMENTS`) and parse the JSON payload:

- **Constitution gate**: If `CONSTITUTION_IS_TEMPLATE` is `true`, **STOP** immediately and instruct the user to generate the project constitution with the `setup-engineering` skill before running review.
- **Open-task gate (`CYCLE == "full"`)**: If `TASKS_STATE.open_count > 0` and `--allow-open-tasks` was **not** passed in `$ARGUMENTS`, **STOP** immediately without reading the diff or modifying `tasks.md`. Report the count and IDs (`TASKS_STATE.open_task_ids`) and instruct the user to complete them with `__SPECKIT_COMMAND_IMPLEMENT__` and verify completion with `__SPECKIT_COMMAND_CONVERGE__` before running `__SPECKIT_COMMAND_VTEX-CX-REVIEW_RUN__`.
- **Non-empty diff gate**: If both `GIT.code_changed_files` and `GIT.deleted_code_files` are empty, report that no code/configuration/test files outside `specs/` and `.specify/` have changed relative to `GIT.base_ref` and stop cleanly.

### 2. Load Governance & Select Active Lenses

1. Read `.specify/memory/constitution.md` in full.
2. Read `lenses/core.md` in full (always active).
3. Inspect `ACTIVE_DOMAINS` from `{SCRIPT}` and load every matching domain lens in full:
   - If `backend` is in `ACTIVE_DOMAINS` → read `lenses/backend.md`.
   - If `frontend` or `frontend-platform` is in `ACTIVE_DOMAINS` → read `lenses/frontend.md` (enable the `CX Platform (frontend-platform)` conditional block whenever `frontend-platform` is in `ACTIVE_DOMAINS`).
   - When `ACTIVE_DOMAINS` is empty, run with `lenses/core.md` only.
4. **Build the principle index**: list every normative principle in the constitution (each `###` heading whose body states `MUST` / `SHOULD` requirements), keyed by its name with any numbering prefix (`I.`, `1.`) removed and compared case-insensitively.
5. **Resolve lens rows against the index**: every lens row and procedure cites one or more principles by name.
   - Apply a row only for the cited principles present in the index.
   - When none of a row's cited principles is present (renamed, removed, or amended away in the project layer), **skip the row**: never enforce it from the lens text alone. In mandatory tables mark it `skipped — principle absent`, and record a `LOW` observation naming the row and the missing principle so the lens can be realigned.

### 3. Read Artifacts, Diff, Full Changed Files & Module Siblings

Never judge a diff from patch hunks alone:

1. Read `SPEC` (`spec.md`) — and `PLAN` (`plan.md`) + `TASKS` (`tasks.md`) when present — extracting:
   - Inherited binding decisions (or `Origin Without Product Spec` acceptance criteria),
   - `## Contracts`, `## Data Model and Migrations`, `## Non-Functional Requirements` (Peak Load, Observability, Failure Handling, Security and Authorization), `## Test Strategy` (`Stubbed at the boundary`), `## Rollout and Rollback`, and `## Constitution Alignment`.
2. Inspect the exact patch with `git diff <GIT.merge_base>` (when `merge_base` exists) plus `git diff` / `git diff --cached` for uncommitted changes.
3. Read **in full** every file in `GIT.code_changed_files` (existing/modified/untracked). Files in `GIT.deleted_code_files` no longer exist in the working tree: inspect them through the patch only, checking whether the removal drops a guard, permission, test, or contract still relied upon.
4. Read **1–3 sibling files** in each touched module/package to anchor local conventions: the actual ownership/scope field (`project`, `account`, `organization`, `store`, `tenant`), permission classes/decorators, service/adapter structure, state stores, and test base helpers. Never assume identifiers from another repository or framework.

### 4. Execute the Adversarial Passes

Evaluate the changed flows methodically across all active passes:

1. **Core Pass (`lenses/core.md`)**:
   - Audit, through the applied rows of `lenses/core.md`, unplanned diff files (`GIT.code_changed_files` vs `spec.md`/`plan.md`/`tasks.md`), silent divergences from inherited Product Spec decisions, SemVer/contract compatibility, secrets/dependency/PII hygiene, proportionality (anti-over-engineering), flow integrity (FIIR), and test authenticity.
   - **SDD Lite addition (`CYCLE == "lite"`)**: Because `__SPECKIT_COMMAND_CONVERGE__` does not run without `tasks.md`, explicitly verify that every acceptance/success criterion in `spec.md` is implemented and proven by a test.
2. **Domain Lens Pass(es) (`lenses/backend.md`, `lenses/frontend.md`)**:
   - Fill every mandatory table for the active lens(es) and execute every conditional check triggered by the diff.
   - Any row marked `n/a` MUST carry a 1-line evidence note naming what was inspected.
   - Judge each row against the cited principle's text in the constitution; the lens only says where to look and how to grade.
3. **Residual Principle Sweep**:
   - For every principle in the index that no applied lens row cited (including project-layer principles and principles added after the lenses were written), read its text and check the diff against each of its `MUST` / `SHOULD` requirements.
   - Grade findings with the impact scale in step 5.
   - Record each swept principle as `finding <ID>`, `clean`, or `no diff surface` with a 1-line note naming what was inspected.
4. **Read-Only Automated Verification**:
   - Discover the repository's configured checks (CI workflows, `Makefile`, `pyproject.toml`, `package.json`, `.pre-commit-config.yaml`) and run targeted, **read-only** verification on the changed paths:
     - Linter & formatter check (`--check` / read-only only),
     - Static typechecker (`mypy`, `pyright`, `tsc --noEmit`, `vue-tsc --noEmit`, `go vet`, `terraform validate`),
     - Targeted test suite covering the changed modules/flows,
     - Configured static security / dependency / secret scan on changed files when installed locally.
   - If a tool or runtime dependency (DB, container, cluster) is unavailable in the current environment, do **not** fail the command: record the exact unverified command in the report summary. If a check runs and fails, record a `HIGH` or `CRITICAL` finding.

### 5. Classify Findings & Severity

Deduplicate overlapping observations into concrete, self-contained findings, then grade each one with these rules, in order:

1. **Actionability comes from the modal verb.** A finding is actionable only when it violates a `MUST`, or an unjustified `SHOULD`, in `.specify/memory/constitution.md` that is not explicitly exempted in `spec.md` `## Constitution Alignment`. Every actionable finding is at least `MEDIUM`; an unjustified `SHOULD` violation is never graded above `MEDIUM`.
2. **Severity comes from impact, never from the modal verb.** "It is a `MUST`" alone never makes a finding `CRITICAL`.
3. **Lens tables are authoritative.** When an applied (not skipped) row in `lenses/core.md` or an active domain lens covers the finding, use the severity stated in that row (picking the higher value only when the row's escalation condition is met). Apply the impact scale below only to findings no lens row covers.

Impact scale:

- **`CRITICAL`** — exploitable, irreversible, or contract-breaking impact:
  - Security or isolation defect: missing/permissive auth or authz (including permission classes the constitution forbids), cross-scope/cross-tenant read/write/FK link, open extra HTTP verb, SQL/shell/template injection, SSRF, unsanitized DOM XSS sink, missing webhook signature/replay protection, worker trusting payload scope, token algorithm/expiry defect, or microfrontend escaping its DOM/global boundary.
  - Hardcoded/bundled secret, PII or secret in logs/error reports, silent Product Spec divergence, or unversioned breaking contract.
  - Scalability hazard: unbounded collection query, OS process spawned in a request, request-outliving in-memory/local-disk state on a stateless service, or shared cache key missing tenant/scope.
  - Missing security/refusal test for a changed access surface, or a tautological test that mocks the permission, scope filter, or boundary it claims to prove.
- **`HIGH`** — incorrect behavior in normal operation or broken verification:
  - Broken failure/async handling: outbound call without timeout, REST propagation retry policy that breaks `Bounded Retry Over REST`, swallowed exception, missing loading/error state, unguarded double-submit, stale async response race, optimistic update without rollback.
  - Missing flow test for a changed functional behavior, failing test/typecheck/lint check on changed files, N+1 query on a changed path, uncleaned mount listener/timer/observer, raw backend fields leaking past the adapter into stores/components, hardcoded user-facing UI strings, keyboard-inaccessible interactive element, or deprecated/duplicated Unnnic primitive or invented token.
  - Any other `MUST` violation whose effect changes runtime behavior.
- **`MEDIUM`** — maintainability, scope, or efficiency impact with no incorrect runtime behavior:
  - Unjustified `SHOULD` violation, speculative over-engineering inside the changed flow, uncontained drive-by refactor/edit in the git diff, clarity/naming/styling violations, or missing debounce/memoization on a frequent UI event.
- **`LOW` (Observation — report-only, never appended to `tasks.md`)** — not anchored in a constitution principle or outside the changed flow:
  - Pre-existing issues outside the changed flow, missing optional scan tooling in the repo, missing rate limiting on a public or expensive endpoint, or non-blocking DAST/pen-test recommendations when the diff introduces a new high-exposure surface (public/third-party endpoint, webhook/callback, service-to-service auth, file upload, external-driven outbound URL).

### 6. Present the In-Session Review Report

Output a concise report in the conversation's language (keeping code paths, principle names, and task descriptions in English). Omit domain subsections that are inactive:

```markdown
## Adversarial Review Summary

- **Cycle**: SDD Full | SDD Lite
- **Active lenses**: core + [backend | frontend | frontend-platform]
- **Scope reviewed**: `<branch>` vs `<base_ref>` (`<N>` code/test files)
- **Automated checks**: <ran & passed/failed, or skipped with reason>
- **Verdict**: PASSED | TASKS_APPENDED | CHANGES_REQUIRED (report-only)

## Findings

| ID | Severity | Domain | Source (Constitution / Lens) | Location | Problem & Remediation |
|----|----------|--------|------------------------------|----------|-----------------------|
| R1 | CRITICAL | backend | Constitution: Explicit, Scoped Authorization (`Lens[backend]: cross-scope-fk`) | `path/file.py:88` | `template_id` from request body is linked without scoping to `request.project`; filter lookup by `project=project` and add cross-scope refusal flow test |
```

Include the compact evidence tables mandated by the active domain lens(es) (**Threat Pass**, **Cross-Scope Pass**, and **Entry-Point Performance** for `backend`; **Client Trust**, **Async State & Boundaries**, and **Rendering/Bundle Performance** for `frontend`), followed by **Residual Principle Sweep** (one line per swept principle), **Flow & Security Test Audit**, and **Observations (`LOW`)** when present, including skipped lens rows.

### 7. Append Review Tasks to `tasks.md` (or Report Clean)

- **When `CYCLE == "lite"` or `--allow-open-tasks` was passed**:
  - Make **zero** file edits. If actionable findings (`CRITICAL`, `HIGH`, `MEDIUM`) exist, list them clearly as the remediation checklist and instruct the user to apply the fixes and re-run `__SPECKIT_COMMAND_VTEX-CX-REVIEW_RUN__`. If none exist, report **`✅ Review passed`**.

- **When `CYCLE == "full"` and one or more actionable findings (`CRITICAL`, `HIGH`, `MEDIUM`) exist** (`tasks_appended` outcome):
  1. Using `TASKS_STATE.max_task_id` (`M`) and `TASKS_STATE.next_phase_number` (`N`) from `{SCRIPT}` (confirming against the end of `tasks.md`), append a single new phase at the bottom of `tasks.md`:

     ```markdown
     ## Phase N: Review

     - [ ] T042 [CRITICAL] <imperative remediation + test requirement naming file path> per Constitution: <Principle Name> (review: <category>)
     ```

  2. Emit one task per actionable finding (combining a code fix and its proving test into a single atomic task when they close the same defect, or separate tasks when independent), ordered `CRITICAL` → `HIGH` → `MEDIUM`, with sequential IDs `T{M+1:03d}, T{M+2:03d}, …`.
  3. `<category>` is one of: `security`, `cross-scope`, `async-state`, `performance`, `contract`, `divergence`, `observability`, `ui-standards`, `over-engineering`, `containment`, `test-gap`, `verification`.
  4. Never modify any existing line of `tasks.md`.

- **When `CYCLE == "full"` and zero actionable findings exist** (`passed` outcome):
  - Leave `tasks.md` **byte-for-byte unchanged** (do not append an empty `## Phase N: Review` header).
  - Report: **`✅ Review passed — git diff satisfies the repository constitution and active domain lenses.`**

### 8. Next Actions (Handoff)

- On `tasks_appended`: state how many tasks were appended under `## Phase N: Review` and recommend running `__SPECKIT_COMMAND_IMPLEMENT__`, followed by `__SPECKIT_COMMAND_CONVERGE__` and `__SPECKIT_COMMAND_VTEX-CX-REVIEW_RUN__` until both report clean.
- On `passed`: recommend staging/committing the verified changes (following `Commit Messages` and `Changelog Maintenance` in `.specify/memory/constitution.md`) and opening the Pull Request.

## Mandatory Post-Execution Hooks

Check if `.specify/extensions.yml` exists in the project root:

- If it does not exist, or no hooks are registered under `hooks.after_vtex_cx_review_run`, finish cleanly.
- If it exists, read it and look for entries under the `hooks.after_vtex_cx_review_run` key.
- If the YAML cannot be parsed or is invalid, do not skip silently: tell the user that `.specify/extensions.yml` could not be read (include the parser error) and that no hooks were checked, including any mandatory (`optional: false`) hooks registered there, then finish cleanly.
- Filter out hooks where `enabled` is explicitly `false`. Treat hooks without an `enabled` field as enabled by default.
- For each remaining hook, do **not** attempt to interpret or evaluate hook `condition` expressions:
  - If the hook has no `condition` field, or it is null/empty, treat the hook as executable.
  - If the hook defines a non-empty `condition`, skip the hook and leave condition evaluation to the HookExecutor implementation.
- When constructing command invocations from hook command names, replace dots (`.`) with hyphens (`-`).
- For each executable hook, output the following based on its `optional` flag:
  - **Optional hook** (`optional: true`):

    ```text
    ## Extension Hooks

    **Optional Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```

  - **Mandatory hook** (`optional: false`):

    ```text
    ## Extension Hooks

    **Automatic Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}
    ```
    After emitting the block above you MUST actually invoke the hook and wait for it to finish before ending your turn.
