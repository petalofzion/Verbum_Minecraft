# Asset Foundry TODO

This TODO now tracks the generalized analysis -> template -> transform milestone.

Completed foundation:
- [x] PNG-to-pixel conversion
- [x] pixel-native drawing
- [x] preview-first review flow
- [x] manifest/validation basics
- [x] preset-era region-aware ops

## Sprint 1: Template Data Model
Goal: replace “abstract preset only” with “template = base raster + region map + rules”.

- [x] Add `template.schema.json`.
- [x] Add `template_id` support in requests and manifests.
- [x] Add template loading in `asset_foundry.py`.
- [x] Keep legacy preset ids readable for compatibility.
- [x] Add first `specs/templates/` family files.

## Sprint 2: Neutral Image Analysis
Goal: let the tool inspect a PNG and emit useful structure without assigning meaning.

- [x] Add `inspect-image`.
- [x] Add `analyze-image`.
- [x] Keep `analyze-image-regions` as a compatibility alias.
- [x] Add `inspect-topology`.
- [x] Emit:
  - [x] image size
  - [x] non-transparent bounds
  - [x] color histogram
  - [x] connected components
  - [x] neutral detail candidates
  - [x] neutral zone candidates
  - [x] tone groups / ramps
- [ ] Remove remaining family-specific semantic assumptions from analysis helpers.

## Sprint 3: Analysis Overlay and Template Authoring
Goal: keep analysis neutral, then author meaning in templates.

- [x] Add `render-region-overlay`.
- [x] Add `render-group-overlay`.
- [x] Add `create-template-from-image`.
- [x] Add `create-template-seed-from-analysis`.
- [x] Add `refine-template-regions`.
- [x] Add `export-group-patch`.
- [x] Add `apply-group-patch`.
- [x] Add friendlier patch/merge ergonomics for template edits.
- [ ] Add more readable overlay labeling for dense regions.
- [ ] Add a lighter-weight semantic authoring example that starts from a neutral analysis file.

## Sprint 4: Exact Base-Raster Engine Behavior
Goal: unchanged template output must equal the base image.

- [x] Make template-backed pixel drawing start from the base raster.
- [x] Make template-backed conversion preserve locked regions exactly.
- [x] Add locked-region diagnostics in validation.
- [x] Allow zero-op template draws.
- [x] Harden non-template/template mixed-edge behavior further.

## Sprint 4B: True Template Variations
Goal: make template-backed variants transform the base raster instead of painting overlays.

- [x] Add template `pixel_groups`, `group_sets`, and `detail_replacements`.
- [x] Add group-aware book analysis for the vanilla book template.
- [x] Add group-aware pixel-native ops:
  - [x] `remap_group_role`
  - [x] `remap_group_set_role`
  - [x] `replace_detail_group`
  - [x] `apply_emblem_motif`
  - [x] `clear_group_to_base`
- [x] Add group-aware validation for template diffs.
- [x] Add group overlay and group patch commands.
- [x] Add delta artifacts for template-backed generation.
- [x] Add rank-aware group-set remapping when the template provides rank metadata.
- [ ] Replace remaining name-based role inference with fully template-authored role mapping.

## Sprint 5: Book Family Completion
Goal: the vanilla book becomes a reusable family template for manuals and scripture items.

- [x] Add `minecraft_vanilla_book_16`.
- [x] Add a full-width vanilla book mask.
- [x] Move Bible/manual examples onto the template path.
- [x] Prove Bible, Book of Hours, and Dusty Devotional variation flow.
- [x] Add one more shipped book-family example such as Rule of Ashes or Pilgrim’s Atlas.
- [ ] Add easier region-map refinement artifacts for the vanilla book family.
- [x] Rebuild shipped manual books as true template reskins of the vanilla book family.
- [ ] Re-author the vanilla book family from a fully neutral analysis artifact instead of relying on legacy semantic analysis output.

## Sprint 6: Handheld Family Templates
Goal: prove that the same workflow scales beyond books.

- [x] Add `minecraft_vanilla_sword_16`.
- [x] Add `minecraft_vanilla_pickaxe_16`.
- [x] Add `minecraft_vanilla_bow_16`.
- [x] Add one handheld proof request/ops example.
- [ ] Add at least two handheld variants from one family.
- [ ] Add a second proof family beyond sword.

## Sprint 7: Promote Generated Assets to Templates
Goal: let new custom item families become reusable templates.

- [x] Add `promote-to-template`.
- [x] Keep `export-preset-seed` as a compatibility bridge.
- [x] Support optional region-map input when promoting.
- [ ] Add a cleaner region-map authoring example for fully custom items.
- [ ] Add a proof flow for one invented non-vanilla item family.

## Sprint 8: Documentation and MCP Surface
Goal: keep the tool usable by humans and agents.

- [x] Update README for template terminology and commands.
- [x] Update ROADMAP for the raster-backed phase.
- [x] Update TODO for the raster-backed phase.
- [x] Expand MCP wrapper to expose the new template-analysis commands.
- [ ] Add one concise “book family workflow” walkthrough doc.

## Definition of Complete Enough
- [x] Existing PNG -> template works.
- [x] Generated PNG -> promoted template works.
- [x] Books can derive from the vanilla base book raster.
- [x] At least one handheld family can derive from a vanilla base raster.
- [x] Both engines can consume templates.
- [ ] Region refinement should feel less manual before calling the milestone fully polished.
- [ ] Analyzer outputs should stay fully generic even as more family templates are added.
