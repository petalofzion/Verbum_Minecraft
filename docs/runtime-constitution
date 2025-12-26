# Runtime Constitution

## The 5 Laws of Performance for Verbum Minecraft

This document outlines the core principles and laws that govern the development of Verbum Minecraft, ensuring maximum performance (FPS/TPS) through adherence to Data-locality, Batching, and Monomorphic calls. Each law is intended to be mechanically checkable, primarily through build-time enforcement, static analysis, or automated benchmarks.

### Law 1: Allocation Minimization
    - Principle: Avoid object allocation in hot paths.
    - Rationale: Object allocations lead to garbage collection pauses, which degrade performance.
    - **Mechanically Checkable Rule:** Hot path methods (e.g., within `sim-kernel`) must pass `verbum-minecraft.no-alloc-checks` Gradle tasks without reporting allocations. Benchmark results (microbenchmarks) should show zero allocations per operation for critical loops.

### Law 2: Invalidation Control
    - Principle: Minimize cache invalidation by structuring data and logic carefully.
    - Rationale: Unnecessary cache invalidations force the CPU to fetch data from slower memory, reducing throughput.
    - **Mechanically Checkable Rule:** Specific data structures and access patterns in performance-critical modules (`sim-kernel`, `runtime`) should be reviewed to ensure optimal cache utilization. Benchmark results should show consistent performance without unexpected drops. (This is harder to automate directly at build-time, often requiring runtime profiling and benchmark analysis).

### Law 3: Ticking Strategy
    - Principle: Implement unified, batched ticking systems for similar entities/mechanisms.
    - Rationale: Centralized ticking reduces overhead, improves data locality, and allows for efficient processing of large numbers of objects.
    - **Mechanically Checkable Rule:** `BlockEntity.tick()` and `Entity.tick()` methods are forbidden in `features/*` modules (enforced via `forbidden-apis` or similar linting/static analysis configured by `verbum-minecraft.module-boundaries`). All ticking logic must be registered with and handled by the `sim-kernel`'s batched processors. Macrobenchmarks should confirm scalable ticking performance.

### Law 4: Data Locality
    - Principle: Design data structures to ensure related data is stored contiguously in memory.
    - Rationale: Maximizing data locality improves CPU cache hit rates, leading to faster access times.
    - **Mechanically Checkable Rule:** Critical data structures in `sim-kernel` and `runtime` must primarily use primitive arrays or specialized fast collections (from `runtime`) that guarantee contiguous memory. Code reviews and microbenchmarks are used to verify. (Difficult to fully automate at build-time).

### Law 5: Monomorphic Calls
    - Principle: Prefer monomorphic call sites where possible to allow the JVM to optimize method dispatches.
    - Rationale: Polymorphic calls can inhibit aggressive optimizations by the JVM, leading to slower execution.
    - **Mechanically Checkable Rule:** JIT compiler logs or specialized profiling tools should show high rates of monomorphic call sites in `sim-kernel` hot paths. Avoid excessive interface implementations or deep inheritance hierarchies in performance-critical code where virtual calls are frequent. Microbenchmarks should show consistent, optimized call performance.

---

**Note:** This document serves as a foundational guide. Specific implementation details and further elaboration on each law will be added as the project progresses. Enforcement mechanisms will be continuously refined and automated through `build-logic` convention plugins and CI/CD pipelines.