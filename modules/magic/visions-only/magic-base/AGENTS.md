# AGENTS.md: Magic Base (visions-only)

## Purpose
Guidelines for the core magic feature module.

## Non-negotiables
- **Boundary:** Only edit files under `modules/magic/visions-only/magic-base/`.
- **Wiring:** Do not touch `settings.gradle`, `assemblies/`, `build-logic/`, or `modules/core/`.
- **Contracts:** If you need a new API contract, request it in your spec doc and stop.
- **Registration:** Implement `FeatureEntrypoint` and register via `META-INF/services/`.

## Commands to run
- `./gradlew :modules:magic:visions-only:magic-base:build`
- `./gradlew :modules:magic:visions-only:magic-base:check`

## Definition of Done for this directory
- Feature compiles independently.
- `FeatureEntrypoint` is correctly implemented.
- No forbidden imports from other feature modules.
