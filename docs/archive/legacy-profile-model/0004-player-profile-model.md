# ADR 0004: Player Profile Model

## Status
Superseded by ADR 0005

## Context
ADR 0002 established a two-edition model: `Vanilla+` and `Visions`.
That was a useful early split, but the project now needs a clearer long-term player-facing model that can support:

- a conservative and cozy line,
- the flagship expanded experience,
- a punitive challenge line,
- upward-only migration semantics,
- cleaner future orchestration and assembly generation.

Keeping both `Vanilla+` and `Sanctuary` as public products would create naming debt and support confusion.

## Decision
Adopt a three-profile player-facing model:

1. `Sanctuary`
2. `Visions`
3. `Purgatory`

`Sanctuary` replaces the role that had been filled by `Vanilla+`.
`Visions` remains the flagship expanded profile.
`Purgatory` is a superset profile that adds punitive difficulty and friction on top of the broader feature set.

The migration is implemented in the repo as:
- `assemblies/sanctuary`
- `assemblies/visions`
- `assemblies/purgatory`

## Consequences
- The player-facing line becomes clearer and more intentional.
- The conservative profile gets a stronger identity than the utilitarian `Vanilla+` label.
- The project avoids a four-SKU public matrix.
- Future build logic should move toward manifest-driven profile assembly generation instead of hand-maintained lists.
- Documentation must distinguish between current implementation names and the target player-facing model during the transition.

## Supersedes
This decision supersedes the player-facing naming decision in ADR 0002 while preserving its core architectural idea of build-time profile selection.
