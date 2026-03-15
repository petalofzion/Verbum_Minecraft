# Feature Packet Example

This is an example of a filled-out orchestrator packet for a feature task in Verbum.

Use it as a model when the task involves real implementation work, likely multiple capsules, and possible wiring/integration follow-through.

```md
# ORCHESTRATOR PACKET

## Assumed agent role
repo_agent

## Packet type
feature

## Task
Implement the first real Vocations gameplay layer for kitchen-garden play

## Mission
Add the first actual Vocations-only gameplay layer above Veritas by creating a small, coherent kitchen-garden feature set that supports calm daily-life play. The result should feel useful and grounded, fit the Vocations profile identity, and integrate cleanly into the existing capsule architecture without introducing cross-feature shortcuts.

## Product intent
- Player-facing purpose:
  Give Vocations players their first real profile-specific gameplay loop beyond manuals by introducing small-scale domestic cultivation and household craft.
- Owning profile:
  Vocations
- Module edition target:
  vocations
- Progression / gameplay role:
  Early-to-mid calm loop built around tending, harvesting, and simple domestic preparation.
- Tone / style constraints:
  Pastoral, warm, practical, low-drama, useful rather than flashy.
- Non-goals:
  No questline, no combat loop, no major new worldgen system, no broad tech/magic overlap.

## Inputs
- Concept or design source:
  “First real Vocations gameplay layer” for calm farming/building/stewardship play.
- Relevant notes supplied with this packet:
  Use existing profile semantics and style bible. Prefer one or two tightly scoped capsules over a sprawling system.
- Existing repo surfaces to read first:
  - `AGENTS.md`
  - `docs/agents/REPO_AGENT.md`
  - `docs/agents/ORCHESTRATOR_QUICKSTART.md`
  - `docs/agents/ORCHESTRATION_SPEC.md`
  - `docs/UPDATE_SURFACES.md`
  - `docs/CAPSULE_INDEX.md`
- Also consult if relevant:
  - `docs/ARCHITECTURE_MAP.md`
  - `docs/CONTENT_STYLE_BIBLE.md`
  - `docs/PROFILE_MODEL.md`
  - `docs/contracts/CORE_API.md`
  - `docs/contracts/CONTRACT_INDEX.md`
  - `docs/wiring/ASSEMBLY_WIRING.md`
  - `docs/GOTCHAS.md`

## Scope
### In scope
- create the first actual Vocations gameplay capsule or capsules
- add player-facing items/content needed for the loop
- update docs and generated repo surfaces
- perform repo-agent integration and verification

### Out of scope
- large-scale farming overhaul
- custom UI framework work unless strictly necessary
- new tech or magic systems
- speculative “nice to have” content beyond the loop

### Likely touched repo areas
- `modules/features/crafting/` or `modules/features/farming/` for one new Vocations-owned capsule root
- the chosen capsule's `docs/` subtree
- `modules/modules.toml`
- `docs/CAPSULE_INDEX.*`
- `docs/TODO_INDEX.md`
- capsule-local assets and metadata, including `module.json`
- assembly-facing integration only if clearly required by current patterns

### Allowed authority
- create or update capsule code and docs
- spawn capsule agents with disjoint write scopes
- repair and integrate subagent output
- refresh generated indexes and docs required by the task
- update wiring only if clearly required by the task

### Disallowed shortcuts
- no speculative expansion beyond this packet
- no architecture rewrite unless required
- no bypassing existing contracts without justification
- no leaving generated update surfaces stale

## Autonomy policy
- Do not send interim progress updates.
- Own the full loop: inspect -> plan -> implement -> review -> repair -> verify -> repeat until done.
- Spawn subagents only when scopes are disjoint and doing so reduces integration risk.
- Review all subagent output before integrating it.
- Prefer conservative implementation when multiple valid options exist.
- Default capsule subagents to `verification_scope: capsule_local`.
- Keep repo-wide integration and final verification as repo-agent work unless a delegated task explicitly owns `repo_integration`.

## Decision budget
### You may decide without escalation
- exact capsule naming consistent with existing conventions
- whether this should be one capsule or two tightly bounded capsules
- small content wording and doc structure choices
- conservative item/content structure choices that fit current patterns

### Escalate only if
- a new long-lived cross-module contract is required
- assembly wiring or config/IO changes are required and not clearly implied
- save/schema compatibility risk appears
- there are materially different product interpretations
- legal / attribution / clean-room concerns appear
- repeated verification failure yields no new hypothesis

## Subagent strategy
### Candidate subagent slices
- capsule worker for the main Vocations kitchen-garden feature capsule
- optional capsule worker for a companion manual or small support capsule if clearly justified
- repo agent retains final integration and verification

### Shared constraints for any subagent
- bounded task packet required
- explicit `allowed_paths`
- explicit `stop_conditions`
- explicit `required_checks`
- structured final report required
- no overlapping write scopes

## Update targets
Mark each as: `<required | inspect | no>`

- `docs/CAPSULE_INDEX.md`: required
- `docs/CAPSULE_INDEX.tsv`: required
- module metadata (including `module.json`): required
- `modules/modules.toml`: required
- `docs/contracts/contract_wiring.tsv`: inspect
- `docs/contracts/CONTRACT_INDEX.md`: inspect
- `docs/wiring/ASSEMBLY_WIRING.md`: inspect
- `docs/wiring/UI_WIRING.md`: no
- `docs/TODO_INDEX.md`: required
- root `TODO.md`: inspect
- capsule `docs/TODO.md`: required
- profile / edition docs: inspect
- player-facing manuals / copy: inspect
- `docs/GOTCHAS.md`: no
- ADR: no unless architecture shifts
- benchmarks: no unless hot paths or kernel work appear
- tests / gametests: inspect
- source attribution / licenses: no unless outside permissive material is intentionally adapted

## Verification plan
### Minimum required
- `./gradlew check build`

### Additional required checks
- profile-specific assembly build(s) for touched edition(s): required
- confirm capsule boundaries remain intact
- confirm Vocations profile inclusion is correct and upward inheritance behaves as intended

### Definition of verified
- required checks passed
- touched surfaces are updated
- no known module-boundary violations remain
- profile placement and upward inheritance are correct
- final diff matches packet intent

## Stop conditions
Stop early only if:
- a required input is missing and blocks any viable implementation
- a materially new architecture seam is required and not implied
- product direction is too ambiguous to choose conservatively
- a legal / clean-room blocker appears
- repeated failure has exhausted plausible fixes

## Done means
- implementation complete
- subagent work reviewed
- integrated into the repo
- update targets handled
- required verification passed
- docs refreshed where needed
- final review completed

## Final report
Include:
- what changed
- where it changed
- which update targets were refreshed
- what verification was run
- risks / follow-ups / deferred items

## Optional appendices
### A. Feature intake
- fantasy: a quiet kitchen-garden loop for domestic life in Vocations
- loop: plant -> tend -> harvest -> prepare -> store -> repeat
- acceptance in plain English: the player should feel like Vocations now has an actual calm-life feature instead of just a name/manual layer

### B. Technical constraints
- stay within current capsule architecture
- prefer existing API/SPI patterns
- avoid new cross-module contracts unless clearly necessary

### C. Content notes
- language should feel practical, warm, and grounded
- no grand lore voice
- player-facing copy should feel like useful guidance, not exposition
```
