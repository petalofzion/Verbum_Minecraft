# AGENTS.md: Tech Base (visions-only)

## Purpose
Guidelines for the core tech feature module.

## Non-negotiables
- **Boundary:** Only edit files under `modules/tech/visions-only/tech-base/`.
- **Wiring:** Do not touch `settings.gradle`, `assemblies/`, `build-logic/`, or `modules/core/`.
- **Contracts:** If you need a new API contract, request it in your spec doc and stop.
- **Registration:** Implement `FeatureEntrypoint` and register via `META-INF/services/`.

## Commands to run
- `./gradlew :modules:tech:visions-only:tech-base:build`
- `./gradlew :modules:tech:visions-only:tech-base:check`

## Definition of Done for this directory
- Feature compiles independently.
- `FeatureEntrypoint` is correctly implemented.
- No forbidden imports from other feature modules.
