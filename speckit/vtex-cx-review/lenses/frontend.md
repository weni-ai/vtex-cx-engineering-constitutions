# Frontend & Frontend-Platform Adversarial Review Lens

Operationalizes `frontend/base-constitution.md` — plus `frontend-platform/base-constitution.md` when `frontend-platform` is active — alongside `lenses/core.md`. Defines **no standalone rules**: rows say where to look and how to grade, while the requirement itself is always the cited principle's text in `.specify/memory/constitution.md`. Inspect 1–3 sibling components, stores, and services first to match the project's framework and test stack.

---

## 1. Client Trust Pass (`Client Trust Boundary` — Mandatory Report Table)

Evaluate every changed component, route, store, adapter, and env/build file (`n/a` requires 1-line evidence):

| Surface | Diff Audit Question | Governing Principle | Severity |
|---------|---------------------|---------------------|----------|
| **DOM XSS Sinks** | Does external, API, URL, or user data reach raw HTML sinks (`v-html`, `dangerouslySetInnerHTML`, `innerHTML`, `document.write`), `eval`/`new Function`, or `javascript:`/`data:` URLs, and how is it sanitized? | `Client Trust Boundary` | `CRITICAL` |
| **Bundle Secrets** | What reaches client code through imports and public build env vars (`VITE_*`, `NEXT_PUBLIC_*`, `VUE_APP_*`, `REACT_APP_*`)? | `Client Trust Boundary` / `Security and Secrets` | `CRITICAL` |
| **Storage, URL & Console** | What do URL params, `localStorage`/`sessionStorage`, `console.*`, and telemetry payloads carry? | `Client Trust Boundary` / `Observability` | `CRITICAL` |
| **UX Guards vs Authz** | What do route guards and role flags protect, and is any data fetched only to be filtered out in memory? | `Client Trust Boundary` | `CRITICAL` |
| **Origins & Redirects** | How do `postMessage` handlers check `event.origin`, and how are dynamic redirect targets validated? | `Client Trust Boundary` / `Communication` | `CRITICAL` / `HIGH` |

---

## 2. Async State & Boundaries Pass (Mandatory Report Table)

| Check | Diff Audit Question | Governing Principle | Severity |
|-------|---------------------|---------------------|----------|
| **Async Lifecycle** | How are loading, success, and error states tracked, and can they contradict each other or fail silently? | `Async State Correctness` | `HIGH` |
| **Concurrency & Rollback** | How are double-submits, superseded requests (`AbortController` / request token), and failed optimistic updates handled? | `Async State Correctness` | `HIGH` |
| **Service & Adapter Edge** | Where do HTTP calls live, and where is backend field naming normalized before data reaches stores and components? | `API Integration` / `API and Data Boundaries` | `HIGH` |
| **State Ownership** | Where does the changed state live, and is server or prop state duplicated into it? | `State Management` | `MEDIUM` / `HIGH` |

---

## 3. Rendering, Bundle & Lifecycle Classification (`Performance` — Mandatory Table)

| Surface Shape | Diff Signal | What to Check | Violation Severity |
|---------------|-------------|---------------|--------------------|
| **Large dynamic list** | Multi-hundred-row / unbounded collection in DOM | Pagination, capping, or virtualization, and what the `key` is bound to | `HIGH` |
| **Frequent event path** | Search-as-you-type, `scroll`, `resize`, drag, high-rate socket | Debouncing/throttling of the handler and memoization of derived state | `MEDIUM` / `HIGH` |
| **New dep / heavy asset** | New package, chart/editor/modal, below-the-fold route, media | Unused deps, import tree-shaking, lazy loading, and asset optimization | `MEDIUM` / `HIGH` |
| **Mount side effects** | Listeners, timers, observers, sockets, bus subscriptions | Cleanup of each registered side effect on unmount | `HIGH` |
| **Ordinary render** | Standard form, card, dialog | Keep declarative — flag gratuitous memoization/indirection (`Proportional Design`) | `MEDIUM` |

---

## 4. UI & Platform Principle Severity Map

Grade violations of these principles in changed `.ts`, `.tsx`, `.vue`, `.js`, `.jsx`, style, and locale files as follows:

| Constitution Principle | Where to Look | Severity |
|------------------------|---------------|----------|
| `Type Safety` | New file languages, `any` usage, typing of props/emits/public contracts, TypeScript config | `HIGH` |
| `Accessibility` | Interactive elements built on non-interactive tags, form labels, focus states, color-only status, image `alt` | `HIGH` |
| `Internationalization` | User-facing text in markup, toasts, and placeholders; locale file parity; date/number/currency formatting | `HIGH` |
| `Single Responsibility` / `Naming Conventions` / `Component Architecture` | File length, multi-purpose functions, logic inlined in templates, casing, and naming of components, props, events, handlers, and state | `MEDIUM` |
| `Styling Standards` / `BEM Methodology` | ID selectors, selector nesting, raw visual values where tokens exist, BEM block/element/modifier naming | `MEDIUM` / `HIGH` |
| **CX Platform** (`frontend-platform` active): `Component Usage` / `Deprecated Components` / `Token Consumption` | Custom or copied versions of `@weni/unnnic-system` primitives, deprecated Unnnic components, raw values, or tokens not documented by the Unnnic skill | `HIGH` |
| **CX Platform**: `Semantic HTML` / `Linting and Formatting` | Landmark elements, heading hierarchy and `h1` count (`MEDIUM`/`HIGH`); lint errors against the configuration the principle mandates (`HIGH`) | `MEDIUM` / `HIGH` |
| **CX Platform**: `Isolation` / `Communication` | `window` globals, style scoping, global listeners, and DOM access beyond the microfrontend boundary | `CRITICAL` / `HIGH` |

---

## 5. Interactive Flow Test Matrix (`Testing` + `Verification Integrity`)

Confirm behavior tests, colocated where `Testing` prescribes, verify user-observable outcomes across changed flows:
1. Happy path (accessible interaction → normalized service call → updated UI); 2. Pending/loading state + double-submit guard; 3. Error state feedback + optimistic rollback without unhandled rejection; 4. Stale/superseded request race handling when applicable; 5. Adapter normalization on new/changed contracts.
