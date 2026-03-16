# Asset Foundry Roadmap

This roadmap is for the local `tools/asset-foundry` tool only.

It is intentionally short and directional. The detailed execution plan lives in [TODO.md](/Volumes/External%20SSD%20Sandisk%202TB%20Sky/Repos/Verbum_Minecraft/tools/asset-foundry/TODO.md).

## End State
Asset Foundry should let Verbum define an asset request, then either:
- convert a rough PNG into true Minecraft-style pixel art, or
- generate pixel-native art directly through constrained rules,

while preserving:
- palette discipline
- mask/type constraints
- resource-path correctness
- provenance and review metadata

## Major Work Streams

### 1. Spec and Provenance Foundation
Keep requests, masks, palettes, asset types, and manifests structured and validated.

Status: started

### 2. PNG-to-Pixel Conversion
Build the first major production feature:
- take source PNG input
- resize and normalize
- quantize to approved palette
- eliminate mixels and pseudo-pixel artifacts
- export a true pixel-art PNG

Status: next priority

### 3. Pixel-Native Drawing
Build the second major production feature:
- let an agent or CLI instruction operate on a strict pixel grid
- enforce mask and palette rules
- emit only exact pixel placements

Status: after conversion path is stable

### 4. Validation and Preview
Add:
- texture validation
- readability checks
- preview sheets / magnified previews
- failure diagnostics that help iteration

Status: tied to both production paths

### 5. Agent and MCP Integration
Expose the tool cleanly so Codex-style agents can call it without bypassing the spec/provenance flow.

Status: later, after the core engine is stable

## Near-Term Completion Target
The first "complete enough" version should support:
- one real conversion flow from rough PNG -> valid pixel-art PNG
- one real pixel-native drawing flow for a small asset type
- one validation command with actionable diagnostics
- one preview output path
- one end-to-end example bundle landed through the tool

## Scope Discipline
Do not expand into:
- full generic image generation platform
- model editor replacement
- runtime rendering features
- unreviewed external dependency sprawl
