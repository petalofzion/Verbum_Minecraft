# Repo Agent Guide (Wiring + Orchestration)

You are a **repo agent** if you touch wiring, assemblies, core modules, or cross‑module contracts.
You have broader scope and must read broader context.

## Read Order (required)
1. `README.md`
2. `WORKFLOW.md`
3. `FUNNELING.md`
4. `docs/ARCHITECTURE_MAP.md`
5. `docs/runtime-constitution.md`
6. `docs/contracts/CORE_API.md`
7. `docs/contracts/CONTRACT_INDEX.md`
8. `docs/wiring/ASSEMBLY_WIRING.md`
9. `docs/CONTRIBUTING.md`
10. `CODEOWNERS`
11. `TODO.md` and `docs/TODO_INDEX.md`
12. Nearest `AGENTS.md` for any module you touch

## Typical Duties
- Assembly wiring and Fabric/Minecraft integration (`assemblies/*`).
- Cross-module contracts in `modules/core/api` or `modules/core/spi`.
- Repo-wide consistency, documentation, and CI gates.
- Maintain `TODO.md` and `docs/TODO_INDEX.md`.
- Maintain `docs/contracts/contract_wiring.tsv` and regenerate `docs/contracts/CONTRACT_INDEX.md` when contracts or wiring change.

## Repo Agent Setup
- Run `tools/scripts/install-git-hooks.sh` to enable the TODO index pre-commit hook.
- The pre-commit hook also keeps `docs/contracts/CONTRACT_INDEX.md` up to date.
- `tools/scripts/update_contract_index.sh` requires `python3` in PATH.

## Conventions (must follow)
- **Java 21** only for code.
- **Mojang mappings** only (no Yarn names).
- Preserve module boundaries in `docs/ARCHITECTURE_MAP.md`.
- Keep assemblies as the only place for Fabric/Minecraft classes and config/IO.

## Common Pitfalls
- Adding feature logic to assemblies.
- Introducing cross-feature imports.
- Editing restricted areas without explicit need.
- Forgetting to merge capsule resources into assemblies, causing missing textures/models/lang at runtime.

## When to Stop and Log
- Architectural changes, new subsystems, or hot‑path changes require ADRs and benchmarks.

## Testing with Prism Launcher (local)
1. Build the edition you want:
   - Vanilla+: `./gradlew :assemblies:vanilla-plus:build`
   - Visions: `./gradlew :assemblies:visions:build`
2. In Prism, create a Fabric instance:
   - Minecraft: 1.21.11
   - Fabric Loader: 0.18.4
3. Add mods:
   - Fabric API 0.140.2+1.21.11
   - The built jar from `assemblies/<edition>/build/libs/`
4. Launch and verify:
   - Only install one edition jar at a time.
   - Use `/give @p verbum:bible` to confirm the item.
