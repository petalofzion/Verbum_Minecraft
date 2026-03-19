# Asset Foundry

`tools/asset-foundry` is the in-repo tooling surface for AI-assisted Minecraft asset production.

It is intentionally a **tooling** surface, not runtime mod code.

## Purpose
- define structured asset requests instead of vague prompts
- convert rough PNGs into **true pixel art** suitable for Minecraft assets
- support pixel-native asset creation where the tool paints exact pixels instead of generating fuzzy images
- keep outputs aligned to Verbum profiles, palettes, masks, and path conventions
- validate asset bundles before they land in module resource paths
- preserve provenance for clean-room and production review
- keep recolor transforms continuous by default instead of snapping edited regions back to a tiny palette unless explicitly requested

## Core Product Goals

### 1. True Pixel Conversion
The first major feature is **not** generic image cleanup.

It is:
- take a source PNG
- reduce it to a valid target canvas
- quantize it to an allowed palette when that is the chosen conversion mode
- remove mixels, partial-alpha fuzz, and pseudo-pixel artifacts
- produce a result that is actual pixel art, not just a smaller blurry image

The standard is Minecraft-usable texture output, not "good enough looking concept art."

### 2. Pixel-Native Drawing
The second major feature is a controlled drawing path for agents.

The goal is:
- an agent can create assets by operating on an explicit pixel grid
- the tool enforces allowed palettes, masks, and asset-type rules
- the final output is composed of real pixel placements, not freeform raster generation

This is the future MCP-facing half of the tool.

## What This Tool Is Not
- not a runtime mod feature
- not a generic AI image generator
- not a prompt-only art bot
- not a bypass around module resource ownership
- not a place for shipping assets to live permanently

## Why It Lives Here
- Verbum already treats `tools/` as the place for generation, validation, and verification support.
- Shipped PNGs/JSON still belong in normal module resource paths.
- This keeps asset generation aligned with repo architecture instead of becoming a separate disconnected workflow too early.

## Current Scope
Asset Foundry now has three working layers:
- neutral PNG analysis -> reviewable analysis artifacts
- authored templates -> semantic family definitions on top of a base raster
- transformation engines -> conversion and pixel-native generation from those templates

Included now:
- request schema
- asset-type schema
- manifest schema
- mask schema
- pixel-op schema
- preset schema
- template schema
- family-template schema
- palette and mask examples
- template family examples for books and handheld items
- a Python CLI for:
  - request validation
  - asset-bundle planning
  - manifest emission
  - manifest validation
  - image inspection
  - neutral image analysis
  - topology inspection
  - analysis overlay rendering
  - raster-backed template seed creation
  - template patch export/application
  - named surface bundle painting
  - surface bundle validation
  - delta rendering
  - richer region-scoped recolor transforms
  - preset inspection
  - template inspection
  - rough PNG repair / conversion
  - texture validation
  - pixel-native item icon painting
  - preset-seed export
  - promote-to-template
- a thin MCP/agent wrapper script

Deferred:
- richer variant contact sheets
- Blockbench integration
- richer MCP surface beyond the thin wrapper

## Suggested Flow
1. Create an asset request JSON under `tools/asset-foundry/requests/`.
2. Create a local venv:
   - `python3 -m venv tools/asset-foundry/.venv`
   - `tools/asset-foundry/.venv/bin/python -m pip install -r tools/asset-foundry/requirements.txt`
3. Validate the request:
   - `tools/asset-foundry/.venv/bin/python tools/asset-foundry/asset_foundry.py validate-request <request.json>`
