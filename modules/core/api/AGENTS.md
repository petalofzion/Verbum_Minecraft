# AGENTS.md: Guidelines for `modules/core/api` Contributions

## Purpose
This document provides specific guidelines for AI agents contributing to the `modules/core/api` directory. This module defines the project's public contracts and vocabulary, and maintaining its stability and purity is paramount to prevent "Dependency Hell" and ensure future compatibility. These guidelines augment and, where applicable, override the general rules in the root `AGENTS.md`.

## Non-Negotiables for `modules/core/api`

*   **API Stability:** Changes to existing API contracts (interfaces, enums, public constants) are extremely high-impact. Avoid breaking changes at all costs.
*   **Backwards Compatibility:** All changes to existing API elements must be strictly backward-compatible.
*   **No Logic, No Implementation:** This module **MUST NOT** contain any concrete implementations, business logic, utility methods with logic, or non-enum fields. It is strictly for interfaces, enums, and basic data classes (pure POJOs without behavior).
*   **Deprecation Rules:** If an API element must be changed in a potentially breaking way (highly discouraged), the old element must first be clearly marked `@Deprecated` with a clear javadoc explaining the replacement and a scheduled removal version.
*   **Migration Notes:** For any API changes that might require migration, prepare clear migration notes for downstream modules/consumers.

## Commands to Run

For any changes to `modules/core/api`:

```bash
# Run all project builds and checks to ensure no downstream breakage
./gradlew build

# Run unit tests for API (primarily checking interface contracts, if any)
./gradlew :modules:core:api:test
```

## Definition of Done for `modules/core/api` Contributions

A contribution to `modules/core/api` is considered "Done" when:

*   All code strictly adheres to the "No Logic, No Implementation" rule.
*   The project builds successfully (`./gradlew build`).
*   All relevant tests pass (`./gradlew :modules:core:api:test`).
*   **No breaking changes are introduced to existing public API elements** without a preceding deprecation cycle.
*   `docs/ARCHITECTURE_MAP.md` is updated if the API contract definitions significantly change or new core interfaces are added that impact architectural understanding.
*   If deprecations are introduced, clear migration guidance is prepared.
*   An ADR is created for any non-backward-compatible or significant API evolution, detailing rationale and impact.
