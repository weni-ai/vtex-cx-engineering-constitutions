# Backend Adversarial Review Lens

Operationalizes `backend/base-constitution.md` alongside `lenses/core.md` when `backend` is active. Defines **no standalone rules**: rows say where to look and how to grade, while the requirement itself is always the cited principle's text in `.specify/memory/constitution.md`. Inspect 1–3 sibling modules first and use **their** permission mechanism, scope field, worker, cache, and test harness.

---

## 1. Threat Pass (Mandatory Report Table)

Evaluate every new or changed route, RPC/GraphQL handler, admin action, use case, query, job, consumer, or webhook (`n/a` requires 1-line evidence):

| Surface | Diff Audit Question | Governing Principle | Severity |
|---------|---------------------|---------------------|----------|
| **Authentication** | Is caller identity verified before any read or side effect, with no empty or permissive auth override? | `Explicit, Scoped Authorization` | `CRITICAL` |
| **Authorization** | Does an explicit resource-scoped permission enforce role + resource access (admin/internal included)? In DRF, inspect `permission_classes`, `@permission_classes`, `DEFAULT_PERMISSION_CLASSES`, permission composition, base classes, and custom `has_permission()` against the classes and patterns the principle forbids or requires, and confirm open endpoints follow the exception path it prescribes. | `Explicit, Scoped Authorization` | `CRITICAL` |
| **Exposed Verbs** | Which HTTP methods, router entries, and ViewSet actions does the change register, and do they match the contract? | `Explicit, Scoped Authorization` / `Versioned Contracts` | `CRITICAL` |
| **Target & Mass Assignment** | Can path/query/body IDs retarget another record, or client input set server-owned fields (e.g. `scope`/`project`/`account`/`tenant`, `owner`, `role`, `status`)? | `Explicit, Scoped Authorization` / `Never Trust the Client` | `CRITICAL` |
| **Injection & SSRF** | Does external or stored input reach raw SQL, shell, templates, dynamic lookups/orderings, file paths, or outbound URLs/hosts? | `Never Trust the Client` | `CRITICAL` |
| **Data Exposure** | What do responses, error payloads, health endpoints, and logs return on success and failure? | `Fail Gracefully and Predictably` / `Observability` | `CRITICAL` |
| **Overload** | Can a caller trigger unbounded queries, oversized payloads, or expensive in-request work? (Missing rate limiting is a `LOW` observation, not a finding.) | `Scalability and Peak Load` / `Never Trust the Client` | `CRITICAL` |
| **Atomicity** | How are multi-step writes and the external side effects they trigger (tasks, events, outbound calls) grouped and ordered relative to the commit? | `Fail Gracefully and Predictably` | `HIGH` / `CRITICAL` |

---

## 2. Cross-Scope Pass (`Explicit, Scoped Authorization` — Mandatory Separate Table)

Identify the module's isolation field (e.g. `project`, `account`, `organization`, `store`, `tenant`, `owner`). List every scoped entity touched (or state `No scoped entity touched` naming the models inspected — never omit this table when scoped entities exist):

| Access Vector | Attacker Scenario | Expected Outcome | Enforced At (`file:line`) | Proving Test (`file:test`) |
|---------------|-------------------|------------------|---------------------------|----------------------------|
| Read other scope | Actor A requests Actor B's ID | Refused with the status the contract defines, zero leak | | |
| Update other scope | Actor A mutates Actor B's ID | Refused, row unchanged | | |
| Delete other scope | Actor A deletes Actor B's ID | Refused, row unchanged | | |
| Create into other scope | Body carries Actor B's scope/owner | Ignored or refused, no row in B | | |
| Link other scope's FK | Body/query carries related ID owned by Actor B | Refused, no cross-scope link | | |
| List with omitted/empty filter | Optional filter omitted, empty, or `None` | Returns only Actor A's rows | | |

Any applicable row missing **either** `Enforced At` or a non-mocked `Proving Test` (`Verification Integrity`) is `CRITICAL`.

---

