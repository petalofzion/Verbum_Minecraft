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

## MVP Scope
Current MVP is **spec-first**, with the next implementation target being pixel-true conversion.

Included now:
- request schema
- asset-type schema
- manifest schema
- palette and mask examples
- a Python CLI for:
  - request validation
  - asset-bundle planning
  - manifest emission
  - manifest validation

Deferred:
- pixel conversion / de-mixel cleanup implementation
- pixel-native drawing implementation
- preview rendering beyond manifest planning
- Blockbench integration
- MCP wrapper

## Suggested Flow
1. Create an asset request JSON under `tools/asset-foundry/requests/`.
2. Validate it:
   - `python3 tools/asset-foundry/asset_foundry.py validate-request <request.json>`
3. Plan the bundle:
   - `python3 tools/asset-foundry/asset_foundry.py plan-bundle <request.json>`
4. Emit a provenance manifest:
   - `python3 tools/asset-foundry/asset_foundry.py emit-manifest <request.json> --output <manifest.json>`
5. Use the planned output paths when creating or converting real PNG/JSON assets.

## Directory Layout
- `specs/`
  - schemas and asset-type definitions
- `palettes/`
  - profile/material palette definitions
- `masks/`
  - silhouette/UV mask metadata
- `requests/`
  - local asset request inputs
- `previews/`
  - local preview output space

## Current Guardrails
- `asset_id` must be lowercase snake_case.
- `output.resource_root` must be repo-relative and point at `modules/<category>/<tier>/<module>/src/main/resources/assets/<namespace>`.
- Requests and manifests are both schema-validated.
- Provenance is mandatory even before real image generation exists.
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
- The long-term design can still expose these operations through MCP later.
- The generated manifest is intended to become the repo memory for how an asset was requested, validated, and reviewed.
- The first MVP intentionally avoids heavyweight external image libraries until dependency/legal review is explicit.

## Local Docs
- [ROADMAP.md](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/ROADMAP.md)
- [TODO.md](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/TODO.md)
