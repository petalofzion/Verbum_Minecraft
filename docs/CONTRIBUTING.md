# Contributing to Verbum Minecraft

This guide outlines the process for contributing to the Verbum Minecraft project. It is intended for both human developers and AI agents.

## Getting Started

### Setup Development Environment
1.  **Java 21:** Ensure you have JDK 21 installed.
2.  **Git:** Clone the repository.
3.  **IDE:** We recommend IntelliJ IDEA. Open the project as a Gradle project.
4.  **Mappings:** This project uses official Mojang mappings.

### Building the Project
```bash
./gradlew build
```

### Running the Mod
```bash
./gradlew runClient
```

## Architectural Guidelines

- **The Runtime Constitution:** All performance-critical code must adhere to the 5 Laws (No allocation in hot loops, batching, etc.). See `docs/runtime-constitution`.
- **Module Boundaries:** Features must not depend on each other. Use `modules/core/api` or `modules/core/spi` for communication.
- **Clean Room Design:** Independent implementation is required for any feature inspired by closed-source work. Document your process in `docs/clean-room-logs/`.

## Contribution Workflow

### Branching Strategy
We use **Trunk-based Development**. 
- Create short-lived feature branches: `feature/your-feature-name`.
- Merge into `main` after successful CI and review.

### Pull Request Guidelines
- All PRs must pass `./gradlew build` and `./gradlew check`.
- PRs affecting `modules/core/sim-kernel`, `modules/core/api`, or `build-logic` require at least one maintainer approval.
- Include performance evidence (JMH or Spark profiles) for any hot-path changes.

### Commit Style
We enforce **Conventional Commits**:
- `feat(category): description`
- `fix(module): description`
- `docs: description`
- `perf(kernel): description`

## Style Guides
- **Formatting:** Enforced via Checkstyle and EditorConfig. Run `./gradlew check` to verify.
- **Documentation:** Keep READMEs and AGENTS.md files up to date.

## Testing
- **Unit Tests:** Located in `src/test`.
- **Integration Tests:** Located in `tools/gametest`.
- **Performance Benchmarks:** Located in `modules/core/sim-kernel/jmh` and `tools/benchmarks`. Use `./gradlew :modules:core:sim-kernel:jmh` for microbenchmarks.