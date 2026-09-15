# Frontend Base Constitution

Frontend engineering principles that specialize the root constitution for
client-side projects. These principles MUST NOT contradict the root; they add
domain-specific rules. Principles are declarative and testable, stated with
`MUST` / `SHOULD` and an explicit rationale. Stack, tooling, and paths belong to
the project layer, not here.

## Core Principles

### Code as Documentation
All code MUST be written entirely in English, including variable names, function
names, comments, and documentation. Exception: domain-specific terms or acronyms
that only have meaning in the original language MAY remain untranslated. Code
MUST prioritize readability and clarity over brevity. Every non-trivial decision
MUST be documented through meaningful comments that explain the "why", not the
"what".

Rationale: a globally comprehensible codebase enables open-source contribution
and cross-team collaboration. Clear, self-documenting code reduces onboarding
time and maintenance costs. Comments that explain reasoning prevent future
developers from breaking invariants they cannot see.

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

### Semantic HTML
HTML MUST use semantic elements (`header`, `nav`, `main`, `section`, `article`,
`aside`, `footer`) wherever they apply. Non-semantic containers (`div`, `span`)
MUST only be used when no semantic alternative exists. Heading tags (`h1`–`h6`)
MUST follow a logical hierarchy; every page MUST have exactly one `h1`. Elements
SHOULD have at least one class to describe their purpose, even when no styling
is applied.

Rationale: semantic HTML improves accessibility for assistive technologies,
boosts SEO through clearer content structure, and makes the markup self-
documenting for developers. Proper heading hierarchy is critical for screen
reader navigation.

### Styling Standards
Inline styles MUST NOT be used; all styles MUST be centralized in external
stylesheets or scoped component styles. CSS selectors MUST use classes only; IDs
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

Rationale: centralized, deduplicated state prevents synchronization bugs and
makes data flow traceable. Modular state organization mirrors feature boundaries
and simplifies testing.

### Async State Correctness
Async operations MUST track loading, success, and error states consistently.
Silent failures MUST NOT occur; errors MUST be surfaced to the user or logged
for debugging. Contradictory states (e.g., loading and error simultaneously)
MUST be prevented. Double submissions MUST be guarded against. State rollback
MUST occur when an operation fails after optimistic updates.

Rationale: incorrect async state is one of the most common sources of bugs and
broken UX. Users must always know what is happening and never be left in limbo.

### API Integration
API calls MUST be encapsulated in dedicated service modules separate from
components. Error handling MUST be explicit; API errors MUST NOT surface as
unhandled exceptions. Loading and error states MUST be tracked and reflected in
the UI. Sensitive data MUST NOT be logged or exposed in error messages.

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
Components with business logic MUST have unit tests. Test files MUST be
colocated with the code they test (e.g., `__tests__/` subdirectory). Tests MUST
NOT depend on implementation details; they MUST verify behavior and outcomes.
Tests MUST NOT be added solely to increase coverage; they MUST validate real
user behavior. A test that would still pass after a regression is introduced
MUST be fixed or removed.

Rationale: colocated tests are easier to maintain and discover. Behavior-focused
tests survive refactors; implementation-coupled tests become maintenance
liabilities. Tests that do not catch real bugs provide false confidence.

### Linting and Formatting
All code MUST pass the project's ESLint configuration without errors before
merge. Projects MUST use `@weni/eslint-config` from
https://github.com/weni-ai/eslint-config as their base configuration. Formatting
MUST be enforced through the configured tooling; style debates MUST NOT occur in
code review.

Rationale: a shared ESLint configuration ensures consistency across all frontend
projects. Automated enforcement eliminates subjective discussions and guarantees
a uniform codebase.

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
debounced when executed on frequent events. Assets MUST be optimized (images,
fonts). Bundle size impact SHOULD be considered before adding new dependencies.
Initial load SHOULD prioritize above-the-fold content.

Rationale: frontend performance directly affects user experience, conversion
rates, and search ranking. Keeping bundles lean and computations efficient
protects users on slow networks and devices.

### Internationalization
User-facing strings MUST NOT be hardcoded; they MUST be externalized to locale
files. Date, number, and currency formatting MUST respect the user's locale.
Locale files SHOULD maintain parity across all supported languages. New strings
introduced in a PR MUST be localized before merge.

Rationale: externalized strings enable translation without code changes. Locale-
aware formatting prevents confusion and builds trust with international users.

### Defensive Programming
Defensive guards (null checks, fallback branches, runtime assertions) SHOULD
only be added when the invalid state is realistically reachable. Root causes
MUST be fixed rather than masked with defensive code. Guards MUST follow the
patterns already established in the surrounding code.

Rationale: unnecessary defensive code clutters the codebase and obscures real
logic. Guards should protect against realistic failures, not hypothetical ones.
Fixing root causes produces more robust code than adding layers of protection.

### Maintainability
Business rules MUST NOT be duplicated across multiple locations; they MUST be
centralized in a single source of truth. Local duplication of utility code MAY
exist when extraction would create unnecessary coupling. Abstractions SHOULD
only be created when there is a clear pattern across multiple use cases.

Rationale: not all duplication is harmful. Premature abstraction creates
coupling that is worse than the duplication it eliminates. Centralize business
rules; tolerate incidental duplication.
