# AGENTS.md: Guidelines for `modules/features/<domain>/<feature>`

## Scope
You are working inside a single capsule. Your entire scope is:
`modules/features/<domain>/<feature>/`

## Allowed Paths
- `modules/features/<domain>/<feature>/**`

## Non-Negotiables
- **No platform classes:** Do not import Minecraft/Fabric classes in this capsule.
- **No cross-feature imports:** Never import another feature module.
- **Pure logic/data only:** Use API/SPI contracts only (`modules/core/api`, `modules/core/spi`).
- **Contract source:** Only use contracts listed in `docs/contracts/CORE_API.md`. Log if missing.
- **Wiring status:** Check `docs/contracts/CONTRACT_INDEX.md` for what is wired.
- **No repo searching:** Do not search/list outside your capsule for examples; use contract docs or log a question.
- **Assets:** If textures/models/lang appear missing, check `docs/wiring/ASSEMBLY_WIRING.md` and log a wiring issue if assets are not merged.
- **No wiring:** Do not touch `assemblies/*` or `build-logic/*`.
- **SPI consistency:** Keep `module.json` and `META-INF/services/com.verbum_minecraft.spi.FeatureEntrypoint` in sync.

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
