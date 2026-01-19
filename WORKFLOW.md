# Verbum Multi-Agent Workflow & Repo Organization
**Copy-paste doc — single source of truth for how we build Verbum with parallel AI agents without breaking things.**

This document defines:
1) how the repo is organized (tiers/modules/editions),
2) how new features are added as “capsules” 🪽,
3) how we run an async multi-agent swarm in parallel safely (minimal dependency hunting, minimal merge conflicts, high confidence).

For capsule onboarding, start with `FUNNELING.md` and follow its steps. For role-specific rules, see `docs/agents/CAPSULE_AGENT.md` and `docs/agents/REPO_AGENT.md`. For available contracts and wiring, see `docs/contracts/CORE_API.md`, `docs/contracts/CONTRACT_INDEX.md`, and `docs/wiring/ASSEMBLY_WIRING.md`.

---

## 0) Core Idea (One sentence)
**One Fabric/Loom runtime + one modular monolith repo + many isolated feature capsules + strict contracts + edition gating + CI/bench evidence.**

---

## 1) The Two Axes of Organization
### Axis A — **Runtime Tiers (performance + dependency firewalls)**
We separate the codebase into tiers so content never pollutes hot loops:

- **Tier 0: `modules/core/api`**
  - Pure interfaces/types/contracts/enums.
  - No logic, no Minecraft side effects.
  - Stable, shared vocabulary.

- **Tier 1: `modules/core/sim-kernel`**
  - Hot paths (batched ticking, data-local arrays, monomorphic call sites).
  - Owns performance budgets.
  - Does not depend on feature modules.

- **Tier 1.5: `modules/core/ux-framework`**
  - Shared UI primitives and rendering helpers.
  - Performance-aware, but not kernel-hot.

- **Tier 2: `modules/features/*`**
  - “Content capsules” (registration + data + feature logic).
  - Must not contain simulation loops that scale with world size unless routed through kernel.

- **Tier 3: `assemblies`**
  - The entrypoint wiring.
  - Builds the final mod artifact and loads enabled features.

- **Verification Layer: `tools/*`**
  - Datagen, gametests, benchmark harness, baseline worlds, measurement protocol.

### Axis B — **Editions (what ships)**
Editions decide which features are included:

- **Verbum Vanilla+**
  - Minimal, “vanilla-adjacent,” low-intrusion features.
- **Verbum Visions (Expanded)**
  - Superset edition (adds larger systems).

**Important:** Editions are **build/distribution concerns**, not separate repos.

---

## 2) Why This Enables Swarms
A multi-agent swarm is safe when:
- every agent has a strict, small “blast radius” (a capsule folder),
- cross-capsule communication is done only via stable contracts (`modules/core/api`),
- hot path edits are gated by benchmarks and extra review,
- edition wiring avoids one shared “registry file” that everyone edits.

This is “organizational concurrency control.”

---

## 3) Feature Capsules 🪽 (the unit of parallel work)
A **feature capsule** is the smallest unit that can be implemented by one agent without hunting dependencies.

### Feature capsule rules
- Must live under a single directory.
- Must not import from other features.
- May depend on:
  - `modules/core/api`
  - optionally `modules/core/sim-kernel` and/or `modules/core/ux-framework`
- Must be enable/disable-able at the edition/build level.
- Must carry its own:
  - minimal docs
  - tests (or test plan)
  - config keys (if applicable)
  - agent logs for questions/decisions
  - capsule TODO

### Recommended capsule directory layout
Example: `modules/features/library/bible/`

```

modules/features/library/bible/
├── AGENTS.md                         # nested rules for THIS capsule
├── README.md                         # capsule spec summary / constraints
├── module.json                       # machine-readable metadata
├── docs/                             # PRD/MVP/agent logs (capsule-local)
│   ├── TODO.md                        # capsule-specific tasks
├── src/main/java/...                 # implementation
├── src/main/resources/...            # assets, book data, lang, etc.
├── src/test/java/...                 # unit tests (if applicable)
└── src/gametest/java/...             # integration/gametest (if applicable)
```

**Nested `AGENTS.md` and `module.json` are mandatory for swarm work.**

