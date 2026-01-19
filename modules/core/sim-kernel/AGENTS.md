# AGENTS.md: Guidelines for `modules/core/sim-kernel` Contributions

## Purpose
This document provides specific, high-priority guidelines for AI agents contributing to the `modules/core/sim-kernel` directory. Changes in this module directly impact the project's core performance and stability, making strict adherence to these rules critical. These guidelines augment and, where applicable, override the general rules in the root `AGENTS.md`.

## Non-Negotiables for `modules/core/sim-kernel`

*   **Hot-Path Rules:** All code within `sim-kernel`, especially within tick loops or frequently executed methods, is considered a "hot path."
*   **No Allocation in Tick Loops:** Memory allocations (`new` keyword, boxing, collection creation) are strictly forbidden within `sim-kernel`'s tick loops or any hot path.
*   **Batching Discipline:** All simulation logic must adhere to the batching discipline described in the `RUNTIME_CONSTITUTION`. Avoid per-entity/per-block-entity ticking; instead, register with and be processed by the kernel's batched systems.
*   **Monomorphic Calls:** Strive for monomorphic call sites in hot paths to enable maximum JVM optimization. Avoid unnecessary polymorphism where performance is critical.
*   **"Benchmark-or-It-Didn't-Happen":** Any change intended to improve or potentially impact performance must be accompanied by benchmark evidence.

### What Counts as a "Hot Path"?
Any code directly involved in the main simulation loop, world ticking, network processing, or rendering data processing, particularly if executed hundreds or thousands of times per tick/frame. Evidence is provided via a Spark profile or JMH numbers showing high execution counts or significant CPU time.

## Commands to Run

For any changes to `modules/core/sim-kernel`:

```bash
# Run all project builds and checks
./gradlew build

# Run unit and integration tests (if applicable to sim-kernel)
./gradlew :modules:core:sim-kernel:test
./gradlew :modules:core:sim-kernel:gametest

# REQUIRED: Execute kernel microbenchmarks
./gradlew :modules:core:sim-kernel:jmh
```

## Definition of Done for `modules/core/sim-kernel` Contributions

A contribution to `modules/core/sim-kernel` is considered "Done" when:

*   All code adheres to the "Non-Negotiables" above.
*   The project builds successfully (`./gradlew build`).
*   All relevant tests pass (`./gradlew :modules:core:sim-kernel:test`, `./gradlew :modules:core:sim-kernel:gametest`).
*   **Benchmark results (`./gradlew :modules:core:sim-kernel:jmh`) are stable or show improvement** for affected hot paths. No regressions are acceptable without explicit, high-level approval and a clear rationale documented in an ADR.
*   A brief summary of benchmark results (before/after) is included in the Pull Request or commit message.
*   If the change is significant, an updated Spark profile or JMH numbers with an explicit environment declaration (CPU/GPU/RAM/OS/Java) is provided as evidence.
*   An ADR is created if the change significantly alters core kernel architecture or performance contracts.
