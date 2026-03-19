# ADR 0001: Minecraft Target and Mapping Strategy

## Status
Accepted

## Context
Verbum Minecraft needs a current platform baseline that matches the active Vista-aligned toolchain and keeps the repo on Mojang mappings. Migrating to Minecraft 26.1-pre-3 also requires moving the build to Java 25 and updating the Loom/Fabric API stack for the unobfuscated 26.1 snapshot line.

## Decision
Target **Minecraft 26.1-pre-3** using official **Mojang mappings**.

## Consequences
- Better alignment with Mojang's internal structure.
- Smoother transitions to future Minecraft versions (2026+).
- Requires Java 25 and the 26.1-era Loom/Fabric build configuration.
