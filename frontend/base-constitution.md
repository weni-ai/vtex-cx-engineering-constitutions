# Frontend Base Constitution

Frontend engineering principles that specialize the root constitution for
client-side projects. These principles MUST NOT contradict the root; they add
domain-specific rules. Principles are declarative and testable, stated with
`MUST` / `SHOULD` and an explicit rationale. Stack, tooling, and paths belong to
the project layer, not here.

## Core Principles

### Client Trust Boundary
The browser executes outside the organization's control: client-side route
guards, role flags, and hidden controls MUST be treated strictly as
user-experience affordances, never as authorization enforcement. Unauthorized or
cross-tenant data MUST NOT be fetched to the client to be filtered in memory.
Server secrets and private credentials MUST NOT be imported into client code or
exposed through public build-time environment variables. Untrusted or external
values MUST NOT reach raw HTML rendering sinks, dynamic code evaluation, or
unvalidated `javascript:` or `data:` URLs without strict sanitization.
Cross-window message listeners MUST validate `origin` against an explicit
allowlist, and post-authentication or parameter-driven redirects MUST restrict
targets to same-origin paths or an explicit allowlist. Sensitive tokens and
personal data MUST NOT be exposed in URLs, unapproved browser storage, or
console output.

Rationale: anything shipped to or executed in the browser can be inspected and
tampered with by the user or an injected script. Keeping secrets and access
control on the server, sanitizing DOM sinks, and validating origins and
redirects prevent XSS, credential leakage, and open-redirect vulnerabilities.

### Type Safety
All new files MUST be written in TypeScript. JavaScript files SHOULD only be
modified for bug fixes or small changes; substantial modifications SHOULD
include migration to TypeScript. Type definitions MUST be explicit; `any` SHOULD
be avoided except when interfacing with untyped external libraries. Strict mode
MUST be enabled in the TypeScript configuration.

Rationale: static typing catches errors at compile time, enables better tooling
support, and serves as inline documentation. Gradual migration allows
incremental adoption without blocking delivery.

### Single Responsibility
Each file SHOULD contain no more than 350 lines of code. Each function MUST have
only one responsibility. Template logic MUST be extracted to computed properties
or methods to keep markup clean and declarative. Complex conditional rendering
MUST be abstracted into descriptive boolean variables.

Rationale: small, focused units are easier to test, review, and refactor. Large
files and multi-purpose functions create cognitive overload and hide bugs.
Readable templates make the component's visual structure immediately apparent.

### Naming Conventions
Variable and function names MUST use `camelCase`. Component names MUST use
`PascalCase`. File and directory names MUST be lowercase. Abbreviations MUST be
avoided unless they are universally understood; clarity MUST take precedence
over conciseness.

Rationale: consistent naming reduces cognitive load and makes the codebase
searchable. Predictable file naming enables automated tooling and faster
navigation.

### Component Architecture
Components MUST be named descriptively and reflect their purpose. Related
components SHOULD be grouped in folders or subfolders. Component prefixes SHOULD
indicate scope or nature (e.g., `AppHeader`, `UserProfile`). Props MUST have
descriptive names (e.g., `userName`, `userEmail`). Events MUST be prefixed with
`on` (e.g., `onUserEmailChange`, `onUserPermissionsUpdate`). Methods that handle
state updates SHOULD be prefixed with `handle` (e.g., `handleUserPermissions`).
State variables MUST clearly reflect what they represent (e.g., `isLoadingUser`,
`errorStatusUser`).

Rationale: a predictable component structure makes the codebase navigable and
maintainable. Clear naming conventions for props, events, and state reduce
integration errors and make component interfaces self-documenting.

### Styling Standards
CSS selectors MUST use classes only; IDs
MUST be reserved for JavaScript targeting when no alternative exists. Nested
selectors SHOULD be avoided to preserve specificity control and readability.
Design system tokens (colors, spacing, typography) MUST be used instead of
hardcoded values whenever available.

Rationale: centralized styles enable theming, ensure consistency, and simplify
maintenance. Avoiding IDs and deep nesting prevents specificity wars that make
CSS unpredictable. Design tokens create a single source of truth for visual
language.

