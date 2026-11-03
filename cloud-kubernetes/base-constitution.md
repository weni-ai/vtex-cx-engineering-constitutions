# Cloud Kubernetes Base Constitution

Kubernetes engineering principles that specialize the root constitution for
repositories that declare cluster workloads and reconcile them from Git. These
principles MUST NOT contradict the root; they add domain-specific rules.
Principles are declarative and testable, stated with `MUST` / `SHOULD` and an
explicit rationale. Cluster names, controllers, and repository paths belong to
the project layer, not here.

## Core Principles

### Declared State Is the Cluster
The Git repository MUST be the only source of truth for workloads in this
domain. A GitOps controller MUST reconcile the cluster from that repository. A
change applied out of band — with the cluster CLI, a dashboard, or a local
apply of rendered manifests — MUST be treated as drift: it MUST be reverted or
brought back into Git. Production MUST NOT delete or self-heal live resources
on its own unless the engineering spec explicitly allows that automation; a
human MUST approve what production reconciles. Any operation against a cluster
MUST name that cluster. Kubeconfigs and rendered output MUST NOT be committed.

Rationale: a change applied by hand never passed review, and the next
reconciliation overwrites it without a record. Naming the cluster is what
keeps a command meant for one environment off another. A human gate on
production is what makes the Git review the change that actually ships.

### Environment Specializes a Shared Base
A workload MUST be declared once, in a shared base, and specialized per
environment by a thin overlay. The environment MUST NOT be the parent of the
application in the repository layout, and the base MUST NOT be treated as an
environment. Two environments MUST NOT share a namespace. A new workload MUST
follow the repository's canonical template rather than invent a layout.

Rationale: one definition plus a thin overlay is what makes an environment
difference readable as a difference, instead of as a second copy of the
workload. A shared namespace removes the boundary that keeps one environment's
failure and credentials off the other. The template exists so that boundary is
not redesigned in every application.

### The Render Is the Change
A change MUST be accepted or rejected on the fully rendered manifest, not on
the unrendered source. Values that differ by environment MUST be overlays on
the shared base. Values injected by the GitOps controller MUST use that
controller's substitution mechanism. A third-party chart MUST be pinned to an
immutable version; a floating tag MUST NOT be used. The rendered manifest MUST
NOT contain secret data or an unresolved placeholder.

When a chart is added or its version changes, the render MUST be inspected
before it is merged. It MUST be rejected, unless the engineering spec records
an exception, when the render widens privilege beyond the workload: a root or
privileged container, host access, cluster-admin rights, a hook that executes
a downloaded script, an image from an unapproved registry, or a network policy
that allows all traffic.

Rationale: the source is not what the cluster runs. Two builds of an unpinned
chart can install different code from the same commit, so the review never
saw the change that shipped. Privilege added by a chart is invisible until
the render is read, which is the last point at which it can still be refused.

### Workloads Are Identifiable
Every workload MUST carry `app.kubernetes.io/name`, `app.kubernetes.io/part-of`,
`app.kubernetes.io/component`, and `tier` set to `backend` or `frontend`. The
environment overlay MUST set `track` to that environment, and `track` MUST NOT
be part of a selector. The annotations `weni.ai/owner` and `weni.ai/source`
MUST name the owning team and the canonical Git source. Placeholder values
MUST NOT ship.

`app.kubernetes.io/component` MUST be the selector shared by the pod, its
Service, its disruption budget, and its network policy. Identity labels placed
on a third-party chart MUST NOT rewrite that chart's selectors. A selector
MUST NOT name a label the pod does not have.

Rationale: these keys are how ownership, environment, and blast radius are
queried without opening every manifest. A selector the pod does not carry, or
a chart selector that was rewritten, drops traffic while the objects still
look present. Keeping `track` off the selector stops an environment overlay
from retargeting a Service.

### Least Privilege Runtime
Every pod MUST run as non-root. User, group, and filesystem group MUST be
`1999`, or the non-root identity the image documents, and the image MUST
already run as that user. The pod MUST drop all capabilities, forbid privilege
escalation, apply the runtime's default seccomp profile, and use a read-only
root filesystem, writing only on a volume declared for that purpose. It MUST
listen on a port above 1024. User id `0`, host namespaces, and host paths MUST
NOT be used unless the engineering spec records the exception. A workload that
cannot meet this baseline MUST NOT be reconciled while it runs as root or
privileged.

Rationale: root, a writable root filesystem, and extra capabilities turn a
bug inside the container into control of the node. Uid `1999` is the
organization's non-root identity, so the image and the volume agree. A port
below 1024 exists only to require a capability that the rest of this rule
removes. Dropping privileges inside an entrypoint still starts the container
as root, which this rule is there to reject.

### Networks Deny by Default
Every workload MUST declare a network policy that selects its own pods and
covers both ingress and egress. Ingress MUST allow only the ports the Service
and its probes use, and only from the peers that call the workload. Egress
MUST allow only declared dependencies, plus name resolution. A policy that
selects every pod, or that allows every port or every peer, MUST NOT be
merged.

Rationale: with no policy, every pod in the cluster can reach every other
pod. A policy that allows all traffic documents an intention and enforces
nothing. Binding the policy to the ports the Service actually publishes makes
it checkable against the render.

### Credentials Stay Outside, Callers Are Named
Secret values MUST NOT appear in this repository. A workload MUST read
credentials from a secret that already exists in the cluster. Configuration
that is not secret MUST be declared apart from those credentials, with values
that differ by environment expressed as overlays.

A workload that calls cloud APIs MUST assume a workload identity bound to its
service account. Long-lived access keys MUST NOT be injected. The permissions
on that identity are provisioned with the account infrastructure, not in this
repository.

A user-facing workload MUST authenticate with OIDC against
`https://accounts.weni.ai/auth/realms/weni` and MUST allow only an explicit
list of groups or roles. When the workload cannot speak OIDC, the platform's
authenticating proxy MUST be its only public entry. Public HTTP MUST redirect
to HTTPS. A workload that is not public MUST NOT be exposed to the internet.

Rationale: a secret committed to Git stays in history after it is rotated.
Workload identity keeps cloud authority on the service account, where it can
be reviewed, instead of on a key copied into the environment. An explicit
allow-list and a single public entry are what keep an internal workload from
answering anonymously on the internet.

### Stop Cleanly Under Load
Every long-running workload MUST define startup, liveness, and readiness
probes. An HTTP service this organization builds MUST expose `/healthcheck`
and MUST NOT return secrets from it. Probes and the public health check MUST
use the same path. On termination the process MUST stop accepting new work and
drain in-flight requests. The termination grace period MUST NOT exceed 120
seconds unless the engineering spec records an exception.

Every container MUST declare CPU and memory requests and limits. Horizontal
scale MUST be owned by a single scaler. Its minimum, maximum, and fallback
MUST be set per environment, and a replica count that fights the scaler MUST
NOT be set beside it. A customer-facing production workload SHOULD run at
least two replicas. When the minimum is greater than one, a disruption budget
MUST still allow one voluntary eviction.

Rationale: probes and a bounded drain are how a rolling update and a node
removal avoid dropping traffic; the platform can only guarantee about two
minutes of grace. Two scalers fight over the same replica count, so the
reviewed minimum is not the count that runs. Requests and a disruption budget
turn eviction from a best effort into a limit that can be checked.
