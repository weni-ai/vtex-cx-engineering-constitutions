# Backend Base Constitution

Backend engineering principles that specialize the root constitution for
server-side projects. These principles MUST NOT contradict the root; they add
domain-specific rules. Principles are declarative and testable, stated with
`MUST` / `SHOULD` and an explicit rationale. Stack, tooling, and paths belong to
the project layer, not here — except when a specific class, function, or
configuration is prohibited for security reasons, in which case it MAY be named.

## Core Principles

### Never Trust the Client
Everything that reaches the server from outside — a mobile app, a web page, a
third-party webhook, a queue message, or another API — MUST be treated as
potentially malicious, incomplete, or incorrect until it is rigorously
validated. Every external input MUST be validated for type, format, range, and
business rules at the server boundary before use, and MUST NOT be interpolated
directly into queries, commands, templates, file paths, or unvalidated outbound
URLs. Inbound webhooks, callbacks, and tokens MUST be verified for authenticity,
expiry, and replay protection before any side effect, using server-fixed
algorithms and constant-time secret comparison. Authorization MUST be enforced
on the server for every request, regardless of any check already performed by
the client.

Rationale: clients and external producers run outside the server's control and
can be inspected, modified, replayed, or bypassed. Validating inputs,
parameterizing queries and outbound targets, and verifying cryptographic
authenticity before side effects prevent injection, SSRF, replay, and
privilege-escalation attacks that client-side checks can never stop.

### Explicit, Scoped Authorization
Every endpoint MUST declare an explicit permission that verifies the caller is
allowed to perform that action on that specific resource — identity alone MUST
NOT be treated as authorization. Access MUST be denied by default: an endpoint
that declares no permission, or declares an empty one, MUST be rejected rather
than left open. Endpoints MUST expose only the HTTP methods or actions required
by their contract; unintended verbs on shared handlers or viewsets MUST be
closed. In the rare case an endpoint must be reachable without an authenticated
user, it MUST use a permission dedicated to that endpoint, named for the reason
it is open and implementing the check that replaces user identity (such as a
webhook signature or an internal token), and the justification MUST be recorded
in the engineering spec.

Every read, write, and related-resource reference on a scoped entity MUST
enforce the caller's scope boundary in the data access layer; an omitted or
empty filter MUST NOT widen a query across scopes, and server-owned ownership or
role fields MUST NOT be writable from external input. Background workers and
queue consumers MUST re-verify scope and current state rather than trusting
message payloads blindly.

In Django REST Framework, `IsAuthenticated` and `AllowAny` MUST NOT be used under
any circumstance: not in `permission_classes`, not in the `@permission_classes`
decorator, not in `DEFAULT_PERMISSION_CLASSES`, not composed with other
permissions through `&` or `|`, and not as a base class. A custom permission
whose check unconditionally grants access is equivalent to `AllowAny` and is
equally forbidden. `DEFAULT_PERMISSION_CLASSES` MUST be set explicitly, because
when it is omitted the framework falls back to `AllowAny`.

Rationale: `IsAuthenticated` only proves that a caller has a valid session, not
that they may touch a given project or record, so it silently opens every
resource to any logged-in user of any tenant. `AllowAny` removes the check
entirely, and it is also what the framework applies when no default is
configured, so an omission becomes a public endpoint. Forbidding both by name
makes the rule mechanically checkable in review and CI, and forcing open
endpoints through a dedicated, named permission keeps every exception visible
and tied to the check that justifies it. Enforcing closed verbs, data-layer
scope predicates, related-record ownership checks, and worker re-verification
ensures tenant isolation holds across every entry point, not only at the route
decorator.

### Fail Gracefully and Predictably
Every external dependency will eventually fail: networks fluctuate, databases
reach connection limits, and third-party APIs go down without warning. Calls to
external dependencies MUST have explicit timeouts and MUST NOT block indefinitely.
Multi-step writes that must succeed or fail together MUST run atomically so a
partial failure cannot leave persisted state inconsistent or trigger premature
external side effects. Failures MUST be handled explicitly and surfaced as
consistent, well-defined error responses — never as unhandled crashes or leaked
internal details.

Rationale: failure is a certainty, not an edge case. Timeouts, atomic writes,
and predictable error boundaries keep partial outages contained and observable
instead of letting a failing dependency corrupt state, take down the system, or
expose internals to callers.

### Bounded Retry Over REST
When data is propagated between services over a REST call, a failure in that
call MUST be retried rather than dropped. A retry MUST be attempted only when
the failure could plausibly succeed on another attempt — a connection error, a
request timeout, an HTTP 5xx, or an HTTP 429 — and MUST NOT be attempted on a
4xx that reflects a defect in the request itself. A retry MUST only be applied
to an operation that is idempotent or protected by a deduplication key; when the
operation is neither, it MUST be made idempotent rather than left without retry.
Every retry policy MUST define a maximum number of attempts and a backoff
strategy; unbounded retry MUST NOT be used. When the attempts are exhausted, the
failure MUST be logged and MUST remain recoverable — it MUST NOT be silently
discarded.

