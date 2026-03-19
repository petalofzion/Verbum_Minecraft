# Project TODO List (Repo Agent)

This file tracks **repo-level** orchestration tasks (wiring, cross-module work, integration).
Capsule agents must not edit this file. Capsule tasks live in each capsule’s `docs/TODO.md`.

See `docs/TODO_INDEX.md` for the list of capsule TODOs.
After adding/removing capsule TODO files, run `tools/scripts/update_todo_index.sh` (or rely on the pre-commit hook).

## Next Steps (Active Development)
*   **Implement Sim-Kernel** batched tick loop (O(1)).
*   **"Stone Age" Vertical Slice** content (Basic materials, items).
*   **Add actual Vocations gameplay layers** (cozy modules and/or config overlays) on top of the Veritas baseline.
*   **Add actual Vorago gameplay layers** (punitive modules and/or config overlays) on top of the Visions assembly.
*   **Add the first `vocations` and `vorago`-tagged modules** so the higher profiles stop being only config/name scaffolds.

## Documentation (Maintain)
*   Update `SOURCE_ATTRIBUTION.md` as new libraries are integrated.
*   Record new architectural decisions in `docs/ADRS/`.

## Completed (Infrastructure Phase)
*   ✅ Real GitHub CI workflow activated for `check` + `build`.
*   ✅ Root verification tasks wired into `check`.
*   ✅ Orchestration spec added for bounded autonomous agent work.
*   ✅ Four-profile player model documented (`Veritas / Vocations / Visions / Vorago`).
*   ✅ Live assembly/profile migration completed (`veritas`, `vocations`, `visions`, `vorago`).
*   ✅ Assembly membership now derives from module tier metadata instead of hand-maintained per-profile lists.
*   ✅ Module manifest verification added so `modules/modules.toml` stays aligned with `module.json`.
*   ✅ Orchestration schemas/examples and Codex packet wrapper are validated in repo checks.
*   ✅ Tiered Build Strategy for monotonic supersets.
*   ✅ Swarm-Ready repository architecture.
*   ✅ SPI-based feature discovery.
*   ✅ AI Agent guardrails (AGENTS.md).
*   ✅ Performance Contract and Runtime Constitution.
*   ✅ Technical Targets (Minecraft 26.1-pre-3).
*   ✅ Security and Contribution Policies.
