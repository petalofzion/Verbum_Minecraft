# <Feature Name> Capsule

## Purpose
Describe the feature in 2-3 sentences: what it provides and what it does not do.

## Scope
- Feature registrations via `FeatureEntrypoint`
- Pure logic/data only (no Fabric/Minecraft classes)

## Dependencies
- `modules/core/api`
- `modules/core/spi`
- Optional: `modules/core/sim-kernel`, `modules/core/ux-framework`

## Key Files
- `module.json`
- `src/main/java/.../<FeatureEntrypoint>.java`
- `src/main/resources/META-INF/services/com.verbum_minecraft.spi.FeatureEntrypoint`
- `docs/PRD.md`, `docs/MVP.md`
- `docs/TODO.md`
- `docs/agent-logs/`
