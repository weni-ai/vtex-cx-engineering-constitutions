# Engineering Base Constitution

Root engineering principles that apply to **every** VTEX CX project, regardless
of domain. Principles are declarative and testable, stated with `MUST` /
`SHOULD` and an explicit rationale. Stack, tooling, and paths belong to the
project layer, not here.

## Core Principles

### Version Control and Review
All code MUST enter the main branch through a pull request. A merge MUST require
at least one approved review and a green CI run. Direct pushes to the main branch
MUST be blocked via platform branch protection.

Rationale: the policy is only real when enforced by the platform, not by trust.
Peer review and a protected main branch keep history auditable and prevent
unreviewed changes from reaching production.


### Security and Secrets
Secrets MUST never be committed to the repository. Secrets MUST be provided by an
external secrets manager and injected at runtime. Access MUST follow least
privilege by default. Dependencies MUST come only from trusted sources and MUST
be checked for known vulnerabilities.

Rationale: leaked credentials and untrusted dependencies are among the most
common and most damaging breaches; prevention is far cheaper than remediation.

### Observability
Logs MUST be structured and MUST never contain secrets or sensitive personal
data. Errors MUST be traceable across components through correlation or trace
identifiers. Errors MUST NOT be silently swallowed; caught failures MUST either
be handled explicitly as part of expected control flow or recorded with
structured context.

Rationale: structured, privacy-safe telemetry is what makes incidents
diagnosable without creating new data-exposure risks, while forbidding silent
catch-all handlers prevents failures from disappearing without a trace.

### Code Clarity and Language
All code, identifiers, comments, and technical documentation MUST be written in
English; domain-specific terms or acronyms that only carry meaning in their
original language MAY remain untranslated. Code MUST prioritize clarity over
brevity or cleverness so that what happens is evident where it is written.
Comments MUST explain *why* a non-obvious decision was made — the constraint,
trade-off, or external quirk behind it — and MUST NOT restate *what* the code
already expresses; code that needs a comment to explain what it does SHOULD be
rewritten to say it directly. Dead branches and commented-out code MUST NOT be
committed.

Rationale: a shared language and self-explanatory code let any engineer across
teams read, review, and maintain a repository without hidden context. Comments
that capture reasoning preserve constraints the code cannot express on its own,
whereas narrative comments and dead code drift out of sync and mislead readers.

### Proportional Design
Every change MUST use the simplest design that satisfies the current
specification within the repository's established architecture. Abstractions,
indirection layers, extension points, or configuration flags MUST NOT be
introduced for hypothetical future needs when only a single concrete use case
exists, unless required by an architectural boundary of the project. Every
decision encoded in code or configuration — a business rule, a shared default,
an environment value — MUST have a single source of truth within a repository,
whereas incidental duplication MAY remain local when extracting it would create
premature coupling. Root causes MUST be fixed rather than masked with
workarounds, and redundant checks SHOULD NOT repeat invariants already enforced
by types, schemas, or an upstream boundary.

Rationale: speculative abstractions, pass-through wrappers, and redundant
defensive checks add cognitive and maintenance cost without solving a real
problem today. Giving every encoded decision a single source of truth prevents
behavioral and environment drift, while waiting for concrete use cases before
abstracting keeps coupling low.

### Contained Changes
A change MUST be limited to the context it was asked to address. Refactoring,
renaming, reformatting, or behavior adjustments outside that context MUST NOT
ride along; each belongs to its own change. This principle governs the scope of
a change as a whole; the requirement that each commit be atomic governs how that
change is divided internally, and a change that stays within scope MAY still
span several commits.

Rationale: a change that reaches beyond its stated scope is a change nobody
reviewed on purpose. It hides the intended fix inside unrelated edits, makes the
diff expensive to read, and turns a revert into a choice between losing the fix
and keeping an unrelated regression.

### Verification Integrity
Automated checks and tests MUST verify real behavior and MUST fail when the
behavior, contract, or guard they cover regresses. A test MUST NOT mock, stub,
or bypass the subject, permission, filter, or boundary contract it claims to
prove. Automated test suites that run on every change MUST be deterministic
and hermetic: external networks, third-party APIs, and shared infrastructure
outside the test harness MUST be stubbed or isolated at the boundary rather
than called live. Test suites that intentionally exercise real dependencies
(integration, end-to-end, contract) MAY reach them when they are labeled as
such, run in a dedicated stage separate from the per-change suite, and never
target production resources. Read-only validation that a domain requires
against live state, such as an infrastructure plan, is governed by that
domain's constitution and is not a test suite under this rule. Failing checks,
lint rules, type checks, or coverage gates MUST NOT be silenced or skipped
without an explicit justification.

