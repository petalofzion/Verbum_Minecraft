# Asset Foundry Next Steps Spec

This document captures the obvious next improvements for `tools/asset-foundry` now that the core
Analyze -> Label -> Transform workflow is working for:
- single-surface item textures
- multi-surface block bundles
- bounded detail replacement
- atlas-ready family/template architecture

The purpose of this document is not to redefine the tool.
It is to identify the next practical improvements that would make Asset Foundry substantially more useful
for real Minecraft asset work across items, blocks, skins, mobs, armor, and future texture families.

The audience is:
- AI agents using the foundry
- humans authoring or reviewing templates
- future orchestrators deciding what to build next

## Guiding Principle

Asset Foundry should behave like a **pixel compiler for Minecraft assets**:
- input: one or more base PNGs
- analysis: neutral pixel facts
- template: semantic regions and rules
- transform: deterministic recolor and detail edits
- output: Minecraft-ready textures and bundles

The next improvements should strengthen that workflow without turning the tool into:
- a family-hardcoded art bot
- a Photoshop clone
- an over-abstract material simulator

The right bias remains:
- generic
- inspectable
- deterministic
- useful for AI-guided production work

## 1. Region And Cluster Inspection UX

### Why it matters
The current analysis data is already powerful enough to support useful reasoning, but it is still awkward to inspect quickly.

When an AI or human needs to answer:
- where is the saw
- which cluster is the page edge
- which pixels form the trim
- which candidate overlaps the eye region

the data is available, but the review ergonomics are still rough.

### What should improve
- better analysis overlays with clearer labels
- easier mapping from candidate ids to visible image locations
- overlays for:
  - connected components
  - detail candidates
  - semantic pixel groups
  - transform domains
- easier preview of only one selected group or candidate at a time
- text-friendly coordinate summaries for tiny assets

### Concrete ideas
- add a `render-candidate-overlay` command
- add per-candidate legend text in overlay output
- add filtered overlays:
  - `--only component_03`
  - `--only detail_candidate_02`
  - `--only group tool_detail`
- add a compact report:
  - pixel count
  - bounds
  - average hue/value
  - touching/adjacent groups

### Why this helps AI specifically
This reduces the gap between:
- “the analysis exists”
and
- “the AI can confidently choose the right pixels to edit”

It makes the reasoning loop much faster and less error-prone.

## 2. Template Patch Authoring Ergonomics

### Why it matters
The current template system is correct in principle, but editing templates can still be too JSON-heavy.

That becomes painful for:
- large block families
- complex item silhouettes
- atlas surfaces with many regions

### What should improve
- easier patch-based editing of semantic groups and zones
- smaller patch files focused on intent rather than full structure
- better merge/split/rename workflows

### Concrete ideas
- support a dedicated patch shape for:
  - rename candidate
  - merge candidates
  - split candidate into named semantic groups
  - set group mode
  - set transform policy
  - create group set
  - create zone
- add validation and preview for patches before applying them
- add a command that prints the minimal patch needed to change a group

### Why this helps AI specifically
The AI should be spending effort on:
- interpreting asset structure
- deciding what should be editable
- choosing transform policy

not on hand-editing large repetitive JSON blocks.

## 3. Compare Sheets And Review Surfaces

### Why it matters
Right now delta images and previews exist, but review is still fragmented.

For real use, the operator often wants:
- base
- generated
- delta
- maybe group overlay

in one place.

### What should improve
- side-by-side review artifacts
- per-surface compare sheets for bundle outputs
- contact sheets for bulk variants

### Concrete ideas
- generate a compare strip:
  - base | generated | delta
- generate per-bundle compare sheets:
  - front, side, top
- generate small manifest-linked review HTML or markdown summaries later if useful

### Why this helps AI specifically
This makes it much easier to notice:
- tool silhouettes that still survive
- recolor flattening
- unintended spread outside the semantic region

without repeated manual inspection.

## 4. Atlas-Specific Helpers

### Why it matters
Minecraft textures are not only icons and block faces.

The tool needs to support:
- player skins
- mob textures
- armor layers
- other atlas-style textures

The current architecture is ready, but the workflow is still thin.

### What should improve
- better zone authoring for large atlases
- easier semantic mapping of atlas subregions
- better overlay support for atlas surfaces

### Concrete ideas
- add atlas-zone overlays
- add zone summaries by named body/UV area after authoring
- support patch operations that work on:
  - named atlas zones
  - rectangular atlas domains
  - semantic zone groups
- add example atlas templates beyond the current proof

### Why this helps AI specifically
Atlas work is where the AI most needs:
- clear coordinates
- region summaries
- zone-level transform control

without being forced into massive raw-pixel editing.

## 5. Safer Detail Replacement Tools

### Why it matters
The desk workflow proved that detail replacement is possible, but it is still too manual.

At the moment, replacing a tool cluster with a book or scissors requires deliberate per-pixel ops.

That is acceptable, but the tool should make that work safer and easier.

### What should improve
- better bounded detail replacement helpers
- easier background fill when old silhouettes are removed
- easier “clear to surrounding material” behavior

### Concrete ideas
- add detail-group clear modes such as:
  - clear to base
  - clear to nearest surrounding material
  - clear to dominant neighboring color field
- add bounded stamp/motif placement for tiny art replacements
- add optional “background infill” helper for exposed areas after deletion

### Why this helps AI specifically
This reduces the amount of brittle manual cleanup after replacing a symbol or tool silhouette.

It would let the AI say:
- clear this old detail group
- fill it consistently with the local material
- then stamp new detail pixels

which is much closer to the intended workflow.

## 6. Transform Diagnostics

### Why it matters
The richer recolor engine is now useful, but debugging transform behavior still requires too much code reading.

