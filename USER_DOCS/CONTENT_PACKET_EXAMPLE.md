# Content Packet Example

This is an example of a filled-out orchestrator packet for a content/manual task in Verbum.

Use it as a model when the task is primarily books, manuals, copy, naming, guidance text, or other style-bound player-facing content.

```md
# ORCHESTRATOR PACKET

## Assumed agent role
repo_agent

## Packet type
content

## Task
Expand the existing profile manuals with clearer player-facing “about this profile” guidance

## Mission
Revise and expand the existing Verbum profile manuals so each one more clearly teaches the player what that profile is for, how it should feel, and what kind of play it invites. Keep the books practical and profile-owned, not lore-heavy, and ensure the content remains aligned to the style bible.

## Product intent
- Player-facing purpose:
  Help players immediately understand the identity of Veritas, Vocations, Visions, and Vorago through useful in-game manual text.
- Owning profile:
  multiple
- Module edition target:
  veritas, vocations, visions, vorago
- Progression / gameplay role:
  orientation, onboarding, thematic framing, practical player guidance
- Tone / style constraints:
  quiet, useful, profile-specific, more manual than lore, “whispers more often than it shouts”
- Non-goals:
  no new mechanics, no new architecture, no speculative system design

## Inputs
- Concept or design source:
  strengthen the manuals as the “about this version” layer
- Relevant notes supplied with this packet:
  use the current library/manual stack and preserve the profile ladder
- Existing repo surfaces to read first:
  - `AGENTS.md`
  - `docs/agents/REPO_AGENT.md`
  - `docs/agents/ORCHESTRATOR_QUICKSTART.md`
  - `docs/agents/ORCHESTRATION_SPEC.md`
  - `docs/UPDATE_SURFACES.md`
  - `docs/CAPSULE_INDEX.md`
- Also consult if relevant:
  - `docs/CONTENT_STYLE_BIBLE.md`
  - `docs/PROFILE_MODEL.md`
  - the existing manual capsules
  - `docs/GOTCHAS.md`

## Scope
### In scope
- update the text and supporting capsule docs for existing manuals
- improve clarity of player-facing guidance
- preserve current capsule boundaries and library-book patterns
- refresh generated indexes if purpose summaries or module metadata meaning changes

### Out of scope
- new game mechanics
- new contracts
- new assemblies
- large-scale refactors

### Likely touched repo areas
- `modules/features/library/dusty-devotional/**`
- `modules/features/library/book-of-hours/**`
- `modules/features/library/pilgrims-atlas/**`
- `modules/features/library/rule-of-ashes/**`
- `docs/CAPSULE_INDEX.*`

### Allowed authority
- update capsule-local content and docs
- spawn capsule content agents for disjoint manuals if useful
- refresh generated indexes and docs required by the task

### Disallowed shortcuts
- no change to profile semantics unless clearly intentional
- no replacing practical manual voice with lore-heavy writing
- no silent drift from the content style bible

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
- exact book wording and section structure consistent with profile identity
- moderate clarity/organization improvements
- small README/PRD/TODO sync updates

### Escalate only if
- revised content implies a real product/profile change
- a new long-lived contract or wiring path is somehow required
- there are materially different interpretations of what a profile is for
- repeated verification failure yields no new hypothesis

## Subagent strategy
### Candidate subagent slices
- one content capsule agent for `dusty-devotional`
- one for `book-of-hours`
- one for `pilgrims-atlas`
- one for `rule-of-ashes`
- repo agent retains final style pass, integration, and verification

### Shared constraints for any subagent
- bounded task packet required
- explicit `allowed_paths`
- explicit `stop_conditions`
- explicit `required_checks`
- structured final report required
- no overlapping write scopes

## Update targets
Mark each as: `<required | inspect | no>`

- `docs/CAPSULE_INDEX.md`: inspect
- `docs/CAPSULE_INDEX.tsv`: inspect
- module metadata (including `module.json`): inspect
- `modules/modules.toml`: no
- `docs/contracts/contract_wiring.tsv`: no
- `docs/contracts/CONTRACT_INDEX.md`: no
- `docs/wiring/ASSEMBLY_WIRING.md`: no
- `docs/wiring/UI_WIRING.md`: no
- `docs/TODO_INDEX.md`: inspect
- root `TODO.md`: no
- capsule `docs/TODO.md`: inspect
- profile / edition docs: inspect
- player-facing manuals / copy: required
- `docs/GOTCHAS.md`: no
- ADR: no
- benchmarks: no
- tests / gametests: no unless content structure changes require them
- source attribution / licenses: no

## Verification plan
### Minimum required
- `./gradlew check build`

### Additional required checks
- profile-specific assembly build(s) for touched edition(s): inspect
- confirm each edited book resource still matches its declared `LibraryBookDef`
- confirm profile distinction is clearer after the change

### Definition of verified
- required checks passed
- touched surfaces are updated
- no known module-boundary violations remain
- content matches packet intent and style constraints

## Stop conditions
Stop early only if:
- profile intent is too ambiguous to choose conservatively
- a legal / clean-room blocker appears
- repeated failure has exhausted plausible fixes

## Done means
- manual content updated
- capsule docs refreshed where needed
- subagent work reviewed
- update targets handled
- required verification passed
- final content pass completed

## Final report
Include:
- what changed
- which manuals changed
- which update targets were refreshed
- what verification was run
- remaining follow-ups or intentional deferrals

## Optional appendices
### A. Feature intake
- acceptance in plain English: each profile manual should better answer “what is this version for?” without becoming preachy or bloated

### B. Technical constraints
- preserve existing library-book id/resource naming rules
- avoid introducing new mechanical dependencies

### C. Content notes
- Veritas: plain, grounded, foundational
- Vocations: warm, pastoral, domestic, useful
- Visions: expansive, learned, exploratory
- Vorago: severe, disciplined, practical under pressure
```
