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

## Core Product Goals

### 1. True Pixel Conversion
The first major feature is **not** generic image cleanup.

It is:
- take a source PNG
- reduce it to a valid target canvas
- quantize it to an allowed palette
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
- rough PNG -> validated pixel-art preview
- pixel-op JSON -> validated pixel-native icon preview
- raster-backed templates -> exact-base family variation workflows

Included now:
- request schema
- asset-type schema
- manifest schema
- mask schema
- pixel-op schema
- preset schema
- template schema
- palette and mask examples
- template family examples for books and handheld items
- a Python CLI for:
  - request validation
  - asset-bundle planning
  - manifest emission
  - manifest validation
  - image inspection
  - image region analysis
  - region overlay rendering
  - raster-backed template creation
  - template region refinement
  - preset inspection
  - template inspection
  - rough PNG repair / conversion
  - texture validation
  - pixel-native item icon painting
  - preset-seed export
  - promote-to-template
- a thin MCP/agent wrapper script

Deferred:
- block/model template helpers beyond simple planning
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
     - `tools/asset-foundry/.venv/bin/python tools/asset-foundry/asset_foundry.py analyze-image-regions --minecraft-asset assets/minecraft/textures/item/book.png --minecraft-version 1.21.11 --heuristic book --output tools/asset-foundry/previews/generated/book_analysis.json`
   - create a raster-backed template:
     - `tools/asset-foundry/.venv/bin/python tools/asset-foundry/asset_foundry.py create-template-from-image --minecraft-asset assets/minecraft/textures/item/book.png --minecraft-version 1.21.11 --asset-type book_cover_16 --base-mask vanilla_book_16_mask --template-id my_book_family --heuristic book`
   - conversion:
     - `tools/asset-foundry/.venv/bin/python tools/asset-foundry/asset_foundry.py repair-generated-png <request.json> --grid`
   - pixel-native:
     - `tools/asset-foundry/.venv/bin/python tools/asset-foundry/asset_foundry.py paint-item-icon <request.json> --ops <ops.json> --grid`
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
- `specs/presets/`
  - reusable family definitions shared by both engines
- `specs/templates/`
  - raster-backed family templates
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
- Presets are optional overlays; non-preset flows still work.
- Templates are the preferred family abstraction for new work.
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
- `analyze-image-regions`
- `render-region-overlay`
- `create-template-from-image`
- `refine-template-regions`
- `repair-generated-png`
- `validate-texture`
- `paint-item-icon`
- `describe-template`
- `describe-preset`
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

## Local Docs
- [ROADMAP.md](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/ROADMAP.md)
- [TODO.md](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/TODO.md)
- [PRESET_TEMPLATE_SPEC.md](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/PRESET_TEMPLATE_SPEC.md)
