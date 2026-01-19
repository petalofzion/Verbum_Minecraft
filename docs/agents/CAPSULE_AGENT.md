# Capsule Agent Guide (Feature Work)

You are a **capsule agent** if you implement or fix a single feature/mod inside one capsule folder.
Stay siloed. Do not touch wiring or cross-module code.

## Read Order (do not read repo-wide docs)
1. `FUNNELING.md`
2. Go to your capsule folder.
3. Capsule `AGENTS.md`
4. `docs/ARCHITECTURE_MAP.md`
5. `docs/runtime-constitution.md`
6. `docs/contracts/CORE_API.md`
7. `docs/contracts/CONTRACT_INDEX.md`
8. Capsule docs: `README.md`, `docs/PRD.md`, `docs/MVP.md`, `docs/TODO.md`, `docs/agent-logs/`

## Allowed Paths
- Only your capsule folder (example: `modules/features/library/bible/**`)

## Typical Duties
- Implement feature logic/data inside the capsule only.
- Update capsule docs and capsule `docs/TODO.md`.
- Log any questions/decisions in `docs/agent-logs/`.

## Do Not
- Do not touch `assemblies/*`, `build-logic/*`, `modules/core/*`, or other features.
- Do not add simulation loops or use Minecraft/Fabric classes.
- Do not edit root `TODO.md` or `docs/TODO_INDEX.md`.
- Do not search/list outside your capsule for patterns; use the contract docs or log and ask.

## Conventions (must follow)
- **Java 21** only for code.
- **Mojang mappings**: do not use Yarn class names.
- Feature code is **pure logic/data** with API/SPI contracts only.
- Package naming: `com.verbum_minecraft.features.<domain>.<feature>`.
- Resource IDs: `verbum:<path>` (lowercase, underscore).
- Keep `module.json` and SPI file in sync.

## Common Pitfalls
- Missing SPI registration in `META-INF/services`.
- Missing assets/lang entries for items.
- Needing cross-module wiring: **stop and log**.
- Ignoring wiring status in `docs/contracts/CONTRACT_INDEX.md`.
- Assuming assets are broken before confirming they are wired into the assembly (see `docs/wiring/ASSEMBLY_WIRING.md`).

## If You Need Cross-Module Changes
Run a **capability sweep** first, log all needs in one entry, then stop and notify the repo agent.
