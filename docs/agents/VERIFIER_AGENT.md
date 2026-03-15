# Verifier Agent Guide

You are a **verifier agent** if your job is to validate an implementation, not to author it.

Use this role after:
- new API/SPI seams,
- assembly wiring changes,
- profile placement changes,
- runtime-sensitive feature work.

## Read Order
1. `AGENTS.md`
2. `docs/agents/ORCHESTRATOR_QUICKSTART.md`
3. `docs/agents/ORCHESTRATION_SPEC.md`
4. `docs/UPDATE_SURFACES.md`
5. `docs/GOTCHAS.md`
6. task packet / handoff notes
7. only the touched code and relevant docs

## Duties
- run the required verification commands
- identify the smallest failing surface
- audit architecture separation against the documented assembly/API/capsule boundaries when required
- report the failure clearly
- do not broaden scope into implementation unless explicitly reassigned

## Default Checks
- `./gradlew check build`
- targeted assembly builds for touched editions
- targeted runtime smoke checks when assemblies or core contracts changed
- `python3 tools/scripts/verify_boundary_separation.py` when architecture audit is required

## Runtime Smoke Rule
If a task changed `assemblies/*` or `modules/core/api/*`, treat a targeted `runClient` or equivalent dev-runtime launch as a recommended smoke check, not an optional extra.

## Architecture Audit Rule
If a task changed `assemblies/*`, `modules/core/api/*`, `modules/core/spi/*`, or introduced a new capability seam, treat boundary verification as part of the done gate.

Confirm:
- Minecraft/Fabric imports did not leak into API, SPI, or feature capsules.
- Assemblies still own Minecraft/Fabric wiring, menus, screens, and registry application.
- Capsules still own feature behavior through pure contracts.
- Assembly code translates and applies pure results; it must not silently take over feature semantics.

## Output
Return:
- exact commands run
- pass/fail status
- smallest failing file/surface
- whether the issue is capsule-local, repo wiring, version gotcha, or environment
- separation verdict: `pass`, `needs_review`, or `blocked`
- boundary checks run and any boundary findings
