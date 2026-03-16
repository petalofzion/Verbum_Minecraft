# AGENTS.md: Guidelines for `tools/asset-foundry`

This directory is the repo-local tooling surface for AI-assisted asset generation, repair, validation, and provenance.

It is **not** runtime mod code.

## Non-Negotiables
- Keep all generation logic under `tools/asset-foundry/`.
- Do not move image-processing or MCP-serving code into `modules/*` or `assemblies/*`.
- Shipped assets still belong in normal module resource paths under `src/main/resources/assets/<namespace>`.
- Keep requests, masks, palettes, and manifests structured and machine-validated.
- Prefer permissive dependencies only. If you adapt external code or algorithms, update [SOURCE_ATTRIBUTION.md](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/SOURCE_ATTRIBUTION.md) and `LICENSES/`.

## Read Order
1. [README.md](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/README.md)
2. [docs/ARCHITECTURE_MAP.md](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/docs/ARCHITECTURE_MAP.md)
3. [docs/UPDATE_SURFACES.md](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/docs/UPDATE_SURFACES.md)
4. [SOURCE_ATTRIBUTION.md](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/SOURCE_ATTRIBUTION.md)

## Definition of Done
- Request/manifest schemas validate.
- Planned asset output paths stay repo-relative and land under module resource roots.
- Provenance is preserved for generated outputs.
- Any new external dependency is documented and legally compatible.
- Tooling changes do not alter runtime code paths.
