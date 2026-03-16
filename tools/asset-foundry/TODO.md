# Asset Foundry TODO

This TODO is for the next milestone: the preset/template upgrade.

The previous milestone is complete and delivered:
- PNG-to-pixel conversion
- pixel-native drawing
- validation
- preview-first review flow
- thin MCP wrapper

## Sprint 1: Preset Schema and Loader
Goal: add a first-class preset/template layer above asset types and masks.

### Schema
- [ ] Add `preset.schema.json`.
- [ ] Define required preset fields:
  - [ ] `id`
  - [ ] `asset_type`
  - [ ] `base_mask`
  - [ ] `palette_roles`
  - [ ] `regions`
  - [ ] `locked_regions`
  - [ ] `free_paint_regions`
  - [ ] `symmetry`
  - [ ] `engine_support`
- [ ] Add `tools/asset-foundry/specs/presets/` folder.

### Loader
- [ ] Add preset loading to `asset_foundry.py`.
- [ ] Validate preset compatibility against asset type and mask.
- [ ] Add `describe-preset` CLI command.

### Acceptance
- [ ] Presets can be loaded and validated by id.
- [ ] The CLI can describe a preset cleanly.

## Sprint 2: Role-Aware Palettes
Goal: make presets express semantic color roles instead of only flat palette lists.

### Palette Upgrade
- [ ] Extend palette schema to support role names.
- [ ] Preserve compatibility with existing flat color arrays.
- [ ] Add role-aware palettes for:
  - [ ] `veritas_leather`
  - [ ] `vocations_oak`

### Acceptance
- [ ] Presets can request palette roles such as `cover_dark`, `spine_dark`, `page_tone`, `metal_accent`.

## Sprint 3: Region-Aware Drawing Engine
Goal: make pixel-native drawing operate through preset regions, not just raw coordinates.

### New Ops
- [ ] Add region-aware operations:
  - [ ] `fill_region_role`
  - [ ] `recolor_region`
  - [ ] `apply_motif`
  - [ ] `shade_region`
- [ ] Keep raw pixel ops available as an advanced path.

### Enforcement
- [ ] Enforce region mode restrictions:
  - [ ] locked
  - [ ] recolor_only
  - [ ] motif
  - [ ] free_paint
  - [ ] shade_only

### Acceptance
- [ ] A preset-driven item can be drawn without specifying every pixel by hand.

## Sprint 4: Region-Aware PNG Conversion
Goal: make the PNG-ingest engine honor preset regions and locked structure.

### Conversion Constraints
- [ ] Add preset-aware conversion rules:
  - [ ] source image can influence only editable regions
  - [ ] locked regions stay fixed
  - [ ] motif extraction happens only in motif regions
  - [ ] recolor-only regions map into palette roles

### Acceptance
- [ ] Rough input images can be converted into preset-consistent results instead of loosely constrained recolors.

## Sprint 5: Base Asset -> Preset Workflow
Goal: promote an approved base asset into a reusable template family.

### Workflow
- [ ] Define how a reviewed asset becomes a preset seed.
- [ ] Add a manifest field or preset-export command to mark a generated asset as a preset candidate.
- [ ] Add a `promote-to-preset` workflow or equivalent documented process.

### Acceptance
- [ ] A newly invented item family can be iterated once, then reused for many variants.

## Sprint 6: Book Family Presets
Goal: implement the first robust family you actually need for the mod.

### Required Presets
- [ ] `vanilla_book_icon_16`
- [ ] `manual_book_icon_32`

### Required Regions
- [ ] spine
- [ ] cover
- [ ] page_edge
- [ ] clasp
- [ ] emblem
- [ ] optional wear/shadow/highlight roles

### First Outputs
- [ ] regenerate Bible through the preset system
- [ ] generate at least two more manual/book variants through the same family

### Acceptance
- [ ] Bible/manual item assets can be produced as a coherent family instead of one-off icons.

## Cross-Cutting Work

### Testing
- [ ] Add tests for preset validation.
- [ ] Add tests for palette-role lookup.
- [ ] Add tests for region-aware drawing enforcement.
- [ ] Add tests for region-aware conversion enforcement.

### Documentation
- [ ] Keep README aligned to the preset system as it lands.
- [ ] Extend `PRESET_TEMPLATE_SPEC.md` only as decisions become implemented.
- [ ] Keep examples current with the new preset-driven flows.

## Definition of "Complete Enough"
- [ ] Presets are real files the tool can load.
- [ ] Both engines can use the same preset id.
- [ ] A base item can become a reusable family template.
- [ ] Vanilla-like book families can be generated consistently from the preset system.
