# Preset Template Spec

This spec defines the next upgrade for Asset Foundry: a reusable preset/template layer that sits above raw asset types and masks.

## Why This Exists
Current Asset Foundry already has:
- asset types
- masks
- palettes
- pixel-native drawing
- rough PNG conversion

That is enough to produce assets, but not enough to make asset families feel effortless.

The next step is a system where Verbum can define reusable **preset families** such as:
- vanilla-style books
- manual/codex books
- ingots
- dusts
- tool heads
- furniture item icons
- block-face material families
- future entity skin templates

Then both engines use the same preset:
- the PNG-ingest engine constrains conversion through the preset
- the pixel-native engine paints within the preset

## Model Layers

### 1. Asset Type
Keep this as the coarse technical category:
- `item_icon`
- `block_texture`
- `uv_texture`

Asset types define:
- canvas dimensions
- output file bundle shape
- general rendering rules

### 2. Preset Family
Add this as a reusable structural template.

Examples:
- `vanilla_book_icon_16`
- `manual_book_icon_32`
- `generated_item_basic_16`
- `single_face_plank_block_16`
- `bench_uv_v1_32`

Preset families define:
- the base silhouette or region layout
- named editable regions
- locked or preserved regions
- allowed overrides
- default style assumptions

### 3. Region Roles
Add named region semantics inside a preset, for example:
- `cover`
- `spine`
- `page_edge`
- `clasp`
- `emblem`
- `shadow`
- `highlight`
- `wear`

Each region should state:
- its pixel bounds
- whether it is recolor-only
- whether motifs can be placed there
- whether it is locked
- whether symmetry applies

## Shared Requirements Across Both Engines

### For PNG Conversion
The preset should tell the conversion engine:
- which regions may be influenced by the source PNG
- which regions must stay structurally fixed
- which regions should be recolored instead of freely copied
- where motif/logo extraction is allowed

### For Pixel-Native Drawing
The preset should tell the drawing engine:
- what regions are available
- which operations are legal per region
- which colors/roles may be used where
- what pixels must stay unchanged or transparent

## New Schema Direction

Add a new schema under `tools/asset-foundry/specs/presets/`.

Each preset should include:
- `id`
- `asset_type`
- `base_mask`
- `palette_roles`
- `regions`
- `locked_regions`
- `free_paint_regions`
- `symmetry`
- `engine_support`
- `notes`

### Region fields
Each region should support:
- `mode`: `locked`, `recolor_only`, `motif`, `free_paint`, `shade_only`
- `rects`
- `allowed_palette_roles`
- `default_palette_role`
- `optional`: true/false

## Palette Upgrade
Palettes should evolve from flat color lists into role-aware palettes.

Example role-aware palette keys:
- `cover_dark`
- `cover_mid`
- `cover_light`
- `spine_dark`
- `page_tone`
- `metal_accent`
- `shadow`
- `highlight`

The flat ordered list can remain for compatibility, but role names should be the main interface for presets.

## Command Upgrades

Current commands should gain optional preset support.

Add or upgrade:
- `describe-preset`
- `repair-generated-png --preset <preset_id>`
- `paint-item-icon --preset <preset_id>`
- `validate-texture --preset <preset_id>`

For pixel-native drawing, add region-aware operations such as:
- `fill_region_role`
- `recolor_region`
- `apply_motif`
- `shade_region`

## First Presets To Build

### `vanilla_book_icon_16`
Purpose:
- all Bible/manual/book items that should feel close to vanilla book language

Editable regions:
- spine
- cover
- page_edge
- clasp
- emblem

### `manual_book_icon_32`
Purpose:
- richer manuals while keeping the same family language

### `generated_item_basic_16`
Purpose:
- a base family for simple custom items that share a silhouette language

### `single_face_plank_block_16`
Purpose:
- material-driven block faces with controlled variation

## Entity and Skin Extension
This same preset idea should later scale to Minecraft skin-like layouts and entity textures.

That means presets should not assume "books only" or "items only." They should remain generic enough to express:
- fixed transparent regions
- required dark/outline regions
- editable zones
- role-based recolor areas

This is the bridge to future mob/entity texture tooling.

## Acceptance Criteria For This Upgrade
- presets can be defined and loaded from files
- both engines can consume the same preset id
- book-family presets can generate consistent variants
- the user can iterate on a base item, then promote it into a reusable preset
- future new item families can be added without rewriting engine logic