4. Run one of the production flows:
   - inspect/analyze a source image:
     - `tools/asset-foundry/.venv/bin/python tools/asset-foundry/asset_foundry.py inspect-image --minecraft-asset assets/minecraft/textures/item/book.png --minecraft-version 1.21.11`
     - `tools/asset-foundry/.venv/bin/python tools/asset-foundry/asset_foundry.py analyze-image --minecraft-asset assets/minecraft/textures/item/book.png --minecraft-version 1.21.11 --heuristic generic --output tools/asset-foundry/previews/generated/book_analysis.json`
     - `tools/asset-foundry/.venv/bin/python tools/asset-foundry/asset_foundry.py inspect-topology --minecraft-asset assets/minecraft/textures/item/book.png --minecraft-version 1.21.11 --heuristic generic`
   - create a raster-backed template seed:
     - `tools/asset-foundry/.venv/bin/python tools/asset-foundry/asset_foundry.py create-template-from-image --minecraft-asset assets/minecraft/textures/item/book.png --minecraft-version 1.21.11 --asset-type book_cover_16 --base-mask vanilla_book_16_mask --template-id my_book_family_seed --heuristic generic`
   - promote neutral analysis into an editable template seed:
     - `tools/asset-foundry/.venv/bin/python tools/asset-foundry/asset_foundry.py create-template-seed-from-analysis --analysis tools/asset-foundry/previews/generated/book_analysis.json --minecraft-asset assets/minecraft/textures/item/book.png --minecraft-version 1.21.11 --asset-type book_cover_16 --base-mask vanilla_book_16_mask --template-id my_book_family_seed`
   - export/apply a semantic patch:
     - `tools/asset-foundry/.venv/bin/python tools/asset-foundry/asset_foundry.py export-group-patch --template tools/asset-foundry/specs/templates/minecraft_vanilla_book_16.json --output tools/asset-foundry/previews/generated/book_patch.json`
     - `tools/asset-foundry/.venv/bin/python tools/asset-foundry/asset_foundry.py apply-group-patch --template tools/asset-foundry/specs/templates/minecraft_vanilla_book_16.json --patch tools/asset-foundry/previews/generated/book_patch.json --output tools/asset-foundry/previews/generated/book_template_patched.json`
   - conversion:
     - `tools/asset-foundry/.venv/bin/python tools/asset-foundry/asset_foundry.py repair-generated-png <request.json> --grid`
   - pixel-native:
     - `tools/asset-foundry/.venv/bin/python tools/asset-foundry/asset_foundry.py paint-item-icon <request.json> --ops <ops.json> --grid`
   - pixel-native surface bundle:
     - `tools/asset-foundry/.venv/bin/python tools/asset-foundry/asset_foundry.py paint-surface-bundle tools/asset-foundry/requests/example-librarians-desk-bundle.json --ops tools/asset-foundry/examples/pixel-ops/librarians_desk_bundle.ops.json --grid`
   - bundle validation:
     - `tools/asset-foundry/.venv/bin/python tools/asset-foundry/asset_foundry.py validate-bundle tools/asset-foundry/requests/example-librarians-desk-bundle.json`
   - explicit repro baseline validation:
     - `tools/asset-foundry/.venv/bin/python tools/asset-foundry/asset_foundry.py validate-repro tools/asset-foundry/repro-baselines/librarians_desk_recolor_only.json`
   - delta review:
     - `tools/asset-foundry/.venv/bin/python tools/asset-foundry/asset_foundry.py render-delta --base-image <base.png> --generated-image <generated.png> --output <delta.png>`
   - inspect a template:
     - `tools/asset-foundry/.venv/bin/python tools/asset-foundry/asset_foundry.py describe-template <template_id>`
   - inspect a preset:
     - `tools/asset-foundry/.venv/bin/python tools/asset-foundry/asset_foundry.py describe-preset <preset_id>`
   - export a reusable preset scaffold:
     - `tools/asset-foundry/.venv/bin/python tools/asset-foundry/asset_foundry.py export-preset-seed <request.json> --generated-asset <image.png> --base-mask <mask_id> --region-map <region-map.json> --target-preset-id <preset_id> --output <preset.json>`
5. Validate the result:
   - `tools/asset-foundry/.venv/bin/python tools/asset-foundry/asset_foundry.py validate-texture <request.json> <image.png>`
6. Review preview-first outputs under `tools/asset-foundry/previews/generated/`.

## Directory Layout
- `specs/`
  - schemas and asset-type definitions
- `palettes/`
  - profile/material palette definitions
- `masks/`
  - silhouette/UV mask metadata
- `specs/templates/`
  - raster-backed family templates
- `specs/template-families/`
  - named surface-bundle family templates
- `specs/presets/`
  - legacy compatibility family definitions
- `requests/`
  - local asset request inputs
- `previews/`
  - local preview output space
- `examples/`
  - sample source PNGs and pixel-op files
- `tests/`
  - local unittest coverage

## Current Guardrails
- `asset_id` must be lowercase snake_case.
- `output.resource_root` must be repo-relative and point at `modules/<category>/<tier>/<module>/src/main/resources/assets/<namespace>`.
- Requests and manifests are both schema-validated.
- Provenance is mandatory even before real image generation exists.
- Preview-first output is the default.
- Analysis artifacts are mechanically neutral and disposable.
- `--heuristic` is now optional on analysis/template-seed commands and defaults to `generic`.
- Templates are the authored semantic bridge between analysis and generation.
- Family templates assemble one or more named surfaces into a reusable asset bundle.
- Presets are compatibility data; templates are the preferred family abstraction for new work.
- Rich recolor transforms are the default for template-backed reskins:
  - `palette_projection`
  - `contrast_preserving_recolor`
  - `preserve_value`
  - `hue_bias_remap`
  - `flat_recolor` remains the explicit override path
- Palette quantization after a transform is optional and now off by default for template-backed recolor domains.
- `quantize_to_palette: true` may be set on a group, group set, or pixel op when strict palette snapping is actually desired.
- Exact regeneration checks are opt-in and only run through explicit repro baselines under `tools/asset-foundry/repro-baselines/`.
- This tool plans and validates outputs; it does not bypass normal module resource ownership.

## Quality Standard for "Proper Pixel Art"
For this tool, "proper pixel art" means:
- exact target dimensions
- no accidental anti-aliasing haze
- no mixels unless explicitly allowed by palette/mask rules
- alpha snapped to legal values for the asset type
- readable at Minecraft scale
- palette discipline rather than uncontrolled color soup

