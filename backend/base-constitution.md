# Backend Base Constitution

Backend engineering principles that specialize the root constitution for
server-side projects. These principles MUST NOT contradict the root; they add
domain-specific rules. Principles are declarative and testable, stated with
`MUST` / `SHOULD` and an explicit rationale. Stack, tooling, and paths belong to
the project layer, not here.

## Core Principles

### Never Trust the Client
Everything that reaches the server from outside — a mobile app, a web page, a
third-party webhook, or another API — MUST be treated as potentially malicious,
incomplete, or incorrect until it is rigorously validated. Every external input
MUST be validated for type, format, range, and business rules at the server
boundary before use. Authorization MUST be enforced on the server for every
request, regardless of any check already performed by the client.

Rationale: clients run outside the server's control and can be inspected,
modified, or bypassed. Treating external input as untrusted until validated is
what prevents injection, data corruption, and privilege-escalation attacks that
client-side checks alone can never stop.

### Fail Gracefully and Predictably
Every external dependency will eventually fail: networks fluctuate, databases
reach connection limits, and third-party APIs go down without warning. Calls to
external dependencies MUST have explicit timeouts and MUST NOT block indefinitely.
Failures MUST be handled explicitly and surfaced as consistent, well-defined error
responses — never as unhandled crashes or leaked internal details.

Rationale: failure is a certainty, not an edge case. Handling it explicitly and
predictably keeps partial outages contained and observable instead of letting one
failing dependency take down the whole system or expose internals to callers.

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

Rationale: capacity is a design input, not something to be discovered during an
incident. Sizing for average traffic guarantees failure precisely when demand
matters most, such as a seasonal sales peak. Statelessness is what makes adding
instances a valid answer to load at all — a service holding state locally can
only be restarted, not scaled out. Declaring the peak turns scalability from an
assumption into a number that can be reviewed and tested against.

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
Every flow MUST have at least one test covering the complete use case, from input
to resulting effect. Tests that assert a single method in isolation are allowed
and SHOULD be used to explore edge cases and input variations that are expensive
to reach through the whole flow — but they MUST NOT be the only coverage a flow
has. Every flow MUST cover its success path and its failure paths; an error path
that no test exercises MUST NOT be considered covered.

Rationale: a suite made only of isolated method tests can be green while the
composition of those methods is broken, because the bug lives in how the pieces
interact rather than inside any one of them. Method-level tests are still the
cheapest way to cover many inputs, so this rule is additive, not exclusive: keep
them, and add the flow test that proves the pieces work together. Failure paths
are where that matters most — they are the least exercised in development and the
most expensive in production.

### Explicit Over Clever
What a piece of code does MUST be evident where it happens. Hidden side effects
and implicit control flow MUST NOT be introduced to save lines. Any literal that
carries meaning — a threshold, a limit, a timeout, a retry count — MUST be a
named constant rather than an inline value. A literal that carries no meaning
beyond its own value, such as an index of 0 or an increment of 1, is exempt.
Comments MUST explain why a decision was made: the constraint, the trade-off, or
the non-obvious reason behind it. A comment that restates what the code already
says is a signal that the code SHOULD be rewritten to say it.

Rationale: code is read far more often than it is written, and usually by
someone without the context that made the clever version feel obvious. An
unexplained literal is a decision nobody can review, because its origin and its
safe range are invisible. Keeping comments on the why preserves the information
the code genuinely cannot carry, without creating a second description of
behaviour that silently goes stale.

### Contained Changes
A change MUST be limited to the context it was asked to address. Refactoring,
renaming, reformatting, or behaviour adjustments outside that context MUST NOT
ride along; each belongs to its own change. This principle governs the scope of a
change as a whole; the root requirement that each commit be atomic governs how
that change is divided internally, and a change that stays within scope MAY still
span several commits.

Rationale: a change that reaches beyond its stated scope is a change nobody
reviewed on purpose. It hides the intended fix inside unrelated edits, makes the
diff expensive to read, and turns a revert into a choice between losing the fix
and keeping an unrelated regression.
