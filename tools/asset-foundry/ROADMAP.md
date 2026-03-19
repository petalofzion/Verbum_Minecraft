# Asset Foundry Roadmap

This roadmap turns the current Asset Foundry direction into a practical build order.

The tool is already usable for:
- neutral PNG analysis
- semantic templates
- recolor and relationship-preserving transforms
- multi-surface block bundles
- bounded detail replacement
- explicit repro baselines for tool fixtures

The next work should focus on making the tool faster to use, easier to inspect, and better suited to real Minecraft asset production across:
- items
- block families
- books
- tools
- player skins
- mobs
- armor layers

## Product Goal

Asset Foundry should be the default deterministic pixel-generation workflow for Minecraft assets in this repo.

That means:
- analyze any relevant PNG or PNG bundle
- expose enough structure for an AI to reason about it
- let templates define semantic edit domains
- regenerate consistent variants quickly
- support direct bounded art edits when recolor is not enough

The roadmap below is ordered by practical value to AI-guided production work, not by theoretical completeness.

## Phase 1: Inspection And Review

### Goal
Make it fast to understand what the analyzer found and what the template currently means.

### Why first
This is the main bottleneck today.
The engine is strong enough to do more work than the current review UX makes comfortable.

### Deliverables
- Better candidate overlays:
  - connected components
  - detail candidates
  - zone candidates
  - semantic pixel groups
- Filtered overlay rendering:
  - `--only component_03`
  - `--only detail_candidate_02`
  - `--only group tool_detail`
- Compact per-region reports:
  - bounds
  - pixel count
  - mean hue/value
  - texture density
  - adjacency
- Compare sheets:
  - base | generated | delta
  - per-surface compare sheets for bundles

### Acceptance criteria
- An agent can identify the right edit domain from foundry output without reading raw JSON first.
- A user can visually confirm what changed on a surface or bundle in one generated artifact.

## Phase 2: Template Refinement Workflow

### Goal
Reduce the amount of raw JSON editing needed to move from analysis to a good semantic template.

### Why second
The next practical bottleneck after inspection is patch ergonomics.
The current template model is good enough, but refinement is still too manual.

### Deliverables
- Intent-focused template patch operations:
  - rename candidate
  - merge candidates
  - split region into named groups
  - create group set
  - assign group mode
  - assign transform policy
  - create zone
- Patch preview before apply
- Minimal patch export for current template deltas
- Better validation messages when a patch references missing groups or invalid transform scopes

### Acceptance criteria
- An agent can promote analysis into a useful template with small targeted patches rather than rewriting full JSON blocks.
- Group and zone authoring becomes a short iterative loop instead of a manual document edit exercise.

## Phase 3: Detail Editing And Symbol Replacement

### Goal
Make bounded art edits safer and less brittle.

### Why third
The desk tool replacement proved the architecture works.
The next step is making that workflow reliable enough for repeated use.

### Deliverables
- Detail-group clear modes:
  - clear to base
  - clear to surrounding material
  - clear to dominant neighboring field
- Better direct art ops:
  - bounded fill
  - bounded stamp
  - outline
  - line
  - mirror
- Better background infill for removed silhouettes
- Stronger detail-edit diagnostics:
  - changed-pixel counts by detail op
  - overlay for only changed detail region

### Acceptance criteria
- An agent can remove an old symbol/tool cluster and replace it with a new one without leaving obvious silhouette remnants.
- Most tiny-art edits no longer require awkward per-pixel cleanup.

## Phase 4: Atlas Workflow

### Goal
Make large atlas textures practical, not just architecturally possible.

### Why fourth
The architecture is already ready for atlas surfaces.
What is missing is usable workflow for skins, mobs, and armor.

### Deliverables
- Atlas-zone overlays
- Better zone summaries for large surfaces
- Zone-scoped patch ops
- More atlas template examples:
  - player skin
  - one simple mob texture
  - one armor layer
- Better review artifact support for large textures

### Acceptance criteria
- An agent can inspect a skin or mob texture, identify the right zone, and apply transform or detail edits without resorting to ad hoc pixel guessing.
- Atlas templates become a normal workflow, not a proof-only path.

## Phase 5: Bulk Variant Generation

### Goal
Turn one good template into many consistent variants efficiently.

### Why fifth
Once inspection, refinement, and detail editing are solid, the next multiplier is throughput.

### Deliverables
- Batch generation from one request family:
  - multiple palettes
  - multiple transform policies
  - multiple named variant ids
- Contact-sheet preview output for batch runs
- Variant manifest summaries
- Optional dedupe guard so identical outputs are detected automatically

### Acceptance criteria
- An agent can produce a family of variants in one run and review them quickly.
- The tool becomes useful for tiered items, material sets, themed book lines, armor recolors, and block families at scale.

## Phase 6: Stronger Diagnostics

### Goal
Make the transform and validation math easier to inspect and trust.

### Why sixth
This supports everything above and reduces debugging time for subtle failures.

### Deliverables
- Per-region transform summaries:
  - source value range
  - hue/saturation summaries
  - target roles used
  - changed pixel counts
  - locked pixel counts
- More explicit validation messages for non-quantized domains
- Region-stat artifacts usable during template authoring and review

### Acceptance criteria
- When a recolor looks wrong, the operator can tell whether the issue is:
  - template scope
  - transform policy
  - palette choice
  - or direct art edits

## Guardrails

The roadmap should preserve these constraints:
- no return to family-hardcoded semantic analysis
- no large material-family simulation framework yet
- no Photoshop-like editing suite inside the tool
- no automatic repro locking for normal asset work
- keep exact reproduction checks limited to explicit baselines

## Suggested Execution Order

If this is implemented as a sequence of practical milestones, the order should be:

1. Phase 1: Inspection And Review
2. Phase 2: Template Refinement Workflow
3. Phase 3: Detail Editing And Symbol Replacement
4. Phase 4: Atlas Workflow
5. Phase 5: Bulk Variant Generation
6. Phase 6: Stronger Diagnostics

## Immediate Next Milestone

The best next milestone is:

**Inspection + refinement + compare sheets**

That should include:
- filtered candidate/group overlays
- compact per-region reports
- base/generated/delta compare sheets
- intent-focused template patch operations

This will improve both:
- the quality of future asset work
- the speed at which the AI can safely use the tool

## Success Condition

Asset Foundry is in a strong next-stage state when an AI can do this reliably:

1. analyze a vanilla texture or bundle
2. inspect candidates and existing groups quickly
3. patch the template with small intent-focused changes
4. recolor or replace detail within the right semantic domain
5. review base/generated/delta output in one pass
6. ship a good asset without ad hoc manual cleanup
