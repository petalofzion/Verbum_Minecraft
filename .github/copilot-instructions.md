# Copilot Instructions for Verbum Minecraft

This repository uses a tiered architecture and a "swarm-ready" multi-project Gradle setup. 

## Primary Rules
- **Follow root AGENTS.md:** Always prioritize the rules in the root `AGENTS.md`.
- **Nested AGENTS.md:** If you are working in a specific module (e.g., `modules/tech/visions-only/tech-base/`), follow the rules in the *nearest* `AGENTS.md` file. These nested rules override or extend the root instructions.
- **Module Boundaries:** Do not introduce dependencies between feature modules. All shared contracts must live in `modules/core/api` or `modules/core/spi`.
- **Hot Paths:** Adhere to the `Runtime Constitution` (no allocations in tick loops).

## Directory Structure
- `modules/core/`: Foundation and engine code.
- `modules/<category>/<baseline|visions-only>/<module>/`: Isolated feature implementations.
- `assemblies/`: Product distribution projects (Vanilla+ vs Visions).

Refer to the project documentation in `docs/` for deeper architectural mapping and performance requirements.
