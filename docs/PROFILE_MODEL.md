# Profile Model

This document is the source of truth for Verbum's player-facing product model.

## Current State
The repo currently builds four profile assemblies:

- `veritas`
- `votum`
- `visions`
- `vorago`

Current shipped artifacts:
- `verbum-veritas.jar`
- `verbum-votum.jar`
- `verbum-visions.jar`
- `verbum-vorago.jar`

Player-facing profiles:
- `Veritas`
- `Votum`
- `Visions`
- `Vorago`

## Profile Semantics
### Veritas
The refined baseline line. This is the "truth" profile: essential, optimized, and close to baseline Minecraft.

Design intent:
- minimal but intentional changes,
- lightweight quality-of-life improvements,
- stable foundation for every larger profile,
- strongest compatibility guarantee in the line.

### Votum
The cozy and expansive line. This is the "vow" profile: slow-life play, decor, farming, atmosphere, and lower-stress progression.

Design intent:
- aesthetic depth without punitive pressure,
- broader ambient and lifestyle content than Veritas,
- devotional and pastoral tone,
- upward compatibility into Visions and Vorago.

### Visions
The flagship full experience.

Design intent:
- broad mechanical depth,
- tech, magic, and exploration systems,
- the main "complete Verbum" profile,
- includes the Veritas and Votum foundations rather than forking away from them.

### Vorago
The brutal challenge line. This is the "abyss" profile for players who want friction, danger, and pressure by design.

Design intent:
- harsh progression pressure,
- intentionally punishing modifiers and constraints,
- hostile-survival and high-risk framing,
- inherits the broader Verbum feature set and layers challenge modules or configuration overlays on top.

## Compatibility Rule
Profiles should remain monotonic wherever possible:

- `Veritas` is the refined baseline.
- `Votum` expands upward from `Veritas`.
- `Visions` expands upward from `Votum`.
- `Vorago` expands upward from `Visions`.

This keeps the migration direction simple and consistent:
- upward migrations are the supported direction,
- downgrades are not supported.

When profile-specific behavior is possible without changing registries, prefer configuration overlays over new content splits.

## Build And Metadata Implications
Current assembly ids and artifacts:

1. `assemblies/veritas` → `verbum-veritas.jar`
2. `assemblies/votum` → `verbum-votum.jar`
3. `assemblies/visions` → `verbum-visions.jar`
4. `assemblies/vorago` → `verbum-vorago.jar`

Metadata guidance:
- `shared` is reserved for non-player-facing core infrastructure under `modules/core/**`.
- Modules that define the player-facing Veritas baseline should be marked `veritas`.
- Modules that ship in `Votum`, `Visions`, and `Vorago` but not `Veritas` should be marked `votum`.
- Modules that ship in `Visions` and `Vorago` but not the calmer lines should be marked `visions`.
- Modules that ship only in `Vorago` should be marked `vorago`.

Interpretation rule:
- If a module is player-facing content or directly contributes to the identity of the shipped experience, it should not use `shared`.
- `veritas` is the default tier for anything that belongs in all four products because it starts at the bottom of the ladder and is inherited upward.
- If a support module exists primarily to serve `veritas` content, it should usually also be `veritas` rather than `shared`.
- `shared` exists only for foundational platform modules that make every profile function at all, such as API/SPI/runtime/kernel infrastructure.

Current implementation note:
- The repo already ships four assemblies.
- Today, `Votum` still shares the Veritas module set until cozy-specific modules/config layers are added.
- Today, `Vorago` still shares the Visions module set until punitive-specific modules/config layers are added.

Assembly membership is now derived from module tier metadata instead of being hand-maintained in each assembly build file.
`modules/modules.toml` is a generated summary of that metadata and should be updated through the repo scripts rather than edited by hand.

## Naming Guidance
The active public line is intentionally alliterative:
- `Veritas`
- `Votum`
- `Visions`
- `Vorago`

This gives the project a clearer conceptual progression from truth, to vow, to sight, to abyss while preserving clean upgrade semantics.
