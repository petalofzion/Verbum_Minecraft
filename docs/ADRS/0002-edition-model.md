# ADR 0002: Tiered Edition Build Model

## Status
Accepted

## Context
We want to support a conservative "Vanilla+" experience and a full "Total Conversion" without maintaining two separate codebases.

## Decision
Implement a **Tiered Build Model** using separate assembly projects:
1. **Verbum: Vanilla+**: Includes baseline QoL and core features.
2. **Verbum: Visions**: A superset including all Vanilla+ features plus high-tech, magic, and world-gen expansions.

## Consequences
- Single codebase with clear module boundaries.
- Build-time feature selection prevents world-breaking "missing registry" issues that runtime toggles can cause.
- Separate artifacts (`verbum-vanilla.jar` vs `verbum-visions.jar`) make player choice explicit.
