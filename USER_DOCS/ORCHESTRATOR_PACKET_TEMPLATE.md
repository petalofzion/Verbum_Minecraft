# Verbum Orchestrator Packet Template

This is a user-facing master packet template for handing a task to a repo-agent orchestrator.

Use this when you want the orchestrator to own the full loop:
`inspect -> plan -> dispatch -> review -> repair -> verify -> integrate -> report`

This template is intentionally aligned to Verbum's actual repo surfaces:
- `AGENTS.md`
- `docs/agents/REPO_AGENT.md`
- `docs/agents/ORCHESTRATOR_QUICKSTART.md`
- `docs/agents/ORCHESTRATION_SPEC.md`
- `docs/UPDATE_SURFACES.md`
- `docs/CAPSULE_INDEX.md`
- `docs/agents/VERIFIER_AGENT.md`

It should not restate the whole repo constitution. It should define the mission, scope, decision budget, update obligations, and stop rules clearly enough that the orchestrator can work without mid-run supervision.

---

## Recommended Use
- Fill this in as the mission wrapper.
- Attach or reference any feature intake, design notes, PRDs, or style notes separately.
- Keep the packet concrete.
- If a section is not relevant, mark it `none` instead of deleting it.

---

```md
# ORCHESTRATOR PACKET

## Assumed agent role
repo_agent

## Packet type
<feature | bugfix | refactor | spike | content>

## Task
<short imperative title>

## Mission
<one short paragraph describing what must exist when the task is fully complete>

## Seam risk
- Does this task create or change repo-level seams?
  `<yes | no>`
- If yes, split execution into:
  - repo-seam implementation packet
  - verifier packet
  - capsule implementation packet
- If no, note why:
  `<one short line>`

## Verifier gate
- `requires_verifier`: `<yes | no>`
- Why verifier signoff is or is not required:
  `<one short line>`
- Closeout rule:
  If `requires_verifier` is `yes`, do not report `done` until verifier evidence exists and the done gate is satisfied.

## Product intent
- Player-facing purpose:
- Owning profile:
  <Veritas | Vocations | Visions | Vorago | multiple>
- Module edition target:
  <veritas | vocations | visions | vorago | shared | mixed>
- Progression / gameplay role:
- Tone / style constraints:
- Non-goals:

## Inputs
- Concept or design source:
- Relevant notes supplied with this packet:
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
  - `docs/agents/VERIFIER_AGENT.md`

## Scope
### In scope
- ...

### Out of scope
- ...

### Likely touched repo areas
- ...

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
- Do not report `done` if verifier signoff is required and still missing.

## Decision budget
### You may decide without escalation
- internal naming and file layout consistent with repo conventions
- conservative use of existing contracts and patterns
- capsule-local implementation details
- small copy/details consistent with profile and style rules
- modest test/doc structure choices

### Escalate only if
- a new long-lived cross-module contract is required
- assembly wiring or config/IO changes are required and not clearly implied
- save/schema compatibility risk appears
- there are materially different product interpretations
- legal / attribution / clean-room concerns appear
- repeated verification failure yields no new hypothesis

## Subagent strategy
### Candidate subagent slices
- ...

### Shared constraints for any subagent
- bounded task packet required
- explicit `allowed_paths`
- explicit `stop_conditions`
- explicit `required_checks`
- structured final report required
- no overlapping write scopes

### Verifier use
- add a verifier pass after assembly or `modules/core/api/*` seam changes
- verifier agents diagnose and report; they do not silently take over implementation
- if `requires_verifier` is `yes`, verifier evidence is mandatory for closeout

## Update targets
Mark each as: `<required | inspect | no>`

- `docs/CAPSULE_INDEX.md`:
- `docs/CAPSULE_INDEX.tsv`:
- module metadata (including `module.json`):
- `modules/modules.toml`:
- `docs/contracts/contract_wiring.tsv`:
- `docs/contracts/CONTRACT_INDEX.md`:
- `docs/wiring/ASSEMBLY_WIRING.md`:
- `docs/wiring/UI_WIRING.md`:
- `docs/TODO_INDEX.md`:
- root `TODO.md`:
- capsule `docs/TODO.md`:
- profile / edition docs:
- player-facing manuals / copy:
- `docs/GOTCHAS.md`:
- ADR:
- benchmarks:
- tests / gametests:
- source attribution / licenses:

## Verification plan
### Minimum required
- `./gradlew check build`

### Additional required checks
- profile-specific assembly build(s) for touched edition(s): `<required | inspect | no>`
- verifier signoff required: `<yes | no>`
- verifier packet/report must exist before closeout when required: `<yes | no>`
- targeted runtime smoke check when `assemblies/*` or `modules/core/api/*` changed: `<required | inspect | no>`
- done gate check: `python3 tools/scripts/verify_done_gate.py ...` `<required | inspect | no>`
- ...
- ...

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
<fantasy, loop, progression role, acceptance in plain English>

### B. Technical constraints
<performance, compatibility, migration, API restrictions>

### C. Content notes
<naming, style, voice, player-facing text constraints>
```

---

## Repo-Aligned Improvements Over A Generic Packet
- Uses `Owning profile` and `Module edition target` separately, because Verbum distinguishes player-facing profile identity from metadata placement.
- Uses the repo's real generated surfaces in `Update targets`.
- Assumes the orchestrator is a repo agent, not a generic agent.
- Treats subagents as bounded packet-driven workers, matching `docs/agents/ORCHESTRATION_SPEC.md`.
- Makes `Update targets` mandatory, because Verbum is trying to keep the repo's self-map accurate as code changes land.
- Keeps `./gradlew check build` as the floor, not an optional nice-to-have.

## Notes
- For capsule-only work, the orchestrator can still use this template, but should keep scope narrow and avoid repo-wide rewrites.
- For content-only tasks, keep the packet short and let `docs/CONTENT_STYLE_BIBLE.md` do most of the style lifting.
- For spike tasks, make the `Done means` section explicitly allow feasibility-only outcomes.
