# ADR 0001: Minecraft Target and Mapping Strategy

## Status
Accepted

## Context
Verbum Minecraft needs a stable target version for its initial development. Minecraft 1.21.11 represents the final stable release of late 2025. Fabric has recommended a move to Mojang mappings for better long-term maintainability.

## Decision
Target **Minecraft 1.21.11** using official **Mojang mappings**.

## Consequences
- Better alignment with Mojang's internal structure.
- Smoother transitions to future Minecraft versions (2026+).
- Requires Fabric Loom 1.14+ for proper non-obfuscated version support.