## 3. Conditional Diff Triggers

Run only the checks whose trigger appears in the diff:

| Diff Trigger | Where to Look | Governing Principle | Severity |
|--------------|---------------|---------------------|----------|
| **Tokens / HMAC / shared secrets** | Algorithm selection, claim and expiry validation (for JWTs, also `aud`/`iss`), and how secrets are compared | `Never Trust the Client` | `CRITICAL` |
| **Inbound webhook / callback** | Authenticity, expiry, and replay/duplicate-delivery handling, and whether each runs before the first side effect | `Never Trust the Client` | `CRITICAL` / `HIGH` |
| **Outbound HTTP / REST propagation** | Timeout configuration (`HIGH`); validation of targets built from external or stored input, including loopback, link-local, private, and metadata addresses (`CRITICAL`); the retry policy — which failures are retried, attempt bound, backoff, idempotency or dedup key, and handling of exhausted attempts (`HIGH`/`CRITICAL`) | `Fail Gracefully and Predictably` / `Never Trust the Client` / `Bounded Retry Over REST` | `HIGH` / `CRITICAL` |
| **Worker / queue consumer** | What the consumer trusts from the payload versus what it re-reads from the database, and how it behaves on redelivery | `Explicit, Scoped Authorization` / `Never Trust the Client` | `CRITICAL` / `HIGH` |
| **Error-tracking call** | Which identifiers are attached (`HIGH` when the required set is incomplete) and whether any personal data is attached (`CRITICAL`) | `Diagnosable Errors` | `CRITICAL` / `HIGH` |
| **Schema / model change** | Migration presence, indexes on hot scope/filter paths, and compatibility with the live version across deploy and rollback | `Backward-Compatible Data Evolution` / `Scalability and Peak Load` | `HIGH` / `CRITICAL` |
| **Thresholds / timeouts / limits** | Literals carrying domain or operational meaning, and side effects hidden behind innocuous calls | `Explicit Over Clever` | `MEDIUM` |

---

## 4. Entry-Point Performance Classification (`Scalability and Peak Load` — Mandatory Table)

Check request-outliving state in process memory or on local disk (`CRITICAL`) and classify each changed entry point against `spec.md`'s declared peak load:

| Entry-Point Shape | Diff Signal | What to Check | Violation Severity |
|-------------------|-------------|---------------|--------------------|
| **Full collection** | List/query over multi-row table | Scope predicate, bounding, and indexing of the query | `CRITICAL` |
| **Bulk sync / import / fan-out** | Work where caller only needs acceptance | Whether the work runs in the request or is offloaded, its idempotency and duplicate-run handling, and any OS process spawned in the request | `CRITICAL` |
| **Hot small read** | Proven high-frequency read (poll, per-message hook, middleware) | Cache key composition, TTL, and invalidation on every write path | `CRITICAL` (key not isolated by scope) / `HIGH` (uncached hot path) |
| **Heavy in-request work** | N+1 query loops, large in-memory aggregation, serial I/O | Query batching (`select_related`/`prefetch_related`/batch), aggregation location, and caps or offloading | `HIGH` |
| **Ordinary scoped read/write** | Single record or bounded page needed synchronously | Keep inline — flag speculative cache/queue (`Proportional Design`) | `MEDIUM` |

---

## 5. Flow & Refusal Test Matrix (`Tests Exercise Flows` + `Verification Integrity`)

Confirm real entry-point flow tests (router + auth + permissions + test DB) cover every applicable surface:
1. Unauthenticated caller rejected; 2. Insufficient role rejected; 3. Own-scope happy path + persisted effect; 4. Cross-scope read/update/delete rejected with row unchanged; 5. Cross-scope related FK rejected; 6. Unregistered HTTP verb rejected; 7. Client-supplied scope/owner/role ignored or rejected; 8. Webhook bad signature, replay, and duplicate delivery; 9. Outbound timeout and retry policy behavior; 10. Query-count / page-cap assertion on list endpoints and cross-scope cache-key isolation.