Rationale: propagation between services fails for transient reasons far more
often than for permanent ones, so retrying is what keeps services converging
instead of drifting apart. But retry only helps when it can change the outcome:
resending a request the server rejected on its merits multiplies load on a
dependency that is already answering correctly, and retrying a non-idempotent
operation duplicates the effect instead of repairing it. Bounds are what keep the
mechanism from becoming the outage: unbounded retry amplifies load on a
dependency exactly when it is already degraded. Making the exhausted case
observable and recoverable is what prevents data from disappearing between two
services that each believe they succeeded.

### Scalability and Peak Load
Every service MUST be stateless so that it can scale horizontally: state that
outlives a single request MUST NOT be kept in process memory or on local disk,
and MUST live in an external store shared by all instances. The peak load a
service is expected to sustain MUST be declared in its engineering spec, stated
as peak and not as average.

Collection queries and list endpoints MUST be bounded through pagination or
explicit caps and indexed on hot scope and filter paths; N+1 query loops and
spawning OS processes inside request handlers MUST NOT be introduced.
Long-running bulk imports, synchronizations, or fan-out work SHOULD execute
asynchronously and idempotently rather than blocking request handling. Shared
cache keys for scoped data MUST include the scope identifier (and actor
identifier when actor-specific), define an explicit TTL, and be invalidated or
versioned by every write path that mutates the underlying data.

Rationale: capacity is a design input, not something to be discovered during an
incident. Sizing for average traffic guarantees failure precisely when demand
matters most, such as a seasonal sales peak. Statelessness is what makes adding
instances a valid answer to load at all — a service holding state locally can
only be restarted, not scaled out. Declaring the peak turns scalability from an
assumption into a number that can be reviewed and tested against. Bounded
queries, background offloading, and scope-isolated caches are what allow those
instances to sustain the declared peak without exhausting connections, leaking
cached data across tenants, or serving stale state.

### Backward-Compatible Data Evolution
Schema changes and data migrations MUST be committed with the code that requires
them and MUST remain backward-compatible with the currently deployed application
version so a rollout can be safely rolled back without data loss or downtime.
Destructive schema changes — such as dropping, renaming, or tightening a column
still read or written by live instances — MUST follow an expand-and-contract
sequence across separate deployments unless downtime is explicitly approved in
the engineering spec.

Rationale: application instances and database migrations rarely switch atomically
during deploys or rollbacks. Keeping every schema step compatible with the
previous running version ensures a bad release can be reverted immediately
without breaking production traffic.

### Diagnosable Errors
Every error reported to an error-tracking system MUST carry enough context to be
located and filtered without reproducing it: at minimum the project identifier,
the account identifier, the user identifier, and the correlation identifier of
the request. Those identifiers MUST be opaque. Sensitive personal data — names,
e-mail addresses, phone numbers, or government identifiers — MUST NOT be
attached to an error report under any circumstance.

Rationale: an error without identifying context can be counted but not
investigated; the team sees that something broke without being able to tell
whose data, which account, or which request it was. Opaque identifiers give
exactly the filtering an investigation needs while keeping the report free of
personal data, which is what the root observability principle requires.

### Tests Exercise Flows
Every flow MUST have at least one test covering the complete use case through
its real entry point, authorization, and persistence layer, from input to
resulting effect. Tests that assert a single method in isolation are allowed and
SHOULD be used to explore edge cases and input variations that are expensive to
reach through the whole flow — but they MUST NOT be the only coverage a flow
has. Every flow MUST cover its success path and its failure paths; whenever an
operation is restricted by role or resource scope, flow tests MUST also cover
refusal paths proving that unauthenticated, unauthorized, or cross-scope
requests are rejected and leave persisted state unchanged.

Rationale: a suite made only of isolated method tests can be green while the
composition of routing, permissions, and queries is broken. Exercising the real
entry point across happy, error, and refusal paths proves both functional
correctness and tenant isolation where bugs are most expensive in production.

### Explicit Over Clever
Hidden side effects and implicit control flow MUST NOT be introduced to save
lines. Any literal that carries domain or operational meaning — a threshold, a
limit, a timeout, a retry count — MUST be a named constant rather than an inline
value; literals that carry no meaning beyond their own value, such as an index
of `0` or an increment of `1`, are exempt.

Rationale: hidden side effects and unexplained magic numbers obscure operational
limits and safe ranges from reviewers, whereas explicit control flow and named
constants make behavior auditable at the call site.
