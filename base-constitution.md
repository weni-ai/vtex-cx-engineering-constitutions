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
identifiers.

Rationale: structured, privacy-safe telemetry is what makes incidents
diagnosable without creating new data-exposure risks.

### Versioned Contracts
Any change to a public interface MUST be versioned following SemVer. Changes MUST
be backward compatible or ship with an announced deprecation path. Silent
breaking changes MUST NOT be introduced.

Rationale: consumers depend on stable contracts; explicit versioning and
deprecation give them a predictable path to adapt without outages.

### Specification Traceability
Every engineering spec MUST derive from exactly one approved product spec and
MUST reference it through an immutable, pinned version (commit or tag) — a
mutable URL or ID alone MUST NOT be used. The product spec MUST exist and be
tagged before its engineering spec is created. An engineering spec MUST NOT
redefine the "what" it inherits: problem, scope, success criteria, and binding
decisions belong to the product spec. A technical architecture document SHOULD
be produced for non-trivial features; when it exists it MUST be linked from the
engineering spec, also pinned by commit/tag, but its absence MUST NOT block the
engineering spec.

Every engineering spec MUST open with an inheritance section in exactly this
format:

```
## Inheritance from Product Spec
- Product Spec: <title> — <URL>
- Pinned version: <commit/tag>
- Architecture doc: <none | URL + commit/tag>
- Inherited binding decisions: <short list>
- Scope of this spec: <slice implemented by this repo>
- Divergences: <none | link to amendment>
```

Rationale: traceability from product intent to technical execution keeps
decisions auditable and lets any change be traced back to the need that
justified it. Pinning the version is what guarantees that every team implements
the same version of the feature instead of divergent readings of a spec that
changed mid-flight. Making the product spec mandatory prevents engineering work
without an agreed problem; keeping the architecture doc optional avoids blocking
delivery on ceremony when the design is trivial. Enforcing a single inheritance
format keeps the link machine-checkable and uniform across every repository.

### No Silent Divergence
When a technical need contradicts something inherited from the product spec —
scope, success criteria, or a binding decision — the divergence MUST NOT be
implemented silently in code. It MUST be raised as an amendment in the product
repository and recorded in the `Divergences` field of the engineering spec's
inheritance section, linking to that amendment. Once the amendment is approved
and produces a new tag, the engineering spec's `Pinned version` MUST be updated
to it. A technical difference that contradicts nothing inherited is not a
divergence but an implementation decision, and MUST live in the engineering spec.

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
