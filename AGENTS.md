# AGENTS.md: Guidelines for AI Agent Contributions to Verbum Minecraft

This document provides a consolidated set of guidelines and a structured workflow specifically tailored for Artificial Intelligence (AI) agents contributing to the Verbum Minecraft project. Our goal is to ensure that AI-driven development adheres to the project's strict architectural principles, performance contracts, and clean-room policy, enabling frictionless and non-destructive contributions.

This file is written for agentic coding tools (Copilot coding agent, Codex-style CLI agents, etc.). For directory-specific rules, this repo uses **nested `AGENTS.md`** files that override or extend these root instructions for specific modules.

## 🤖 AI Agent Mission

Your primary mission is to contribute code that enhances Verbum Minecraft while strictly upholding its **Runtime Constitution**, **Performance Contracts**, and **Architectural Map**. Every change must contribute positively to the project's goals of maximum FPS/TPS, stability, and maintainability.

## 🚦 Capsule Agent Quick Start (Siloed Work)
First decide your role:
- **Capsule agent (feature/mod logic)**: read `docs/agents/CAPSULE_AGENT.md` and do **not** read repo‑agent docs.
- **Repo agent (wiring/orchestration)**: read `docs/agents/REPO_AGENT.md` and follow the broader workflow.

If you are assigned to a capsule, follow the funnel in `FUNNELING.md`. It tells you exactly where to go, what to read, and where to log issues without hunting through the repo.

## ✅ Role Decision Helper (Read This First)
Use this quick test:
- If you only touch `modules/features/<domain>/<feature>/`, you are a **Capsule Agent**.
- If you touch `assemblies/*`, `modules/core/*`, or cross‑module contracts, you are a **Repo Agent**.

If you are tasked with implementing a feature/mod or fixing a bug within a single in‑game feature, you are most likely a **Capsule Agent**.
If you are tasked with wiring, integration, cross‑module contracts, or system‑wide changes, you are most likely a **Repo Agent**.
If unsure, **ask the user/orchestrator for clarification before proceeding**—do not hunt the repo to decide your role.

## 🧰 Setup & Golden Commands (Run These)

Agents should prefer reproducible, one-command checks. When in doubt, run the superset:

- **Build + unit/integration checks:** `./gradlew build`
- **Style/lint gates:** `./gradlew check`
- **Dev runs:** `./gradlew runClient` / `./gradlew runServer`
- **Kernel microbenchmarks (JMH):** `./gradlew :modules:core:sim-kernel:jmh`

If you touched anything performance-critical, include the exact commands you ran (and results summary) in your PR description / final report.

## 📖 Essential Pre-Computation (Before Coding)

### Capsule Agents (siloed feature work)
If you are assigned to a capsule, **do not** read the entire repo. Follow the funnel:

1. **[FUNNELING.md](FUNNELING.md)** (capsule onboarding and stop conditions).
2. **Nearest capsule `AGENTS.md`** (local rules and commands).
3. **[docs/ARCHITECTURE_MAP.md](docs/ARCHITECTURE_MAP.md)** (module boundaries).
4. **[docs/runtime-constitution.md](docs/runtime-constitution.md)** (performance laws).
5. **[docs/contracts/CORE_API.md](docs/contracts/CORE_API.md)** (available contracts).
6. **[docs/contracts/CONTRACT_INDEX.md](docs/contracts/CONTRACT_INDEX.md)** (wiring coverage).
7. Capsule docs: `README.md`, `docs/PRD.md`, `docs/MVP.md`, `docs/TODO.md`, `docs/agent-logs/`.

### Repo Agents (wiring, orchestration, cross-module)
Repo agents must read broader documentation before working:

1. **[README.md](README.md)** (mission + architecture overview).
2. **[WORKFLOW.md](WORKFLOW.md)** (multi-agent flow + capsule rules).
3. **[FUNNELING.md](FUNNELING.md)** (capsule constraints and stop conditions).
4. **[docs/ARCHITECTURE_MAP.md](docs/ARCHITECTURE_MAP.md)** (boundaries and allowed deps).
5. **[docs/runtime-constitution.md](docs/runtime-constitution.md)** (performance laws).
6. **[docs/contracts/CORE_API.md](docs/contracts/CORE_API.md)** (available contracts).
7. **[docs/wiring/ASSEMBLY_WIRING.md](docs/wiring/ASSEMBLY_WIRING.md)** (wiring map).
8. **[docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)** (style/testing workflow).
9. **[CODEOWNERS](CODEOWNERS)** (ownership).
10. **[TODO.md](TODO.md)** and **[docs/TODO_INDEX.md](docs/TODO_INDEX.md)** (coordination).
11. **Nearest `AGENTS.md`** for any module you touch.

