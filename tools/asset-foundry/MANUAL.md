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

The intended architecture is:
- Analyze
- Label
- Transform

The default transformation policy is now:
- preserve relationships first
- flatten only when explicitly requested
- do not palette-snap transformed regions unless explicitly requested

The generalized asset model is:
- a single-surface asset, or
- a named surface bundle

This matters because Minecraft textures are not all one PNG:
- items are often single-surface
- many blocks use multiple face textures
- skins and mobs often use atlas-style layouts inside one surface

## Core Mental Model

There are three important layers:

### 0. Analysis Artifact
This is the mechanical view of a PNG.

It contains:
- canvas and bounds
- color inventory
- connected components
- tone groups / ramps
- detail candidates
- zone candidates
- topology text maps

Important rule:
- analysis artifacts are mechanically neutral
- they do not get to decide that something is a `cover`, `spine`, `blade`, or `pages`
- analysis commands now default to `generic` if no heuristic hint is provided

Those meanings are added later when authoring a template.

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
- optional exact pixel groups and group sets
- edit rules
- engine support rules

Examples:
- `minecraft_vanilla_book_16`
- `minecraft_vanilla_sword_16`
- `minecraft_vanilla_pickaxe_16`
- `minecraft_vanilla_bow_16`

If no edits are applied, a template-backed output should equal the base raster exactly.

This is the important rule.

### 4. Family Template
This is the bundle layer for assets with more than one surface.

A family template defines:
- a family id
- an asset class
- named surfaces like `front`, `side`, `top`, or `atlas_main`
- the output bundle shape
- optional block-model slot mapping

Examples:
- a book icon can be a one-surface family
- a crafting-table-style block is a multi-surface family
- a future player skin can be a single atlas surface with many semantic zones

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
- region-aware and group-aware ops can edit only legal template surfaces
- zero-op draws are valid and should output the base raster exactly

The default recolor behavior for template-backed reskins should be preserve-value:
- source dark pixels map to dark target pixels
- source mid pixels map to mid target pixels
- source light pixels map to light target pixels

This preserves internal detailing instead of flattening a material to one color.

That baseline is now extended by richer transform policies:
- `preserve_value`
- `palette_projection`
- `hue_bias_remap`
- `contrast_preserving_recolor`
- `flat_recolor` as the opt-in fallback

In practical terms:
- semantic regions stay human-manageable
- the transform policy decides how internal color/detail relationships are preserved inside that region
- exact pixel editing still exists, but it is the override path rather than the default reskin path

## Current Template Workflow

There are two main ways to create a template.

### A. Existing PNG -> Template
Use this when the source already exists, such as:
- vanilla book
- vanilla sword
- any other known PNG

Flow:
1. Inspect the image.
2. Analyze it into a neutral analysis artifact.
3. Render overlays or topology maps if helpful.
4. Create a template seed from the image or the analysis artifact.
5. Author semantic groups, sets, and zones in the template patch.
6. Generate variants from the authored template.

If the asset has multiple surfaces, repeat this per surface and then assemble them into a family template.

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
- `validate-repro`

### Template Analysis
- `inspect-image`
- `analyze-image`
- `analyze-image-regions` (compatibility alias)
- `inspect-topology`
- `render-region-overlay`
- `render-group-overlay`
- `create-template-from-image`
- `create-template-seed-from-analysis`
- `refine-template-regions`
- `describe-template`

### Generation
- `repair-generated-png`
- `paint-item-icon`
- `paint-surface-bundle`
- `validate-bundle`
- `render-delta`
- `render-group-overlay`
- `export-group-patch`
- `apply-group-patch`

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
Semantics belong here, not in the analysis artifact.

### `family_template_id`
The reusable named surface-bundle reference.

Use this when an asset has more than one emitted surface, such as:
- front/side/top block textures
- future complex block families
- future atlas-oriented workflows

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
- `cover_detail`
- `emblem_zone`
- `highlight`

Templates can also define exact pixel groups, for example:
- `cover_shadow`
- `cover_mid`
- `cover_light`
- `spine_shadow`
- `spine_mid`
- `page_shadow`
- `page_mid`
- `clasp_pixels`
- `cover_detail_pixels`

Templates may also define:
- `group_set_options`
- `preserve_value`
- `transform_policy`
- `preserve_local_contrast`
- `ramp_roles`

Those control whether recolor should preserve internal tonal relationships, local contrast, and ramp structure instead of flat-filling a whole group.
They can also opt a transform back into palette snapping with `quantize_to_palette: true`, but that is now optional and off by default.
Exact regeneration is not implied by any of this. It is only enforced for explicit repro baselines under `tools/asset-foundry/repro-baselines/`.

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

For multi-surface assets, the same logic applies per surface.
The family template simply bundles the surfaces together and declares their output slots.

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

## Example: Crafting Table Style Block Family