### `module.json` Fields:
- `id`: unique module identifier.
- `domain`: core/qol/world/magic/tech/ui/etc.
- `edition`: vanilla-plus/visions.
- `providesFeature`: boolean (true if it implements `FeatureEntrypoint`).
- `entrypointClass`: FQCN of the `FeatureEntrypoint` implementation (optional).
- `dependsOn`: list of module IDs.

---

## 4) Adding a New Feature (the standard pipeline)
### Step 1 — PRD / Spec Sheet (human or “spec agent”)
Create one doc per feature **inside the capsule** (use templates in `docs/templates/`), containing:
- Purpose + non-goals
- User stories
- Data model (save schema impacts)
- Performance notes (hot path? yes/no)
- Edition target (Vanilla+ / Visions / both)
- Test plan + benchmark needs
- API needs (new contracts in `modules/core/api`?)

### Step 2 — Scaffold the capsule (repo agent)
Repo agent creates the folder layout and stubs (see `docs/templates/capsule/` and `docs/checklists/new-feature.md`):
- `modules/features/<domain>/<feature>/...`
- nested `AGENTS.md`
- capsule `README.md`
 - capsule `docs/PRD.md` and `docs/MVP.md`
 - capsule `docs/agent-logs/README.md`
- optional test skeleton
- optional “feature manifest” (see Section 6)

### Step 3 — Assign the capsule to an implementation agent (swarm)
Each agent is told:
- the PRD link/path
- the **exact allowed directories**
- the commands they must run before finishing
- what evidence to report

### Step 4 — Implementation + local verification
Agent implements inside the capsule only, then runs:
- `./gradlew build`
- `./gradlew check`
- plus any capsule-specific tests
- plus benchmarks if kernel-hot paths were touched

### Step 5 — Review + merge (repo agent)
Repo agent checks:
- directory constraints were respected
- no forbidden imports
- edition wiring is correct
- test/benchmark evidence exists
- ADRs/attribution updated if required

---

## 5) Async Multi-Agent Swarm Protocol (Parallel Work Without Breakage)
### 5.1 Swarm prerequisites
To run N agents at once, we enforce:
- **Strict folder ownership**: each agent only touches its capsule folder (and optionally a designated “contract PR” if API changes are required).
- **No shared wiring file** edits by multiple agents (avoid merge wars).
- **CI gates**: every PR must pass `build` + `check`.

### 5.2 Branch/PR conventions
Use one branch per capsule:
- `feat/<domain>-<feature>`
- `fix/<domain>-<feature>`

Each PR includes a final report:
- what changed
- files touched
- commands run
- results summary
- any risks/follow-ups

### 5.3 Dependency hunting is forbidden (replace with contracts)
If a feature needs something from another feature:
- DO NOT import it.
- Add a contract to `modules/core/api` (or `modules/core/spi` if internal).
- Implement provider/consumer via kernel/service/lookup rather than direct imports.

### 5.4 “Two-Phase” cross-module changes (to avoid swarm coupling)
When multiple features need new contracts, do it in two PR phases:

**Phase A (Contracts PR):**
- Add interfaces/types in `modules/core/api` only.
- No feature logic.
- Merged early.

**Phase B (Feature PRs):**
- Each feature implements against the new contracts inside its own capsule.

This avoids ten agents editing `modules/core/api` simultaneously.

---

## 6) Wiring Features Without Merge Conflicts (No central mega-file)
Central “list of features” files cause merge conflicts during swarms.
Prefer **discovery-based wiring**.

### Recommended wiring pattern: “Feature Entry” + discovery
Each capsule provides a small entrypoint class, e.g.:
- `com.verbum.features.library.bible.BibleFeatureEntry implements VerbumFeature`

Then `assemblies` discovers feature entries at runtime using one of:
- **ServiceLoader** (Java SPI)
- a build-time generated index
- a resource manifest per module merged at build

**Goal:** each capsule can add itself without editing one shared file.

> Note: If discovery is not implemented yet, use a temporary central registry but treat it as a merge hotspot:
> - only the repo agent edits it
> - feature agents never touch it

**Assembly responsibility:** Only `assemblies/*` should touch Fabric/Minecraft APIs, config/IO, and registry wiring. Capsules remain pure logic/data and register via API/SPI.

