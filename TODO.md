# Project TODO List (Repo Agent)

This file tracks **repo-level** orchestration tasks (wiring, cross-module work, integration).
Capsule agents must not edit this file. Capsule tasks live in each capsule’s `docs/TODO.md`.

See `docs/TODO_INDEX.md` for the list of capsule TODOs.
After adding/removing capsule TODO files, run `tools/scripts/update_todo_index.sh` (or rely on the pre-commit hook).

## Next Steps (Active Development)
*   **Implement Sim-Kernel** batched tick loop (O(1)).
*   **"Stone Age" Vertical Slice** content (Basic materials, items).
*   **Implement Performance Gating** in CI (Mandatory for PRs).

## Documentation (Maintain)
*   Update `SOURCE_ATTRIBUTION.md` as new libraries are integrated.
*   Record new architectural decisions in `docs/ADRS/`.

## Completed (Infrastructure Phase)
*   ✅ Tiered Build Strategy (Vanilla+ vs Visions).
*   ✅ Swarm-Ready repository architecture.
*   ✅ SPI-based feature discovery.
*   ✅ AI Agent guardrails (AGENTS.md).
*   ✅ Performance Contract and Runtime Constitution.
*   ✅ Technical Targets (Minecraft 1.21.11).
*   ✅ Security and Contribution Policies.