If the output still looks like resized digital painting, the tool has failed.

## Design Notes
- The intended architecture is `Analyze -> Label -> Transform`.
- The analyzer is not allowed to assign semantic names like `cover` or `pages`.
- Semantic names belong in authored templates and patches.
- Legacy family hints may still bias coarse region suggestions, but the default path is generic mechanical analysis.
- Surface templates may now carry relationship-preserving transform policy metadata so recolor can preserve:
  - value ordering
  - local hue/saturation drift
  - local contrast and texture detail
- Python is used for the first MVP because Verbum already has a Python tooling surface under `tools/scripts/`.
- The thin wrapper at `asset_foundry_mcp.py` exposes the stable operations without moving logic out of the CLI/core engine.
- The generated manifest is intended to become the repo memory for how an asset was requested, validated, and reviewed.
- The first MVP intentionally avoids heavyweight external image libraries until dependency/legal review is explicit.

## Implemented Commands
- `validate-request`
- `plan-bundle`
- `emit-manifest`
- `validate-manifest`
- `inspect-image`
- `analyze-image`
- `analyze-image-regions` (compatibility alias)
- `inspect-topology`
- `render-region-overlay`
- `render-analysis-overlay` (compatibility alias)
- `render-group-overlay`
- `create-template-from-image`
- `create-template-seed-from-analysis`
- `refine-template-regions`
- `repair-generated-png`
- `validate-texture`
- `paint-item-icon`
- `paint-surface-bundle`
- `validate-bundle`
- `render-delta`
- `describe-template`
- `describe-preset`
- `export-group-patch`
- `apply-group-patch`
- `export-preset-seed`
- `promote-to-template`

## Example Flows
- preset-driven scripture/manual family:
  - [requests/example-bible-icon.json](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/requests/example-bible-icon.json)
  - [requests/example-book-of-hours-icon.json](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/requests/example-book-of-hours-icon.json)
  - [requests/example-dusty-devotional-icon.json](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/requests/example-dusty-devotional-icon.json)
- template definitions:
  - [specs/templates/minecraft_vanilla_book_16.json](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/specs/templates/minecraft_vanilla_book_16.json)
  - [specs/templates/minecraft_vanilla_sword_16.json](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/specs/templates/minecraft_vanilla_sword_16.json)
  - [specs/templates/minecraft_vanilla_pickaxe_16.json](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/specs/templates/minecraft_vanilla_pickaxe_16.json)
  - [specs/templates/minecraft_vanilla_bow_16.json](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/specs/templates/minecraft_vanilla_bow_16.json)
  - [specs/templates/minecraft_crafting_table_front_16.json](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/specs/templates/minecraft_crafting_table_front_16.json)
  - [specs/templates/minecraft_crafting_table_side_16.json](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/specs/templates/minecraft_crafting_table_side_16.json)
  - [specs/templates/minecraft_crafting_table_top_16.json](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/specs/templates/minecraft_crafting_table_top_16.json)
- family templates:
  - [specs/template-families/minecraft_crafting_table_family_16.json](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/specs/template-families/minecraft_crafting_table_family_16.json)
  - [specs/template-families/minecraft_vanilla_player_skin_family_64.json](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/specs/template-families/minecraft_vanilla_player_skin_family_64.json)
- atlas architecture proof:
  - [requests/example-player-skin-atlas.json](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/requests/example-player-skin-atlas.json)
  - [specs/templates/minecraft_vanilla_steve_skin_64.json](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/specs/templates/minecraft_vanilla_steve_skin_64.json)
- preset definitions:
  - [specs/presets/vanilla_book_icon_16.json](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/specs/presets/vanilla_book_icon_16.json)
  - [specs/presets/manual_book_icon_32.json](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/specs/presets/manual_book_icon_32.json)
  - [specs/presets/generated_item_basic_16.json](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/specs/presets/generated_item_basic_16.json)
- book/manual cover conversion:
  - [requests/example-devotional-cover.json](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/requests/example-devotional-cover.json)
- simple icon drawing:
  - [requests/example-librarians-desk-icon.json](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/requests/example-librarians-desk-icon.json)
  - [examples/pixel-ops/librarians_desk_icon.ops.json](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/examples/pixel-ops/librarians_desk_icon.ops.json)
- furniture/block texture conversion:
  - [requests/example-librarians-desk-face.json](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/requests/example-librarians-desk-face.json)
- multi-surface block bundle conversion:
  - [requests/example-librarians-desk-bundle.json](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/requests/example-librarians-desk-bundle.json)
  - [examples/pixel-ops/librarians_desk_bundle.ops.json](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/examples/pixel-ops/librarians_desk_bundle.ops.json)

## Local Docs
- [ROADMAP.md](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/ROADMAP.md)
- [TODO.md](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/TODO.md)
- [PRESET_TEMPLATE_SPEC.md](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/PRESET_TEMPLATE_SPEC.md)