---

## 7) Edition Gating vs Runtime Toggles (Safety)
### 7.1 Edition gating (build-time, safest)
Use editions to include/exclude entire capsules:
- Vanilla+ includes a curated set
- Visions includes superset

This avoids world corruption from removing registries.

### 7.2 Runtime toggles (config, safe only for behavior)
Runtime config can disable:
- behaviors (ticks routed through kernel)
- recipe availability
- worldgen knobs (ideally world-creation only)
- UI features

Runtime config MUST NOT:
- unregister blocks/items/entities from a world that already used them
- remove registry entries post-save

**Rule of thumb:**
- “Removing content” = edition/build concern
- “Disabling behavior” = runtime config concern

**Feature toggle wiring:** Config/IO lives in `assemblies/*` only. Assemblies load toggles at startup and pass precomputed, allocation-free data into hot paths. Capsules remain pure logic/data and do not read config or touch Fabric/Minecraft APIs.

---

## 8) Kernel Hot Path Rule (special handling)
If a capsule touches `modules/core/sim-kernel` or introduces kernel workloads:
- it must include benchmark changes (JMH and/or baseline world scenario)
- it must summarize results in the PR report
- it should include an ADR if architecture shifts

Hot path changes are the only class of change that may require extra review before merge.

---

## 9) Nested `AGENTS.md` (the enforcement mechanism)
Root `AGENTS.md` defines repo-wide rules.
Nested `AGENTS.md` defines capsule/module rules.

### Priority rule
When editing a file:
- the **closest** `AGENTS.md` in the directory tree is highest priority
- root rules still apply unless explicitly overridden by stricter local rules

### Recommended nested files to add (as repo grow)
- `modules/core/sim-kernel/AGENTS.md` (hot-path + benchmarking)
- `modules/core/api/AGENTS.md` (API stability + deprecation discipline)
- `tools/benchmarks/AGENTS.md` (measurement protocol)
- `modules/features/<domain>/<feature>/AGENTS.md` (capsule scope + “do not edit outside”)

---

## 10) Repo Agent Checklist (merge gate)
Before merging any feature PR:

**Scope**
- [ ] PR touches only allowed paths (capsule folder; no drive-by edits)
- [ ] No forbidden imports (feature-to-feature)

**Build**
- [ ] `./gradlew build` passes
- [ ] `./gradlew check` passes

**Performance**
- [ ] If kernel touched: benchmark evidence included
- [ ] No allocations in hot loops introduced

**Docs / Legal**
- [ ] ADR added if architecture changed
- [ ] Attribution + licenses recorded if open-source adapted
- [ ] Save data impact documented + migration path if needed

---

## 11) Example: “Bible as a Book” capsule placement
Feature goal: overhaul books and add a full Bible experience.

Recommended placement:
- Domain module: `modules/features/library/`
- Capsule: `modules/features/library/bible/`

Why:
- book UX + text store + styling belongs to “library” domain
- later book features (manuals, grimoires, indexing, shelves) extend the same domain without new scaffolding

If “book overhaul” becomes large, split within the domain by capsules:
- `library/book-core/` (shared book engine)
- `library/bible/`
- `library/manuals/`
- `library/library-blocks/`

Each is swarm-friendly.

---

## 12) What We Do NOT Do (anti-patterns)
- ❌ “Subrepos per feature” by default (too much friction)
- ❌ Feature-to-feature imports
- ❌ Ten agents editing the same registry/wiring file
- ❌ Runtime toggles that remove already-used registries
- ❌ Kernel logic inside `modules/features/*`

---

## 13) Optional Enhancements (to implement later)
These are recommended but not required on day 1:

- A `tools/scaffold` generator:
  - creates capsule folders + nested AGENTS.md + skeleton tests + manifest
- CI job that rejects PRs touching forbidden paths for a capsule
- Static dependency rules (archunit/custom Gradle check) enforcing tier boundaries
- Automated benchmark regression checks for sim-kernel

---

## 14) One-liner Summary
**Specs create capsules. Capsules isolate agents. Contracts eliminate dependency hunting. Editions control what ships. Benchmarks guard hot paths.**
