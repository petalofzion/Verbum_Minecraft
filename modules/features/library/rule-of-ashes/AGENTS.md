# AGENTS.md: Guidelines for `modules/features/library/rule-of-ashes`

## Purpose
This capsule defines the Rule of Ashes profile manual and item registration for Vorago.

## Allowed Paths
- `modules/features/library/rule-of-ashes/**`

## Non-Negotiables
- **Scope:** Only edit files under `modules/features/library/rule-of-ashes`.
- **No cross-feature imports:** Do not import from other feature modules.
- **Pure registration:** Use API contracts (`modules/core/api`) and SPI (`modules/core/spi`) only.
- **Contract source:** Use contracts listed in `docs/contracts/CORE_API.md`. Log if missing.
- **Wiring status:** Check `docs/contracts/CONTRACT_INDEX.md` for what is wired.
- **No platform classes:** Do not import Minecraft/Fabric classes in this module.
- **SPI wiring required:** Keep `module.json` and `META-INF/services/com.verbum_minecraft.spi.FeatureEntrypoint` in sync.
- **No wiring:** Do not touch `assemblies/*` or `build-logic/*`.

## Required Capsule Docs
- `README.md`
- `docs/PRD.md`
- `docs/MVP.md`
- `docs/TODO.md`
- `docs/agent-logs/README.md`

## Issue / Question Logging
If blocked or uncertain, add a log under:
`docs/agent-logs/YYYY-MM-DD_<type>_<slug>.md`

## Commands (when you change this capsule)
- `./gradlew build`
- `./gradlew check`
