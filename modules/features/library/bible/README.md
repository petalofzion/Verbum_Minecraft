# Bible Feature Capsule

This capsule provides the Bible item definition and related feature wiring for Verbum.

## Scope
- Item definition(s) registered via `FeatureEntrypoint`.
- Pure data and logic; no direct Minecraft/Fabric dependencies.

## Capsule Docs
- `docs/PRD.md`
- `docs/MVP.md`
- `docs/TODO.md`
- `docs/agent-logs/` (issues/questions/decisions)

## Key Files
- `module.json`: module metadata and dependency declarations.
- `src/main/java/.../BibleFeature.java`: feature entrypoint.
- `src/main/resources/META-INF/services/com.verbum_minecraft.spi.FeatureEntrypoint`: SPI registration.