Surface templates:
- [minecraft_crafting_table_front_16.json](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/specs/templates/minecraft_crafting_table_front_16.json)
- [minecraft_crafting_table_side_16.json](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/specs/templates/minecraft_crafting_table_side_16.json)
- [minecraft_crafting_table_top_16.json](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/specs/templates/minecraft_crafting_table_top_16.json)

Family template:
- [minecraft_crafting_table_family_16.json](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/specs/template-families/minecraft_crafting_table_family_16.json)

Canonical bundle request:
- [example-librarians-desk-bundle.json](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/requests/example-librarians-desk-bundle.json)

This is the reference pattern for:
- multi-face blocks
- block reskins that preserve wood/stone/metal detailing
- future block families that cannot be represented by one `cube_all` texture

The intended reskin behavior here is:
- lock tool/line/paper/detail clusters exactly
- recolor only authored material regions
- preserve the original per-pixel structure of those regions

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
- true variations should remap the existing vanilla raster groups, not paint broad overlays over the base book

## Example: Vanilla Handheld Families

Current template proofs:
- [minecraft_vanilla_sword_16.json](/Volumes/External%20SSD%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/specs/templates/minecraft_vanilla_sword_16.json)
- [minecraft_vanilla_pickaxe_16.json](/Volumes/External%20SSD%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/specs/templates/minecraft_vanilla_pickaxe_16.json)
- [minecraft_vanilla_bow_16.json](/Volumes/External%20SSD%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/specs/templates/minecraft_vanilla_bow_16.json)

Current sword proofs:
- [example-ashen-sword-icon.json](/Volumes/External%20SSD%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/requests/example-ashen-sword-icon.json)
- [example-bright-sword-icon.json](/Volumes/External%20SSD%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/requests/example-bright-sword-icon.json)

These prove the family model works beyond books.

## Example: Atlas-Oriented Surface Family

Atlas proof template:
- [minecraft_vanilla_steve_skin_64.json](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/specs/templates/minecraft_vanilla_steve_skin_64.json)

Atlas family template:
- [minecraft_vanilla_player_skin_family_64.json](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/specs/template-families/minecraft_vanilla_player_skin_family_64.json)

Atlas proof request:
- [example-player-skin-atlas.json](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/requests/example-player-skin-atlas.json)

This is not a shipped skin workflow yet.
It is an architecture proof that one atlas surface can:
- remain a neutral analysis target
- be semantically templated into named regions
- carry transform policy metadata
- validate as a family/bundle shape for future player, mob, and armor work

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
2. Run `analyze-image`.
3. Run `render-analysis-overlay` or `render-region-overlay`.
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

### Analyze the vanilla book into a neutral artifact
```bash
tools/asset-foundry/.venv/bin/python tools/asset-foundry/asset_foundry.py analyze-image \
  --minecraft-asset assets/minecraft/textures/item/book.png \
  --minecraft-version 1.21.11 \
  --heuristic book \
  --output tools/asset-foundry/previews/generated/book_analysis.json
```

### Inspect the topology text map
```bash
tools/asset-foundry/.venv/bin/python tools/asset-foundry/asset_foundry.py inspect-topology \
  --minecraft-asset assets/minecraft/textures/item/book.png \
  --minecraft-version 1.21.11 \
  --heuristic generic
```

### Create a template seed from the vanilla book analysis
```bash
tools/asset-foundry/.venv/bin/python tools/asset-foundry/asset_foundry.py create-template-from-image \
  --minecraft-asset assets/minecraft/textures/item/book.png \
  --minecraft-version 1.21.11 \
  --asset-type book_cover_16 \
  --base-mask vanilla_book_16_mask \
  --template-id analyzed_vanilla_book_16 \
  --heuristic generic \
  --output tools/asset-foundry/previews/generated/analyzed_vanilla_book_16.json
```

### Create a seed directly from the saved analysis artifact
```bash
tools/asset-foundry/.venv/bin/python tools/asset-foundry/asset_foundry.py create-template-seed-from-analysis \
  --analysis tools/asset-foundry/previews/generated/book_analysis.json \
  --minecraft-asset assets/minecraft/textures/item/book.png \
  --minecraft-version 1.21.11 \
  --asset-type book_cover_16 \
  --base-mask vanilla_book_16_mask \
  --template-id analyzed_vanilla_book_16_from_analysis \
  --output tools/asset-foundry/previews/generated/analyzed_vanilla_book_16_from_analysis.json
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
- authoring ergonomic improvements for large atlas templates
- richer compare/contact-sheet outputs for bundle review
- more example family templates beyond books and crafting-table-derived blocks
- more MCP/operator shortcuts around transform-policy inspection
- region refinement is still JSON-heavy
- overlays are useful but basic
- neutral region proposals are deterministic but still simple
- not every future family has dedicated masks or richer analysis hints yet

In practice, the next improvements should be:
- easier region patch/refinement workflow
- stronger neutral proposal hints for block faces, single-surface items, and atlas surfaces
- more template families
- better MCP exposure for the analysis/refinement path
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
