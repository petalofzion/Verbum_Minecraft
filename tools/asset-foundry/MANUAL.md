# Asset Foundry Manual

This manual is the operational guide for `tools/asset-foundry`.

It is written for:
- future Codex/Copilot-style agents
- human operators working in this repo
- orchestrators that need to understand how asset generation is meant to work here

This file should be updated whenever the foundry model or workflow changes in a meaningful way.

## What Asset Foundry Is

Asset Foundry is the in-repo tooling surface for 2D Minecraft asset production.

It is not runtime mod code.

Its job is to:
- inspect and analyze source PNGs
- convert rough PNGs into proper pixel-art outputs
- support exact-pixel drawing flows
- turn base rasters into reusable template families
- generate coherent variants from those templates
- keep outputs validated, preview-first, and provenance-tracked

## Core Mental Model

There are three important layers:

### 1. Asset Type
This is the coarse technical category.

Examples:
- `book_cover_16`
- `book_cover_32`
- `simple_item_16`
- `simple_block_face_16`

Asset types define:
- canvas size
- broad output kind
- general rules like alpha and mixel policy

Asset types do not define a reusable family look.

### 2. Mask
This is the coarse allowed-pixel shape or layout.

Examples:
- `vanilla_book_16_mask`
- `full_item_16_mask`
- `bench_item_icon_mask`

Masks define:
- where opaque pixels are allowed
- forbidden areas
- coarse zones

Masks are useful guardrails, but they are not enough on their own for coherent families.

### 3. Template
This is the real reusable family unit.

A template is:
- a base raster image
- a region map
- edit rules
- engine support rules

Examples:
- `minecraft_vanilla_book_16`
- `minecraft_vanilla_sword_16`
- `minecraft_vanilla_pickaxe_16`
- `minecraft_vanilla_bow_16`

If no edits are applied, a template-backed output should equal the base raster exactly.

This is the important rule.

## Exact Base Output

Templates are exact-raster-backed by default.

That means:
- if a template is created from Mojang's `book.png`
- and you render it with zero edits
- the output should match that source PNG pixel-for-pixel

This is what makes template variation trustworthy.

The template is not just an abstract “book-like shape.”
It is a specific base asset plus allowed edit regions.

## Current Engines

Asset Foundry has two production engines:

### 1. PNG Ingest / Conversion
Command:
- `repair-generated-png`

Purpose:
- take a rough source PNG
- resize it to the target canvas
- constrain it to the asset family
- clean pseudo-pixel artifacts
- emit a valid preview-first texture

When a template is present:
- the base raster is the starting point
- source influence is limited to editable regions
- locked regions preserve the base pixels exactly

### 2. Pixel-Native Drawing
Command:
- `paint-item-icon`

Purpose:
- start from either blank canvas or template base
- apply exact pixel operations
- emit a deterministic texture

When a template is present:
- drawing starts from the exact base raster
- region-aware ops can edit only legal regions
- zero-op draws are valid and should output the base raster exactly

## Current Template Workflow

There are two main ways to create a template.

### A. Existing PNG -> Template
Use this when the source already exists, such as:
- vanilla book
- vanilla sword
- any other known PNG

Flow:
1. Inspect the image.
2. Analyze it for regions.
3. Render an overlay if helpful.
4. Create a template from that image.
5. Refine the region map if needed.
6. Generate variants from the template.

### B. Generated PNG -> Promoted Template
Use this when a family does not exist yet and you invent a base asset first.

Flow:
1. Make or import the base PNG.
2. Promote it into a template.
3. Refine regions if needed.
4. Generate future variants from that template.

This is the workflow for totally new item families.

## Current Commands

### Validation and Planning
- `validate-request`
- `plan-bundle`
- `emit-manifest`
- `validate-manifest`
- `validate-texture`

### Template Analysis
- `inspect-image`
- `analyze-image-regions`
- `render-region-overlay`
- `create-template-from-image`
- `refine-template-regions`
- `describe-template`

### Generation
- `repair-generated-png`
- `paint-item-icon`

### Promotion / Reuse
- `promote-to-template`
- `export-preset-seed`

`describe-preset` still exists as a compatibility alias.

## Important Request Fields

### `asset_type`
The technical class of asset.

### `mask_id`
The coarse allowed shape/layout.

### `template_id`
The preferred reusable family reference.

This is the primary family mechanism for new work.

### `preset_id`
Legacy compatibility field.

Still supported, but template-first is the intended direction now.

### `material_palette`
The palette used for recolor and role resolution.

### `provenance`
Always required.

This is part of the clean-room and review memory.

## Template Regions

Regions are the parts of a template that can be understood and edited separately.

Examples for book families:
- `spine`
- `cover`
- `page_edge`
- `clasp`
- `emblem`
- `highlight`

Examples for sword families:
- `blade`
- `guard`
- `handle`

Each region has a mode:
- `locked`
- `recolor_only`
- `motif`
- `free_paint`
- `shade_only`

These modes control what the engines are allowed to do there.

## Region Modes

### `locked`
Pixels in this region should preserve the base raster exactly.

Use this for:
- pages
- bow strings
- structural details you do not want drifted

### `recolor_only`
The region can change color, but should preserve the underlying structure.

Use this for:
- book cover areas
- sword blade material
- handles

### `motif`
The region accepts bounded decorative edits.

Use this for:
- emblems
- logos
- small symbolic marks

### `free_paint`
The region allows more open editing.

Use this sparingly.