### BEM Methodology
CSS class names MUST follow the BEM (Block Element Modifier) methodology to
prevent selector conflicts and clarify component boundaries. Blocks MUST be
independent components (`.button`). Elements MUST be parts of a block and use
double underscores (`.button__text`). Modifiers MUST represent variations and
use double hyphens (`.button--large`). Elements MUST NOT be nested in class
names (`.block__elem`, not `.block__elem1__elem2`).

Rationale: BEM provides scoped, collision-free CSS that scales across large
applications and teams. Flat element naming keeps selectors predictable and
maintainable.

### State Management
Global state MUST be managed through the project's designated state management
solution. State MUST NOT be duplicated across components or stores. Related
state SHOULD be grouped in logical objects or modules. Local component state
SHOULD be preferred when the data does not need to be shared.

Rationale: centralized, duplicated state prevents synchronization bugs and
makes data flow traceable. Modular state organization mirrors feature boundaries
and simplifies testing.

### Async State Correctness
Async operations MUST track loading, success, and error states consistently.
Silent failures MUST NOT occur; errors MUST be surfaced to the user or logged
for debugging. Contradictory states (e.g., loading and error simultaneously)
MUST be prevented. Double submissions MUST be guarded against. Superseded or
concurrent requests triggered by rapid navigation or filtering MUST be cancelled
or ignored so stale responses cannot overwrite newer state. State rollback MUST
occur when an operation fails after optimistic updates.

Rationale: incorrect async state and out-of-order responses are among the most
common sources of broken UX and corrupted UI state. Users must always see
accurate progress and never have current selections overwritten by stale network
replies.

### API Integration
API calls MUST be encapsulated in dedicated service modules separate from
components. Error handling MUST be explicit; API errors MUST NOT surface as
unhandled exceptions. Loading and error states MUST be tracked and reflected in
the UI.

Rationale: separating API logic from presentation enables reuse, simplifies
testing, and keeps components focused on rendering. Explicit error handling
prevents silent failures; safe logging protects user data.

### API and Data Boundaries
Backend contracts MUST remain at the API/service boundary. Internal code MUST
use camelCase; snake_case fields from the backend MUST be normalized at the
adapter layer. Raw backend fields MUST NOT leak into stores, business logic, or
components. DTOs or raw API interfaces that intentionally represent the backend
contract MAY use the backend naming convention.

Rationale: clean data boundaries prevent coupling between frontend code and
backend implementation details. Normalization at the edge keeps the rest of the
codebase consistent and refactorable.

## Quality Standards

### Testing
Components, state stores, composables or hooks, and adapters with business or
interaction logic MUST have colocated automated tests (e.g., `__tests__/`
subdirectory). Tests MUST verify user-observable behavior, rendered async
states, accessibility semantics, and normalized service boundaries rather than
internal component implementation details.

Rationale: colocated tests are easier to maintain and discover. Behavior-focused
tests survive internal refactors and prove what the user actually experiences,
complementing the root verification-integrity guarantees.

### Accessibility
Interactive elements MUST be keyboard accessible. Form inputs MUST have
associated labels. Color MUST NOT be the only means of conveying information.
Images MUST have meaningful `alt` text or be marked decorative with `alt=""`.
Focus states MUST be visible.

Rationale: accessibility is a legal requirement in many jurisdictions and a
moral imperative. Accessible interfaces also improve usability for all users,
not just those with disabilities.

### Performance
Unused dependencies MUST be removed. Heavy computations MUST be memoized or
debounced when executed on frequent events. Large dynamic lists MUST be
paginated, capped, or virtualized and keyed by stable domain identifiers rather
than mutable array indices. Subscriptions, timers, observers, and global
listeners registered by a component MUST be cleaned up on unmount. Assets MUST
be optimized (images, fonts). Bundle size impact SHOULD be considered before
adding new dependencies, and initial load SHOULD prioritize above-the-fold
content.

Rationale: frontend performance and lifecycle cleanup directly affect user
experience, memory stability, and responsiveness on slow networks and devices.

### Internationalization
User-facing strings MUST NOT be hardcoded; they MUST be externalized to locale
files. Date, number, and currency formatting MUST respect the user's locale.
Locale files SHOULD maintain parity across all supported languages. New strings
introduced in a PR MUST be localized before merge.

Rationale: externalized strings enable translation without code changes. Locale-
aware formatting prevents confusion and builds trust with international users.
