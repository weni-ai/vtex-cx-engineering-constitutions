# Core Adversarial Review Lens (All Domains)

Operationalizes `base-constitution.md` against the **actual git diff**. This lens defines **no standalone rules**: rows say where to look and how to grade, while the requirement itself is always the cited principle's text in `.specify/memory/constitution.md`. Every finding honours any exception documented in `spec.md` (`## Constitution Alignment`).

---

## 1. Diff Containment, Divergence & Rollout Audit

| Governing Principle | How to Audit the Diff | Severity |
|---------------------|-----------------------|----------|
| `Contained Changes` | Diff `GIT.code_changed_files` against the touch-points in `spec.md`, `plan.md`, and `tasks.md`. Flag drive-by refactors, renames, formatting churn, or unrequested edits. | `MEDIUM` (`HIGH` if runtime behavior changes) |
| `No Silent Divergence` | When `spec.md` pins a Product Spec, verify code does not contradict or work around an inherited binding decision, scope boundary, or success criterion without a linked amendment. | `CRITICAL` |
| `Specification Traceability` | Verify rollout/rollback guards, feature flags, and backward-compatibility obligations declared in `spec.md` / `plan.md` exist in code. | `HIGH` |

## 2. Public Contracts, Secrets & Telemetry Audit

| Governing Principle | How to Audit the Diff | Severity |
|---------------------|-----------------------|----------|
| `Versioned Contracts` | Compare every changed public surface (HTTP routes/schemas, events, task signatures, exported UI props/types, host messages, shared IaC module inputs/outputs) against `spec.md` (`## Contracts`). Flag unversioned or silent breaking changes. | `CRITICAL` |
| `Changelog Maintenance` | When the repository falls within the principle's scope, check the changelog file and version metadata for every user-facing change in the diff. | `HIGH` |
| `Security and Secrets` | Scan code, configs, fixtures, `.env*`, and manifests in the diff for credentials and keys (`CRITICAL`), and check the source and vulnerability status of newly added dependencies (`HIGH`). | `CRITICAL` / `HIGH` |
| `Observability` | Check new/modified logs and error paths for what they record (`CRITICAL` for secrets or personal data), how trace or correlation identifiers propagate (`HIGH`), and catch blocks that drop the failure (`HIGH`). | `CRITICAL` / `HIGH` |

## 3. Diff Heuristics for `Proportional Design` & `Code Clarity and Language`

The module's established architecture and constitution-mandated layers are **never** over-engineering. Flag only complexity added *beyond* them (`MEDIUM`):

- **Speculative indirection (`Proportional Design`)**: single-implementation interfaces, base classes, factories, strategies, or registries with no second consumer in `spec.md`; pass-through wrappers that add neither error translation nor contract adaptation; parameters/flags every caller leaves at default; generalizing for *N* providers when `spec.md` scopes one; redundant downstream checks repeating static types or upstream boundary validation.
- **Clarity smells (`Code Clarity and Language`)**: the language of identifiers, comments, and docs; comments that narrate the code instead of explaining a constraint; dead branches; commented-out blocks.

## 4. Flow Integrity Procedure — FIIR

Auditing procedure for `No Silent Divergence`, `Proportional Design`, and domain auth/state principles whenever the diff modifies a conditional branch, filter, state transition, config switch, or event/webhook/integration handler:

1. **Trace**: `trigger → boundary validation / gate → handler → persisted state / outward effect`.
2. **Invariants**: note what must hold before and after each step, and where it is enforced vs merely assumed.
3. **Branch isolation**: inspect each branch on its own — widening one condition or filter must not bypass an adjacent auth, scope, loading, or error guard.
4. **Consumer parity**: confirm emitted states, event names, and payload shapes still match downstream consumers.

## 5. Diff Heuristics for `Verification Integrity`

Inspect new and modified tests alongside the production diff:

- **Tautological mocks**: check whether a test mocks/stubs the permission class, route guard, ORM/query scope filter, adapter, or state handler it claims to prove (`CRITICAL` on auth/isolation surfaces; `HIGH` on functional flows).
- **Shallow assertions**: treat tests that stay green when the guarded behavior is deleted (e.g. asserting only `status == 200` or "renders without crashing", or omitting refusal/unchanged-state assertions on rejected writes) as missing coverage (`HIGH`, or `CRITICAL` on security/isolation).
- **Unisolated boundaries**: check which suite each new test belongs to and whether it reaches live external HTTP, brokers, cloud APIs, or shared non-test caches/databases instead of the seam declared in `spec.md`; grade against the suite categories and exemptions the principle defines (`HIGH`, or `CRITICAL` when production resources are targeted).
- **Silenced gates**: check `# pragma: no cover`, `# noqa`, `eslint-disable`, `@ts-ignore`, and scanner ignores added in the diff for the justification the principle requires (`MEDIUM` / `HIGH`).