Rationale: a green suite that mocks away the mechanism under test, passes
through regressions, or disables quality gates creates false confidence where
defects hide. Hermetic boundaries keep the per-change suite fast, reproducible,
and independent of external outages or shared state, while a separately labeled
integration stage still proves the real wiring that stubs cannot.

### Versioned Contracts
Any change to a public interface MUST be versioned following SemVer. Changes MUST
be backward compatible or ship with an announced deprecation path. Silent
breaking changes MUST NOT be introduced.

Rationale: consumers depend on stable contracts; explicit versioning and
deprecation give them a predictable path to adapt without outages.

### Specification Traceability
An engineering spec either derives from a product spec or originates in
engineering. Both are regular paths of the process; neither requires a
justification, and either may follow the full or the lite cycle.

When the change has a product spec, the engineering spec MUST derive from
exactly one approved product spec and MUST reference it through an immutable,
pinned version (commit or tag) — a mutable URL or ID alone MUST NOT be used.
The product spec MUST exist and be tagged before its engineering spec is
created. An engineering spec MUST NOT redefine the "what" it inherits: problem,
scope, success criteria, and binding decisions belong to the product spec. A
technical architecture document SHOULD be produced for non-trivial features;
when it exists it MUST be linked from the engineering spec, also pinned by
commit/tag, but its absence MUST NOT block the engineering spec.

An engineering spec derived from a product spec MUST open with an inheritance
section in exactly this format:

```
## Inheritance from Product Spec
- Product Spec: <title> — <URL>
- Pinned version: <commit/tag>
- Architecture doc: <none | URL + commit/tag>
- Inherited binding decisions: <short list>
- Scope of this spec: <slice implemented by this repo>
- Divergences: <none | link to amendment>
```

An engineering spec without a product spec states its own "what" and MUST open
with an origin section in exactly this format:

```
## Origin Without Product Spec
- Product Spec: none
- Problem: <what is wrong or missing, in one or two sentences>
- Acceptance criteria: <observable outcomes that prove the change is done>
```

Rationale: traceability from intent to technical execution keeps decisions
auditable and lets any change be traced back to the need that justified it.
When the change is born in product, the product spec is that origin, and
pinning its version guarantees that every team implements the same version of
the feature instead of divergent readings of a spec that changed mid-flight.
When the change is born in engineering — a hotfix, a fix, technical debt — the
engineering spec itself is the origin, and its problem and acceptance criteria
are what the change is verified against. Keeping the architecture doc optional
avoids blocking delivery on ceremony when the design is trivial. Enforcing a
fixed opening format for each path keeps the origin machine-checkable and
uniform across every repository.

### No Silent Divergence
When a technical need contradicts something inherited from the product spec —
scope, success criteria, or a binding decision — the divergence MUST NOT be
implemented silently in code. It MUST be raised as an amendment in the product
repository and recorded in the `Divergences` field of the engineering spec's
inheritance section, linking to that amendment. Once the amendment is approved
and produces a new tag, the engineering spec's `Pinned version` MUST be updated
to it. A technical difference that contradicts nothing inherited is not a
divergence but an implementation decision, and MUST live in the engineering spec.
This principle applies only to engineering specs derived from a product spec;
a spec without one inherits nothing it could diverge from.

Rationale: in a federated model where the product spec is the single source of
truth, a silent code deviation makes intent and implementation drift apart with
no audit trail. Forcing divergences through amendments keeps the spec
authoritative and every decision traceable back to an agreed change.

### Commit Messages
Commits MUST follow Conventional Commits format: `<type>: <description>`.
Allowed types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`. The
description MUST be imperative, specific, and no longer than 50 characters.
Commits MUST be atomic: one logical change per commit.

Rationale: conventional commits enable automated changelog generation and
semantic versioning. Atomic commits simplify bisecting, reverting, and reviewing.

### Changelog Maintenance
Public libraries MUST maintain a changelog following Keep a Changelog format.
Every user-facing change MUST appear in the changelog under the appropriate
category (Added, Changed, Deprecated, Removed, Fixed, Security). Version bumps
MUST follow SemVer.

Rationale: a well-maintained changelog communicates impact to consumers and
serves as release documentation. SemVer alignment ensures predictable upgrade
expectations.
