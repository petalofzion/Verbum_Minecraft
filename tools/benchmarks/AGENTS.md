# AGENTS.md: Guidelines for `tools/benchmarks` Contributions

## Purpose
This document provides specific guidelines for AI agents contributing to the `tools/benchmarks` directory. This module is critical for upholding the project's performance contract by defining, executing, and verifying performance claims. Contributions here directly impact the project's ability to "turn myth into math." These guidelines augment and, where applicable, override the general rules in the root `AGENTS.md`.

## Non-Negotiables for `tools/benchmarks`

*   **Measurement Protocol:** All benchmarks must follow a clearly defined, repeatable measurement protocol (e.g., warm-up iterations, measurement iterations, number of forks).
*   **Repeatability:** Benchmarks must be deterministic and produce consistent results across identical hardware and software environments. Avoid external factors that could introduce variance.
*   **Environment Reporting:** Benchmark results must always include a clear declaration of the environment: CPU/GPU model, RAM, Operating System, Java version, and any relevant JVM flags.
*   **Baseline World Usage:** For in-game macrobenchmarks, always use the defined baseline world located at `tools/benchmarks/worlds/verbum-bench-seed`.
*   **Workload Definition:** Each benchmark must have a clearly documented workload (e.g., N machines + M transport edges + K chunk updates).
*   **Client vs. Server:** Clearly distinguish between client-side (FPS, frame times) and server-side (TPS, tick times) measurements.
*   **Evidential Capture:** Any performance claim or regression analysis requires verifiable evidence (JMH results, Spark profiles, in-game TPS/FPS recordings).

## Commands to Run

For any changes to `tools/benchmarks` or when running performance tests:

```bash
# Run kernel microbenchmarks (JMH)
./gradlew :modules:core:sim-kernel:jmh

# Build the project to ensure benchmarks are compiled
./gradlew build

# Launch a development client to manually run in-game macrobenchmarks
./gradlew runClient
```

### Running the Baseline Scenario & Capturing Evidence

1.  **Launch Client/Server:** Use `./gradlew runClient` (or `runServer`) and load `tools/benchmarks/worlds/verbum-bench-seed`.
2.  **Activate Workload:** Trigger the defined workload within the benchmark world (e.g., activate machines, simulate entity movement).
3.  **Capture Metrics:**
    *   For **TPS/Tick Time:** Use in-game profiling tools (e.g., Fabric's `/tick` command, server console output, or external profilers).
    *   For **FPS/Frametimes:** Use in-game overlay or external tools (e.g., MSI Afterburner, client-side profilers).
    *   For **Deep Analysis:** Generate a [Spark](https://modrinth.com/mod/spark) profile (`/spark profiler start` then `/spark profiler stop --upload`) during the workload execution.

## Definition of Done for `tools/benchmarks` Contributions

A contribution to `tools/benchmarks` is considered "Done" when:

*   The benchmark code itself adheres to project code style and best practices.
*   The benchmark accurately measures the intended performance aspect.
*   The benchmark is repeatable and its results are stable (low variance).
*   The environment requirements for reproducing results are clearly documented.
*   The workload being tested is precisely defined within the benchmark's documentation or accompanying `README.md`.
*   New benchmarks are integrated into the overall build/CI system if appropriate.
*   An ADR is created if the benchmark defines a new performance contract or changes how an existing one is measured.
