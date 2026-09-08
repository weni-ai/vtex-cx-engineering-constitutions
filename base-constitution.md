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
Every engineering spec MUST derive from an approved product spec and MUST link
back to it through a stable reference (ID or URL). The product spec MUST exist
before its engineering spec is created. A technical architecture document SHOULD
be produced for non-trivial features; when it exists it MUST be linked from the
engineering spec, but its absence MUST NOT block the engineering spec.

Rationale: traceability from product intent to technical execution keeps
decisions auditable and lets any change be traced back to the need that
justified it. Making the product spec mandatory prevents engineering work
without an agreed problem; keeping the architecture doc optional avoids blocking
delivery on ceremony when the design is trivial.
