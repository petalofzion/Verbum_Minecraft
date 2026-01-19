# ADR 0003: Decentralized Feature Discovery (SPI)

## Status
Accepted

## Context
A "swarm" of AI agents contributing features simultaneously would cause constant merge conflicts if all features had to be registered in a single central registry file.

## Decision
Use Java's **ServiceLoader (SPI)** mechanism for feature discovery.
- Define a `FeatureEntrypoint` interface in `modules/core/spi`.
- Each feature module implements this interface and provides a `META-INF/services/com.verbum_minecraft.spi.FeatureEntrypoint` file.
- The assembly projects discover and initialize these features at runtime.

## Consequences
- Agents can add features by only touching their own module.
- Zero merge conflicts in central wiring.
- Slight performance cost at startup (negligible).