Repo agents are responsible for maintaining `TODO.md`, `docs/TODO_INDEX.md`, and the contract wiring index (`docs/contracts/contract_wiring.tsv` → `docs/contracts/CONTRACT_INDEX.md`).

## ⚖️ AI Agent Rules (Non-Negotiable - from README)

These are explicit rules reiterated from the `README.md` that you, as an AI agent, **must** follow:

1.  Read **docs/ARCHITECTURE_MAP.md** first.
2.  **Never** place simulation logic in `modules/<category>/...`.
3.  Any change to kernel hot paths requires:
    *   a benchmark update (`tools/benchmarks` or JMH), and
    *   a short ADR if it changes architecture.
4.  If you need cross-feature communication, add contracts in `modules/core/api` (or `modules/core/spi` if internal).
5.  Do not import between feature modules. Ever.

## 🛡️ Clean Room & Legal Policy Adherence

*   **Strict Clean Room Policy:** You **MUST NOT** use decompiled code from closed-source mods or assets ripped from other projects as a reference for any contribution.
*   **Contribution Declaration:** Every contribution implicitly affirms that no such forbidden materials were used.
*   **Attribution:** If adapting permissive open-source code/designs, make an entry in `SOURCE_ATTRIBUTION.md` and copy the license to `LICENSES/`.
*   **ADRs:** For any new subsystem or significant architectural change, create an ADR in `docs/ADRS/`.

## 🔒 Restricted Areas (Ask First)

These areas have high blast radius. Do not change them unless the task explicitly requires it:

- `build-logic/` (Gradle convention plugins)
- Root Gradle wiring (`settings.gradle`, root `build.gradle`)
- Mixin configs and access wideners
- Licensing / attribution files
- Public API contracts (`modules/core/api`)

## 📈 Performance-First Mandate

*   **Performance Contract:** Every performance-critical change **must** consider the goals defined in the `## 📈 Performance Contract (Verifiable)` section of `README.md`.
*   **Optimization Discipline:** Prioritize data locality, batching, and monomorphic calls. Avoid allocations in hot loops.
*   **Testing:** Automatically generate or update relevant performance benchmarks.

## ✅ Definition of Done (Do Not Declare “Complete” Without This)

A change is only “done” when all applicable items are satisfied:

- [ ] The change respects module boundaries (no forbidden imports, no feature-to-feature dependencies).
- [ ] `./gradlew build` passes.
- [ ] `./gradlew check` passes (style/lint).
- [ ] Tests are added/updated if behavior changed.
- [ ] If kernel hot paths were touched: benchmarks were added/updated and results are summarized.
- [ ] Feature registration is implemented via the `FeatureEntrypoint` SPI.

## 🛠️ Feature Discovery (SPI Registration)

To register a new feature, implement `FeatureEntrypoint` and register it in `META-INF/services`.

**Example:**
1. Create `com.verbum_minecraft.feature.MyFeature implements FeatureEntrypoint`.
2. Create `src/main/resources/META-INF/services/com.verbum_minecraft.spi.FeatureEntrypoint`.
3. Add the line: `com.verbum_minecraft.feature.MyFeature`.

## 🚫 Forbidden Patterns

- **DO NOT USE `configuration: 'namedElements'`** in project dependencies. This causes variant resolution failures and breaks the multi-project build. Use standard `implementation project(':path:to:module')` instead.

## 🛠️ AI Agent Workflow (Iterative Development Cycle)

1.  **Understand & Contextualize:** Review request, docs, and codebase.
2.  **Plan:** Break down task, consider performance/architecture, identify tests.
3.  **Implement:** Adhere to project style and rules. Register features via SPI.
4.  **Test:** Run unit/integration tests and benchmarks.
5.  **Verify:** Ensure all project checks pass.
6.  **Finalize:** Commit changes and provide a final report.
