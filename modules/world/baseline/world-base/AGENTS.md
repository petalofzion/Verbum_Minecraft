# AGENTS.md: World Base (baseline)

## Purpose
Guidelines for the core worldgen feature module.

## Non-negotiables
- **Boundary:** Only edit files under `modules/world/baseline/world-base/`.
- **Wiring:** Do not touch `settings.gradle`, `assemblies/`, `build-logic/`, or `modules/core/`.
- **Contracts:** If you need a new API contract, request it in your spec doc and stop.
- **Registration:** Implement `FeatureEntrypoint` and register via `META-INF/services/`.

## Commands to run
- `./gradlew :modules:world:baseline:world-base:build`
- `./gradlew :modules:world:baseline:world-base:check`

## Definition of Done for this directory
- Feature compiles independently.
- `FeatureEntrypoint` is correctly implemented.
- No forbidden imports from other feature modules.