### `shade_only`
The region is for highlights/shadows, not wholesale redesign.

## Example: Vanilla Book Family

Canonical template:
- [minecraft_vanilla_book_16.json](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/specs/templates/minecraft_vanilla_book_16.json)

Canonical mask:
- [vanilla_book_16_mask.json](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/masks/vanilla_book_16_mask.json)

This is the intended base for:
- Bible
- Book of Hours
- Dusty Devotional
- Rule of Ashes
- Pilgrim's Atlas
- similar manual/about/book items

Current proof requests:
- [example-bible-icon.json](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/requests/example-bible-icon.json)
- [example-book-of-hours-icon.json](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/requests/example-book-of-hours-icon.json)
- [example-dusty-devotional-icon.json](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/requests/example-dusty-devotional-icon.json)

Important principle:
- these should be variants of the vanilla book family
- not one-off disconnected icons

## Example: Vanilla Handheld Families

Current template proofs:
- [minecraft_vanilla_sword_16.json](/Volumes/External%20SSD%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/specs/templates/minecraft_vanilla_sword_16.json)
- [minecraft_vanilla_pickaxe_16.json](/Volumes/External%20SSD%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/specs/templates/minecraft_vanilla_pickaxe_16.json)
- [minecraft_vanilla_bow_16.json](/Volumes/External%20SSD%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/specs/templates/minecraft_vanilla_bow_16.json)

Current sword proofs:
- [example-ashen-sword-icon.json](/Volumes/External%20SSD%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/requests/example-ashen-sword-icon.json)
- [example-bright-sword-icon.json](/Volumes/External%20SSD%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/requests/example-bright-sword-icon.json)

These prove the family model works beyond books.

## Typical Workflows

### Use the Vanilla Book as a Base and Make Variants
1. Start from template:
   - `minecraft_vanilla_book_16`
2. Create a request with:
   - `asset_type = book_cover_16`
   - `mask_id = vanilla_book_16_mask`
   - `template_id = minecraft_vanilla_book_16`
3. Add pixel ops that only change:
   - cover
   - spine
   - clasp
   - emblem
   - highlight
4. Generate the new asset.
5. Validate it.

### Import a New Existing PNG into a Template
1. Run `inspect-image`.
2. Run `analyze-image-regions`.
3. Run `render-region-overlay`.
4. Run `create-template-from-image`.
5. If needed, patch the regions with `refine-template-regions`.

### Promote a New Generated Item into a Family
1. Create the base asset.
2. Run `promote-to-template`.
3. Refine regions.
4. Use that template for later variants.

## Commands to Remember

### Inspect the vanilla book
```bash
tools/asset-foundry/.venv/bin/python tools/asset-foundry/asset_foundry.py inspect-image \
  --minecraft-asset assets/minecraft/textures/item/book.png \
  --minecraft-version 1.21.11
```

### Analyze regions for the vanilla book
```bash
tools/asset-foundry/.venv/bin/python tools/asset-foundry/asset_foundry.py analyze-image-regions \
  --minecraft-asset assets/minecraft/textures/item/book.png \
  --minecraft-version 1.21.11 \
  --heuristic book \
  --output tools/asset-foundry/previews/generated/book_analysis.json
```

### Create a template from the vanilla book
```bash
tools/asset-foundry/.venv/bin/python tools/asset-foundry/asset_foundry.py create-template-from-image \
  --minecraft-asset assets/minecraft/textures/item/book.png \
  --minecraft-version 1.21.11 \
  --asset-type book_cover_16 \
  --base-mask vanilla_book_16_mask \
  --template-id analyzed_vanilla_book_16 \
  --heuristic book \
  --output tools/asset-foundry/previews/generated/analyzed_vanilla_book_16.json
```

### Render the base vanilla book from the template exactly
```bash
tools/asset-foundry/.venv/bin/python tools/asset-foundry/asset_foundry.py paint-item-icon \
  tools/asset-foundry/requests/example-bible-icon.json \
  --ops tools/asset-foundry/examples/pixel-ops/noop.ops.json \
  --output tools/asset-foundry/previews/generated/vanilla_book_base.png \
  --manifest-output tools/asset-foundry/previews/generated/vanilla_book_base.manifest.json \
  --preview-output tools/asset-foundry/previews/generated/vanilla_book_base_preview.png \
  --grid
```

## What Still Needs Polish

The core workflow works.

What is still rough:
- region refinement is still JSON-heavy
- overlays are useful but basic
- heuristic proposals are deterministic but still simple
- not every future family has dedicated masks or strong heuristics yet

In practice, the next improvements should be:
- easier region patch/refinement workflow
- stronger family-specific heuristics
- more template families
- better MCP exposure for the analysis/refinement path

## Family-Specific Robustness

Some families need their own layout intelligence.

Books are already a good example.

For future families, the same principle applies:
- swords want `blade`, `guard`, `handle`
- pickaxes want `head`, `handle`
- bows want `limbs`, `grip`, `string`
- humanoid skins would want things like:
  - head front
  - torso front
  - arms
  - legs
  - outer layer zones

That is what “better family-specific mask/template support” means:
- not just generic image tools
- but reusable coordinate and region logic for each texture family

## Rules for Future Agents

- Prefer `template_id` for new work.
- Keep `preset_id` only for compatibility or migration.
- If using a vanilla family, use the exact-base template, not a vague approximation.
- If no family exists yet, create or promote one instead of producing many one-off assets.
- Update this manual when the workflow meaningfully changes.
