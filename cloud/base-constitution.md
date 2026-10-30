# Cloud Base Constitution

Cloud engineering principles that specialize the root constitution for
infrastructure-as-code projects. These principles MUST NOT contradict the root;
they add domain-specific rules. Principles are declarative and testable, stated
with `MUST` / `SHOULD` and an explicit rationale. Cloud provider, pipeline
product, secrets product, and repository paths belong to the project layer, not
here.

## Core Principles

### Spec Before Infrastructure
No infrastructure change MUST begin without an engineering spec that follows the
root specification-traceability rules, or without a golden-path agent run that
takes that spec and this constitution as context. Hand-written infrastructure
code submitted without a linked spec MUST NOT be accepted in a pull request.
Manual edits after the agent generates code are allowed and MUST be called out
in the pull request.

Rationale: infrastructure changes are hard to reverse and easy to make without
recording why. Forcing a spec (or a traced agent run) before code keeps every
apply auditable from intent to resources, and keeps agents from inventing scope
the team never agreed to.

### Repository as Source of Truth
Declared infrastructure in the repository is the only source of truth for
managed resources. A change made in the cloud console, CLI, or any other
out-of-band path MUST be treated as drift: it MUST be reverted or imported into
code. What is not in the repository MUST NOT be considered intentional state.

Rationale: console edits create environments nobody can reproduce, review, or
roll back. Treating them as drift keeps the declared configuration authoritative
instead of letting live infrastructure silently diverge from the code reviewers
approved.

### Pipeline-Only Apply
`terraform apply` and equivalent apply or destroy operations against shared
environments MUST run only through the project's approved pipeline. Engineers
MUST NOT apply or destroy from a personal machine against staging or production.
Flags that bypass review or safety — including targeted applies and
auto-approve outside the pipeline or an declared break-glass path — MUST NOT be
used.

Rationale: local applies skip the plan review, the audit trail, and the same
credentials and policies every other change uses. Pipeline-only apply is what
makes the review of the plan meaningful instead of optional.

### Reviewed Plan Before Apply
Every apply MUST be preceded by a plan attached to the pull request and approved
by at least one human other than the author. The reviewer MUST confirm that the
plan matches the linked spec. An unexpected destroy or replace MUST block merge
until the spec is updated or the plan is corrected. Merging without an approved
plan, or with a plan that no longer matches the spec, MUST NOT occur.

Rationale: the diff of HCL is not the change that will hit production — the plan
is. Reviewing the plan against the spec is the last chance to catch destructive
or out-of-scope actions before they execute.

### Module Reuse Over Raw Resources
Shared modules from the team's internal registry MUST be preferred over raw
`resource` blocks. Introducing a raw resource MUST be justified in the
engineering spec. Modules and providers MUST be pinned to an immutable version
(tag or exact version constraint). References to a mutable branch such as
`main` MUST NOT be used. The Terraform `required_version`, every
`required_providers` entry, and the dependency lock file MUST be committed and
kept current.

Rationale: versioned modules concentrate reviewed defaults for networking,
identity, and data protection. Unpinned modules and providers make two applies
of the same commit able to pull different code, which destroys reproducibility.

### Small Reversible Changes
Each pull request MUST serve a single stated purpose. The engineering spec MUST
describe how to roll the change back. Unrelated refactors, renames, or
reformatting MUST NOT ride along with an infrastructure change.

Rationale: a multi-purpose infrastructure PR hides risk inside noise. Small,
reversible units keep review honest and make an incident response a revert
instead of a reconstruction.

### Secrets Outside Code and State
Secrets MUST NOT appear in Terraform source, committed variable files, outputs,
or state in plaintext. Sensitive variable values MUST be marked `sensitive`.
Secrets MUST be read at apply time from the project's external secrets manager.
State MUST live in a remote backend with locking and encryption enabled. There
MUST be one state per environment and domain boundary. State MUST NOT be edited
by hand. Resource adoption and refactoring MUST use `import` and `moved` blocks
in code rather than manual state CLI operations.

Rationale: Terraform state and variable files are common leak paths. Keeping
secrets out of them, and keeping state remote, locked, and encrypted, is what
makes collaboration on infrastructure safe. Codified import and move operations
keep history reviewable the same way as any other change.

### Declared Environments and Metadata
Environments MUST be separated so that they differ by variables and inputs, not
by duplicated logic. Resource names MUST follow the project's documented naming
convention (lowercase, hyphen-separated identifiers that encode ownership,
service, environment, and resource role). Every managed resource MUST carry the
tags required by the project for ownership, team, service, environment, cost
allocation, Terraform management, and the originating spec identifier. Every
variable and output MUST declare `type` and `description`. Outputs MUST NOT
expose secrets. Stateful resources that hold data in production MUST enable
destruction protection.

Rationale: identical logic across environments prevents "works in staging only"
drift. Consistent naming and mandatory tags are what make cost, ownership, and
incident response queryable without reading every module. Destruction protection
on data stores turns a mistaken destroy into a blocked plan instead of data
loss.

### Validated Before Merge
Before merge, every change MUST pass formatting, configuration validation,
linting, and the project's security scanner in CI. Findings MUST NOT be silenced
without a justification recorded in the engineering spec. Local pre-checks of
the same gates SHOULD be run before opening the pull request.

Rationale: formatting and validation failures are cheap in CI and expensive
after apply. Security scanners catch common misconfigurations before a reviewer
has to spot them by eye; requiring a recorded exception stops "disable to green"
from becoming the default.

### Human Accountability for Agents
An agent MAY draft infrastructure code and pull request text. An agent MUST NOT
merge a pull request or trigger an apply without explicit human approval. Final
responsibility for merge and apply MUST rest with a named cloud engineer.

Rationale: agents accelerate drafting; they do not absorb operational
accountability. A named human owner is what keeps merge and apply decisions
inside the same review and incident model the team already trusts.

### Break-Glass with Retroactive Codification
During an active incident, the mandatory change flow MAY be shortened to restore
service. The break-glass action MUST be declared in the incident channel with
who is acting and what will change. The minimum change required MAY run through
an emergency pipeline or, when that is impossible, the console. Within 24 hours
the actor MUST open a retroactive engineering spec and a pull request that
reflects the live change in code, confirm with a clean plan that no drift
remains, and record the break-glass in the incident post-mortem.

Rationale: incidents need speed, but undocumented emergency changes become
permanent mystery infrastructure. The 24-hour codification window restores the
repository as source of truth without blocking the restore itself.
