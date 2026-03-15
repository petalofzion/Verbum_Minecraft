# Book Enhancement Capsule

## Purpose
Provide a library-backed book system that allows very large books (e.g., the full Bible) to be read from a vanilla written book without storing megabytes in item NBT.

## Scope
- Feature registrations via `FeatureEntrypoint`
- Pure logic/data only (no Fabric/Minecraft classes)
- Offline-first book content store, pagination rules, and navigation helpers

## Dependencies
- `modules/core/api`
- `modules/core/spi`

## Key Files
- `module.json`
- `src/main/java/.../BookEnhancementFeature.java`
- `src/main/resources/META-INF/services/com.verbum_minecraft.spi.FeatureEntrypoint`
- `docs/PRD.md`, `docs/MVP.md`
- `docs/TODO.md`
- `docs/agent-logs/`

## Content Assets (Stage 1)
- Content lives in feature capsules (e.g., `modules/features/library/bible`).
- Book Enhancement loads packaged resources from the runtime classpath.
