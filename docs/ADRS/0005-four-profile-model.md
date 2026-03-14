# ADR 0005: Four-Profile Player Model

## Status
Accepted

## Context
ADR 0004 moved the project away from the original `Vanilla+ / Visions` split and into a stronger player-facing naming system.
That simplified the product line, but it also collapsed two different intents into one conservative profile:

- a refined Vanilla+ baseline,
- and a broader cozy / slow-life line.

Those are not the same design target.
The project now needs room for:

- a minimal truth-to-vanilla baseline,
- a cozy and expansive lifestyle line,
- the flagship full experience,
- and a brutal challenge line,
- while preserving upward-only migration semantics.

## Decision
Adopt a four-profile player-facing model:

1. `Veritas`
2. `Votum`
3. `Visions`
4. `Vorago`

Semantics:
- `Veritas` is the refined Vanilla+ baseline.
- `Votum` is the cozy and expansive profile.
- `Visions` is the flagship full profile.
- `Vorago` is the punitive challenge profile.

The migration is implemented in the repo as:
- `assemblies/veritas`
- `assemblies/votum`
- `assemblies/visions`
- `assemblies/vorago`

Compatibility direction:
- `Veritas -> Votum -> Visions -> Vorago`

Metadata guidance:
- shared modules use `shared`
- Votum-layer modules use `votum`
- Visions-layer modules use `visions`
- Vorago-layer modules use `vorago`

## Consequences
- The product line can distinguish "minimal" from "cozy" without muddy naming.
- The alliterative progression gives the profiles a stronger identity and clearer thematic ladder.
- Upward migration semantics remain simple.
- The repo can add cozy-only and challenge-only modules later without renaming the public line again.
- Until profile-specific modules land, some assemblies may temporarily share the same module set while still serving as stable public targets.

## Supersedes
This decision supersedes ADR 0004 while preserving the build-time profile-selection model established in ADR 0002.
