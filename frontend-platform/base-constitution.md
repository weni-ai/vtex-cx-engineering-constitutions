# Frontend Platform Base Constitution

Frontend engineering principles that specialize the frontend constitution for
CX Platform projects (microfrontends and host applications). These principles
MUST NOT contradict the root or frontend base; they add platform-specific rules.
Principles are declarative and testable, stated with `MUST` / `SHOULD` and an
explicit rationale. Stack, tooling, and paths belong to the project layer, not
here.

## Inheritance

This constitution extends `frontend/base-constitution.md`. All principles
defined in the frontend base constitution MUST be followed. The rules below
are additional requirements specific to CX Platform projects.

```
base-constitution.md + frontend/base-constitution.md + frontend-platform/base-constitution.md
```

## Core Principles

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

## Design System Integration

### Component Usage
UI primitives MUST be sourced from the Unnnic design system library
(`@weni/unnnic-system`) when available. Custom components MUST NOT duplicate
design system functionality. Design system updates MUST be adopted through
controlled version upgrades, not copy-pasted code.

For component references, props, tokens, and usage patterns, the Unnnic skill
MUST be consulted. The skill provides authoritative guidance on available
components, their modern alternatives, and correct implementation patterns.

Rationale: a shared component library guarantees visual consistency, reduces
duplication, and centralizes accessibility fixes. Versioned consumption provides
a predictable upgrade path.

### Deprecated Components
Legacy components MUST NOT be introduced in new code when modern alternatives
exist. The Unnnic skill documents which components are deprecated and their
recommended replacements. Existing usages SHOULD be migrated when the
surrounding code is being modified.

Rationale: deprecated components will be removed in future versions. Preventing
new usages limits migration scope and keeps the codebase moving forward.

### Token Consumption
Color, typography, spacing, shadow, and radius values MUST reference design
tokens, not raw values. Semantic tokens MUST be preferred over primitive tokens
when styling UI surfaces. The Unnnic skill documents all available tokens and
their intended use cases. Tokens MUST NOT be invented; only documented tokens
are valid.

Rationale: tokens decouple design decisions from implementation, enabling
global visual changes without hunting through code. Using only documented tokens
prevents inconsistencies and future breakage.

## Microfrontend Principles

### Isolation
Microfrontends MUST NOT pollute the global scope (window, document styles).
Styles MUST be scoped or prefixed to avoid collision with the host or other
microfrontends. Global event listeners MUST be cleaned up on unmount.

Rationale: isolation prevents cross-microfrontend interference and makes each
module independently deployable and testable.

### Communication
Microfrontends MUST communicate with the host through a documented contract
(custom events, props, or a shared message bus). Direct DOM manipulation of
elements outside the microfrontend boundary MUST NOT occur.

Rationale: explicit contracts make integration predictable and allow
independent evolution of host and module. DOM encapsulation prevents fragile
coupling.

## Quality Standards

### Linting and Formatting
All code MUST pass the project's ESLint configuration without errors before
merge. Projects MUST use `@weni/eslint-config` from
https://github.com/weni-ai/eslint-config as their base configuration. Formatting
MUST be enforced through the configured tooling; style debates MUST NOT occur in
code review.

Rationale: a shared ESLint configuration ensures consistency across all frontend
projects. Automated enforcement eliminates subjective discussions and guarantees
a uniform codebase.
