# CODEX REPORT - 2026-01-04

## Snapshot
- Repo state: clean working tree, branch `main` is ahead of `origin/main` by 28 commits (per `git status -sb`).
- HEAD: `61a755b` "Enforce module boundaries and add sim-kernel benchmarks" (per `git log -5 --oneline`).
- Build/test status: no commands run during this review.

## Structure and Discovery
- Top-level layout matches the documented modular monolith: `modules/`, `assemblies/`, `docs/`, `tools/`, `build-logic/`, plus Gradle files.
- Module discovery is recursive and only includes folders with both `build.gradle` and `module.json` (see `settings.gradle`).
- `tools/` are currently not included in discovery (explicitly commented out in `settings.gradle`).

## Implemented Components (Current)
- Core API: minimal content/energy/fluid interfaces and records (see `modules/core/api/src/main/java/...`).
- Core SPI: `FeatureEntrypoint` only (see `modules/core/spi/src/main/java/...`).
- Runtime: `FeatureConfig` stub loads toggles but no file-backed config yet (see `modules/core/runtime/src/main/java/...`).
- Sim-kernel: only JMH benchmark stub present; no main kernel code yet (see `modules/core/sim-kernel/src/jmh/java/...`).
- UX framework: placeholder module only (no source under `modules/core/ux-framework`).
- Baseline core feature: `CoreFeature` entrypoint prints to stdout (see `modules/core/baseline/feature-core/...`).
- Feature capsule: Bible feature registers an item, has SPI registration (see `modules/features/library/bible/...`).
- Assemblies: Vanilla+ and Visions wire up ServiceLoader-based feature discovery and content registration (see `assemblies/vanilla-plus/...` and `assemblies/visions/...`).
- Tests: no `src/test` or `tools/gametest` content found.

## Notable Gaps and Inconsistencies (Clarify / Reconsider / Double-Check)
- Doc structure mismatch: `WORKFLOW.md` and several `AGENTS.md` refer to `modules/api`, `modules/sim-kernel`, and `modules/assembly`, but actual paths are `modules/core/api`, `modules/core/sim-kernel`, and `assemblies/`.
- Edition naming mismatch: docs use "Vanilla+"/"Visions", module metadata uses `baseline`/`visions` and one module uses `vanilla` (see `modules/**/module.json`, `docs/ARCHITECTURE_MAP.md`, `README.md`, and `modules/modules.toml`).
- `modules/modules.toml` does not list `modules:features:library:bible` even though assemblies depend on it.
- Benchmarks references are missing: `README.md` points to `tools/benchmarks/README.md` and `tools/benchmarks/worlds/verbum-bench-seed`, but `tools/benchmarks/` currently only has an `AGENTS.md`.
- Mapping inconsistency: `docs/CONTRIBUTING.md` says official Mojang mappings, but `docs/TARGETS.md` and `gradle.properties` specify Yarn.
- API mismatch in feature init: `FeatureContext` exposes only `content()`, but `BibleFeature` includes a TODO referencing `ctx.kernel()` (see `modules/core/api/src/main/java/...` and `modules/features/library/bible/...`).
- Runtime constitution vs implementation: `docs/ARCHITECTURE_MAP.md` forbids allocations in `modules/core/runtime`, but `FeatureConfig` uses `HashMap` and prints to stdout.
- Feature capsule hygiene: `modules/features/library/bible/` lacks a nested `AGENTS.md` and capsule `README.md` as required by `WORKFLOW.md`.
- Portability: `gradle.properties` hard-codes `org.gradle.java.home` to a local path; confirm whether this should stay in repo.
- Content registration TODOs: both assemblies still need creative tab mapping for `ItemDef.creativeTabKey` (see `assemblies/*/registry/MinecraftContentRegistrar.java`).

## Items to Address Before Moving Forward
1) Resolve naming/structure inconsistencies across `README.md`, `docs/ARCHITECTURE_MAP.md`, `WORKFLOW.md`, and module metadata (`module.json`, `modules/modules.toml`).
2) Decide canonical edition labels (baseline vs vanilla vs vanilla-plus) and update metadata/docs accordingly.
3) Align mapping documentation: confirm Mojang vs Yarn, then update `docs/CONTRIBUTING.md` or `gradle.properties`/`docs/TARGETS.md` as needed.
4) Add or update `tools/benchmarks` documentation and baseline assets, or remove references until ready.
5) Add required capsule docs (`AGENTS.md`, `README.md`) under `modules/features/library/bible/` per workflow rules.
6) Clarify Feature API shape: if kernel access is intended during `init()`, add it to `FeatureContext`; otherwise remove the TODO and document the intended pattern.
7) Decide whether runtime allocations are allowed in `modules/core/runtime` or relax the rule in `docs/ARCHITECTURE_MAP.md`.
8) Add tests (unit/gametest) scaffolding or explicitly document that tests are deferred for the vertical slice.
9) Implement creative tab mapping or redefine `ItemDef.creativeTabKey` so the registration pipeline is complete.

