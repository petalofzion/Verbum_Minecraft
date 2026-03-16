# Asset Foundry TODO

This TODO now tracks the raster-backed template milestone.

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

## Sprint 2: Image Analysis Primitives
Goal: let the tool inspect a PNG and propose useful structure.

- [x] Add `inspect-image`.
- [x] Add `analyze-image-regions`.
- [x] Emit:
  - [x] image size
  - [x] non-transparent bounds
  - [x] color histogram
  - [x] connected components
  - [x] candidate regions
- [ ] Improve heuristics beyond the first deterministic pass.

## Sprint 3: Region Overlay and Refinement
Goal: make region proposals reviewable and editable.

- [x] Add `render-region-overlay`.
- [x] Add `create-template-from-image`.
- [x] Add `refine-template-regions`.
- [ ] Add friendlier patch/merge ergonomics for region edits.
- [ ] Add more readable overlay labeling for dense regions.

## Sprint 4: Exact Base-Raster Engine Behavior
Goal: unchanged template output must equal the base image.

- [x] Make template-backed pixel drawing start from the base raster.
- [x] Make template-backed conversion preserve locked regions exactly.
- [x] Add locked-region diagnostics in validation.
- [x] Allow zero-op template draws.
- [ ] Harden non-template/template mixed-edge behavior further.

## Sprint 5: Book Family Completion
Goal: the vanilla book becomes a reusable family template for manuals and scripture items.

- [x] Add `minecraft_vanilla_book_16`.
- [x] Add a full-width vanilla book mask.
- [x] Move Bible/manual examples onto the template path.
- [x] Prove Bible, Book of Hours, and Dusty Devotional variation flow.
- [ ] Add one more shipped book-family example such as Rule of Ashes or Pilgrim’s Atlas.
- [ ] Add easier region-map refinement artifacts for the vanilla book family.

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
- [ ] Expand MCP wrapper to expose the new template-analysis commands.
- [ ] Add one concise “book family workflow” walkthrough doc.

## Definition of Complete Enough
- [x] Existing PNG -> template works.
- [x] Generated PNG -> promoted template works.
- [x] Books can derive from the vanilla base book raster.
- [x] At least one handheld family can derive from a vanilla base raster.
- [x] Both engines can consume templates.
- [ ] Region refinement should feel less manual before calling the milestone fully polished.
