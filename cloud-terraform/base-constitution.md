# Cloud Terraform Base Constitution

Terraform engineering principles that specialize the cloud constitution for
infrastructure repositories that provision cloud resources with Terraform (or
OpenTofu). These principles MUST NOT contradict the root or cloud base; they
add Terraform-specific rules. Principles are declarative and testable, stated
with `MUST` / `SHOULD` and an explicit rationale. Account IDs, workspace
names, and repository paths belong to the project layer, not here.

## Core Principles

### Config Outside HCL
Environment-specific values MUST live in the repository's workspace config
file, not hardcoded in `.tf` files. Workspaces MUST declare account, role,
environment, and region. Shared defaults MUST live in a common section.
Terraform code MUST read those values through locals decoded from that file
and MUST treat optional keys as optional. Changing an attribute that varies by
environment MUST be done in the config file unless the change is structural.

Rationale: operators change config far more often than module wiring. Keeping
tunables outside HCL makes plan diffs reviewable as intended environment
changes instead of code churn.

### Default Region with Per-Resource Override
Resources MUST be created in the workspace default region unless the resource
entry in the config file sets an explicit region. When a resource overrides
the region, it MUST select the matching aliased provider rather than changing
the workspace default. Adding a new region override MUST also ensure a
provider instance exists for that region.

Rationale: most resources belong with the workspace; forced multi-region
defaults multiply blast radius. A per-resource override covers legitimate
exceptions without forking the workspace or duplicating state.

### File Layout by Concern
Terraform files MUST be organized by concern. One primary resource type or
module family MUST live per file, named after that resource or module.
Shared locals MUST live in a locals file, outputs in an outputs file, and
data sources in a data file. Backend and provider bootstrap MUST stay in the
template's established files. Unrelated resource types MUST NOT share a file.

Rationale: one resource family per file keeps reviews focused and ownership
obvious. Separating locals, data, and outputs prevents dump files that hide
side effects.

### Prefer Maintained Registry Modules
Shared modules from the team's preferred public registry namespace MUST be
preferred over raw `resource` blocks when a maintained module covers the need.
Module sources MUST be pinned to an immutable version constraint. A raw
resource MUST be justified in the engineering spec when no suitable module
exists. Project-local modules MAY wrap a registry module to encode org
defaults; they MUST NOT reimplement what the registry module already provides.

Rationale: maintained modules concentrate reviewed defaults for IAM,
networking, logging, and encryption. Pinning versions keeps two applies of
the same commit reproducible.

### Mandatory Resource Tags
Every managed resource MUST receive tags, merged so entry-level tags from the
config file compose with repository defaults. At minimum every resource MUST
carry a human-readable name, owning team, service or resource family, a
marker that Terraform manages it, the canonical source URL of this repository,
and a creation timestamp that is set once and ignored on later applies so
plans stay stable. Empty or missing required tags MUST NOT pass review.

Rationale: tags are how ownership, cost, and blast radius are queried without
reading every module. Stable creation metadata plus management and source
markers make console drift and orphaned resources detectable.

### Workspace Isolation and State Key
Each Terraform workspace MUST map to exactly one environment and region
combination declared in the config file. The remote state key MUST be unique
to the repository or clearly bounded domain and MUST NOT collide with another
infrastructure repository's key.

Rationale: colliding state keys silently overwrite another team's
infrastructure history. One workspace per environment and region keeps plans
scoped to the blast radius the reviewer expects.
