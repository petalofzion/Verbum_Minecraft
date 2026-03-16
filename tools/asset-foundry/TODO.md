# Asset Foundry TODO

This is the detailed implementation plan for `tools/asset-foundry`.

The two primary goals are:
1. convert rough PNGs into proper pixel art for Minecraft assets
2. support pixel-native drawing where an agent paints actual pixels under strict rules

## Sprint 1: Conversion Path MVP
Goal: the tool can take an input PNG and emit a real pixel-art output that avoids mixels and pseudo-pixel blur.

### Request and Spec Expansion
- [x] Add a source-image input field to the request model or a dedicated conversion command input.
- [x] Add asset-type rules for:
  - [x] target dimensions
  - [x] palette source
  - [x] transparency policy
  - [x] mixel tolerance policy
  - [x] readability hints
- [x] Add one or two more real asset types beyond current scaffolds:
  - [x] `book_cover_16`
  - [x] `book_cover_32`
  - [x] `simple_block_face_16`

### Conversion Engine
- [x] Choose the first image-processing dependency path and review license fit.
- [x] Implement image load and export.
- [x] Implement dimension normalization:
  - [x] resize to exact target canvas
  - [x] preserve nearest-neighbor semantics where appropriate
- [x] Implement palette quantization:
  - [x] map to explicit palette file
  - [x] reject uncontrolled colors
- [x] Implement alpha cleanup:
  - [x] remove unintended semi-transparent haze
  - [x] snap alpha according to asset type
- [x] Implement anti-mixel cleanup:
  - [x] detect isolated off-palette fuzz
  - [x] normalize noisy edge transitions
  - [x] avoid turning intended contrast into mush

### Conversion Commands
- [x] Add `repair-generated-png` CLI command.
- [x] Add output-path selection consistent with the manifest/request flow.
- [x] Add dry-run mode that reports what would be changed.
- [x] Add optional side-by-side before/after preview output.

### Validation
- [x] Add `validate-texture` CLI command.
- [x] Validate:
  - [x] dimensions
  - [x] palette membership
  - [x] alpha policy
  - [x] forbidden pixels outside the mask
  - [x] output path conventions
- [x] Emit clear diagnostics instead of generic pass/fail only.

### Acceptance for Sprint 1
- [x] A rough PNG can be converted into a true pixel-art output.
- [x] The output is visibly cleaner and Minecraft-usable.
- [x] The validator can explain why an output fails.
- [x] The tool emits provenance for the conversion.

## Sprint 2: Pixel-Native Drawing MVP
Goal: the tool can generate pixel art directly through exact pixel placement and constrained rules.

### Mask System
- [x] Replace placeholder mask metadata with a real mask format.
- [x] Define mask semantics:
  - [x] allowed pixels
  - [x] forbidden pixels
  - [x] optional zones
  - [x] symmetry rules
  - [x] reserved highlight/shadow regions
- [x] Add first real masks for:
  - [x] simple item icon
  - [x] book cover
  - [x] bench/block item silhouette

### Drawing Model
- [x] Define a pixel-operation schema:
  - [x] set pixel
  - [x] fill region
  - [x] shade zone
  - [x] mirror/symmetry helper
- [x] Add an internal canvas representation.
- [x] Enforce:
  - [x] exact palette use
  - [x] exact coordinate placement
  - [x] mask boundaries
  - [x] allowed transparency rules

### Drawing Commands
- [x] Add `paint-item-icon` or equivalent first drawing command.
- [x] Add a JSON input shape for agent-driven pixel operations.
- [x] Add output PNG export.
- [x] Add manifest integration for pixel-native outputs.

### Acceptance for Sprint 2
- [x] A small item icon can be created without any raster-image-generation step.
- [x] The output contains only exact pixel placements.
- [x] The tool can reject out-of-mask or out-of-palette drawing attempts.

## Sprint 3: Preview and Review Loop
Goal: make the outputs easy to inspect and iterate on.

### Preview Outputs
- [x] Add magnified preview rendering.
- [x] Add simple contact-sheet output for variants.
- [x] Add optional grid overlay for debugging masks and pixel placement.

### Review Metadata
- [x] Expand manifest review fields if needed:
  - [x] reviewer
  - [x] review timestamp
  - [x] approved/rejected reason
- [x] Add status transitions:
  - [x] draft
  - [x] approved
  - [x] rejected

### Acceptance for Sprint 3
- [x] A human can review an asset quickly from generated previews.
- [x] The manifest can record review outcomes cleanly.

## Sprint 4: Agent and MCP Integration
Goal: expose the engine to Codex-style agents without turning MCP into the core.

### Stable Tool Surface
- [x] Freeze a small CLI contract.
- [x] Document the CLI commands clearly for agents.
- [x] Add example requests and example pixel-op inputs.

### MCP Wrapper
- [x] Design a thin wrapper around the CLI or core library.
- [x] Expose only focused operations:
  - [x] `repair_generated_png`
  - [x] `paint_item_icon`
  - [x] `validate_texture`
  - [x] maybe `emit_manifest`
- [x] Keep provenance and path validation mandatory even through MCP.

### Acceptance for Sprint 4
- [x] A Codex-style agent can call the tool deterministically.
- [x] MCP use does not bypass masks, palettes, or provenance.

## Sprint 5: First Real Asset Families
Goal: prove the tool works on actual Verbum-shaped assets, not just abstract test cases.

### Asset Families
- [x] Book/manual cover flow
- [x] Simple item icon flow
- [x] Furniture/block texture flow

### Example Bundles
- [x] one book/manual example
- [x] one item example
- [x] one block/furniture example

### Acceptance for Sprint 5
- [x] At least three concrete assets can be produced through the tool flow.
- [x] Outputs land in correct module resource paths.
- [x] The assets are good enough for in-game review.

## Cross-Cutting Work

### Repo Fit
- [ ] Keep update obligations in sync if the workflow expands.
- [ ] Add attribution if any external algorithm/library is adopted.
- [ ] Keep this tool under `tools/asset-foundry`, not runtime code.

### Testing
- [ ] Add automated tests for:
  - [ ] schema validation
  - [ ] path validation
  - [ ] manifest validation
  - [ ] palette enforcement
  - [ ] alpha enforcement
  - [ ] mask enforcement

### Documentation
- [x] Keep README aligned to actual implemented capabilities.
- [ ] Add example docs only after commands are real.
- [ ] Avoid promising image-generation features before they exist.

## Definition of "Complete Enough"
- [x] Conversion path works on real PNG input and outputs true pixel art.
- [x] Pixel-native drawing works for at least one asset family.
- [x] Validation catches common mistakes automatically.
- [x] Provenance and review metadata are preserved.
- [x] A Codex-style agent can use the tool without bypassing repo guardrails.
