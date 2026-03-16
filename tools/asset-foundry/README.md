# Asset Foundry

`tools/asset-foundry` is the in-repo tooling scaffold for AI-assisted Minecraft asset production.

It is intentionally a **tooling** surface, not runtime mod code.

## Purpose
- define structured asset requests instead of vague prompts
- keep generated assets aligned to Verbum profiles, palettes, masks, and path conventions
- validate asset bundles before they land in module resource paths
- preserve provenance for clean-room and production review

## Why It Lives Here
- Verbum already treats `tools/` as the place for generation, validation, and verification support.
- Shipped PNGs/JSON still belong in normal module resource paths.
- This keeps asset generation aligned with repo architecture instead of becoming a separate disconnected workflow too early.

## MVP Scope
Current MVP is **spec-first**, not full image synthesis.

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
- AI image generation
- pixel repair / de-mixel cleanup
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
5. Use the planned output paths when creating real PNG/JSON assets.

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

## Design Notes
- Python is used for the first MVP because Verbum already has a Python tooling surface under `tools/scripts/`.
- The long-term design can still expose these operations through MCP later.
- The generated manifest is intended to become the repo memory for how an asset was requested, validated, and reviewed.
- The first MVP intentionally avoids heavyweight external image libraries until dependency/legal review is explicit.
