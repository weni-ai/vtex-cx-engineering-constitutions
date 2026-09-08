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
