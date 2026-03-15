# Repo Agent Guide (Wiring + Orchestration)

You are a **repo agent** if you touch wiring, assemblies, core modules, or cross‑module contracts.
You have broader scope and must read broader context.

## Read Order (required)
1. `README.md`
2. `WORKFLOW.md`
3. `docs/agents/ORCHESTRATOR_QUICKSTART.md`
4. `docs/agents/ORCHESTRATION_SPEC.md`
5. `FUNNELING.md`
6. `docs/ARCHITECTURE_MAP.md`
7. `docs/runtime-constitution.md`
8. `docs/contracts/CORE_API.md`
9. `docs/contracts/CONTRACT_INDEX.md`
10. `docs/wiring/ASSEMBLY_WIRING.md`
11. `docs/PROFILE_MODEL.md`
12. `docs/CAPSULE_INDEX.md`
13. `docs/UPDATE_SURFACES.md`
14. `docs/GOTCHAS.md` (version-specific pitfalls that affect wiring and assets)
15. `docs/CONTRIBUTING.md`
16. `CODEOWNERS`
17. `TODO.md` and `docs/TODO_INDEX.md`
18. Nearest `AGENTS.md` for any module you touch

## Typical Duties
- Assembly wiring and Fabric/Minecraft integration (`assemblies/*`).
- Cross-module contracts in `modules/core/api` or `modules/core/spi`.
- Repo-wide consistency, documentation, and CI gates.
- Maintain `TODO.md` and `docs/TODO_INDEX.md`.
- Maintain `docs/CAPSULE_INDEX.md` and `docs/CAPSULE_INDEX.tsv` through the generator.
- Maintain `docs/contracts/contract_wiring.tsv` and regenerate `docs/contracts/CONTRACT_INDEX.md` when contracts or wiring change.
- Prepare task packets and validate structured final reports when orchestrating subagents.
- Use `tools/scripts/verify_orchestration_run.py` when dispatching or integrating autonomous subagent work.
- Use `tools/scripts/verify_done_gate.py` before reporting a verifier-gated task as done.
- Use `python3 tools/scripts/verify_boundary_separation.py` or an equivalent verifier packet check whenever the task touches assemblies, API/SPI seams, or routing between capsules and assemblies.
- Own repo-integration follow-through after capsule subagents finish: manifest refreshes, capsule index refreshes, TODO index refreshes, and full `./gradlew check build`.
- Treat verifier failure as an iteration trigger, not as a user-facing closeout, unless a terminal blocker has been reached.

## Repo Agent Setup
- Run `tools/scripts/install-git-hooks.sh` to enable the TODO index pre-commit hook.
- The pre-commit hook also keeps `docs/contracts/CONTRACT_INDEX.md`, `docs/CAPSULE_INDEX.*`, and `modules/modules.toml` up to date.
- `tools/scripts/update_contract_index.sh` requires `python3` in PATH.
- For multi-agent runs, use `subagent_temp/active_packets/` and `subagent_temp/report_history/` so overlap and loop-brake checks are durable across runs.
- `tools/scripts/runtime_smoke_check.py` provides a standard non-GUI runtime smoke path for verifier tasks.

## Conventions (must follow)
- **Java 21** only for code.
- **Mojang mappings** only (no Yarn names).
- Preserve module boundaries in `docs/ARCHITECTURE_MAP.md`.
- Keep assemblies as the only place for Fabric/Minecraft classes and config/IO.
- **Logic ownership:** Feature/module logic lives in capsules under `modules/*`. Repo agents should only wire and integrate. If capsule logic is needed, spawn a capsule subagent using `docs/agents/SUBAGENT_ORCHESTRATION.md`.
- Enforce stop conditions and loop brakes from `docs/agents/ORCHESTRATION_SPEC.md`; do not let agents continue indefinitely after repeated no-progress reports.
- Default capsule task packets to `verification_scope: capsule_local`. Use `repo_integration` only when the delegated task is intentionally responsible for repo-wide integration updates and verification.
- For verifier-gated work, keep iterating through repair packets until verifier evidence is green; do not stop at the first failed verifier report.

## Common Pitfalls
- Adding feature logic to assemblies.
- Introducing cross-feature imports.
- Editing restricted areas without explicit need.
- Forgetting to merge capsule resources into assemblies, causing missing textures/models/lang at runtime.
- Treating executor-specific prompting as the orchestration model instead of using task packets and structured reports.
- Accepting prose-only subagent summaries without validating the diff and required checks.

## When to Stop and Log
- Architectural changes, new subsystems, or hot‑path changes require ADRs and benchmarks.

## Testing with Prism Launcher (local)
1. Build the profile you want:
   - Veritas: `./gradlew :assemblies:veritas:build`
   - Vocations: `./gradlew :assemblies:vocations:build`
   - Visions: `./gradlew :assemblies:visions:build`
   - Vorago: `./gradlew :assemblies:vorago:build`
2. In Prism, create a Fabric instance:
   - Minecraft: 1.21.11
   - Fabric Loader: 0.18.4
3. Add mods:
   - Fabric API 0.140.2+1.21.11
   - The built jar from `assemblies/<profile>/build/libs/`
4. Launch and verify:
   - Only install one profile jar at a time.
   - Use `/give @p verbum:bible` to confirm the item.