The operator should be able to see:
- what policy was used
- what changed
- whether quantization happened
- whether local contrast was preserved

### What should improve
- richer per-region transform reports
- more explicit diagnostics about transform settings and outcomes

### Concrete ideas
- emit transform summaries per semantic domain:
  - source value range
  - source hue/saturation mean and spread
  - transform policy used
  - quantization on/off
  - changed pixel count
- show these in delta JSON or a dedicated report artifact

### Why this helps AI specifically
This would make it much easier to answer:
- why did this region flatten
- why did this hue drift too far
- why does this still read like the old silhouette

without jumping directly into engine code.

## 7. Template Versioning And Promotion Flow

### Why it matters
As the foundry accumulates more families, the path from:
- neutral analysis
- to semantic template
- to family template
- to shipped output

needs to stay organized.

### What should improve
- clearer promotion/refinement/versioning flow
- easier distinction between:
  - seed
  - refined template
  - family template

### Concrete ideas
- add metadata about template origin:
  - seed from analysis
  - promoted from generated PNG
  - refined from prior template
- add helper docs/examples for when to:
  - create a new template
  - patch an existing template
  - create a family template

### Why this helps AI specifically
This keeps template reuse disciplined and prevents the tool from devolving into a pile of ad hoc JSON files.

## 8. Neutral Analysis Profiles

### Why it matters
The old hardcoded `book/sword/pickaxe/bow` analyzer gating was wrong.

That does not mean all profile-like hints are useless.
It means they must be:
- optional
- neutral
- proposal-oriented only

### What should improve
- replace object-family heuristics with neutral analysis profiles when useful

### Acceptable profile ideas
- `generic`
- `single_icon`
- `block_face`
- `atlas_surface`
- maybe `multi_face_block_surface`

### What they must not do
- assign semantic names
- define template truth
- silently overfit analysis to one asset family

### Why this helps AI specifically
This can improve proposal quality while still keeping the interpretation step in the AI/human layer where it belongs.

## 9. Bulk Variant Generation

### Why it matters
A large part of the value of this tool is consistency across variants.

Examples:
- ore/material variants
- tool tier variants
- book family recolors
- wood/stone/metal block families
- armor trim recolors

### What should improve
- one template/family should be able to generate many variants in one run

### Concrete ideas
- accept a request set or variant matrix:
  - asset ids
  - palette swaps
  - transform overrides
- emit one review bundle containing all variants
- optionally emit compare sheets for the whole set

### Why this helps AI specifically
This is exactly the kind of repetitive, consistency-sensitive work AI should automate instead of doing manual Photoshop-like passes.

## 10. Better Direct Art Ops

### Why it matters
Direct pixel editing now works, but the current op vocabulary is still narrow.

For custom detail work, the AI would benefit from a few more bounded drawing primitives.

### What should improve
- richer but still small pixel-native art operations

### Useful additions
- line
- outline rectangle
- bounded flood fill
- small stamp placement
- mirror with placement offsets
- local erase-to-background helper

### What should not happen
- do not turn this into a full image editor
- keep operations deterministic and template-bounded

### Why this helps AI specifically
It reduces the amount of huge per-pixel op payloads needed for tiny motif/detail changes.

## 11. Multi-Surface Block Authoring Convenience

### Why it matters
Blocks like crafting-table families, furniture, furnaces, workstations, and other machine-like blocks often need:
- front
- side
- top
- bottom

Those are not special cases.
They are a common class of Minecraft assets.

### What should improve
- easier multi-surface bundle authoring
- clearer slot-to-surface mapping review

### Concrete ideas
- better bundle planning output
- model slot preview in diagnostics
- easier cloning of a family template from a known vanilla block family

### Why this helps AI specifically
This makes complex block reskins much faster and reduces wiring mistakes.

## 12. Better Handling Of “Preserve Relationships”

### Why it matters
The biggest conceptual lesson from the desk work is that preserving relationships is more important than simply recoloring by region.

The tool now supports:
- preserve value
- palette projection
- hue bias remap
- contrast-preserving recolor

That is good, but further clarity is needed.

### What should improve
- clearer model of what each policy preserves
- easier selection of the right policy for a given region

### Concrete ideas
- document each transform mode with:
  - preserved properties
  - typical use cases
  - failure modes
- add a per-region recommendation helper in diagnostics later if useful

### Why this helps AI specifically
It makes it easier to choose:
- preserve_value for simple tonal remaps
- contrast_preserving_recolor for textured material
- palette_projection for more stylized controlled recolor

without trial-and-error.

## 13. Future-Ready Entity And Armor Work

### Why it matters
The foundry should be useful not just for small blocks and items, but for:
- mobs
- player skins
- armor layers
- future custom atlas workflows

### What should improve
- more proofs and examples for atlas-based workflows
- better multi-zone semantic authoring

### Concrete ideas
- add one more atlas example beyond Steve
- add one armor-layer proof later
- add a mob-skin proof later

### Why this helps AI specifically
It proves the same tooling model scales beyond icons and simple block faces.

## Priority Recommendation

If these were ordered by practical value to the AI using the tool, the strongest next priorities are:

1. Region and cluster inspection UX
2. Template patch authoring ergonomics
3. Compare sheets and review surfaces
4. Safer detail replacement helpers
5. Bulk variant generation
6. Atlas-specific helpers
7. Better direct art ops

That order reflects actual day-to-day asset production value rather than architectural novelty.

## Final Principle

The foundry does not need to become “smart” in itself.

It needs to become:
- mechanically excellent at analysis
- structurally clear in templates
- deterministic in transformation
- easy for an AI to inspect, reason about, and operate

That is the right long-term shape for a general Minecraft pixel asset tool.
