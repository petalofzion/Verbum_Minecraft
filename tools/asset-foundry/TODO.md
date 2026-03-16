# Asset Foundry TODO

This is the detailed implementation plan for `tools/asset-foundry`.

The two primary goals are:
1. convert rough PNGs into proper pixel art for Minecraft assets
2. support pixel-native drawing where an agent paints actual pixels under strict rules

## Sprint 1: Conversion Path MVP
Goal: the tool can take an input PNG and emit a real pixel-art output that avoids mixels and pseudo-pixel blur.

### Request and Spec Expansion
- [ ] Add a source-image input field to the request model or a dedicated conversion command input.
- [ ] Add asset-type rules for:
  - [ ] target dimensions
  - [ ] palette source
  - [ ] transparency policy
  - [ ] mixel tolerance policy
  - [ ] readability hints
- [ ] Add one or two more real asset types beyond current scaffolds:
  - [ ] `book_cover_16`
  - [ ] `book_cover_32`
  - [ ] `simple_block_face_16`

### Conversion Engine
- [ ] Choose the first image-processing dependency path and review license fit.
- [ ] Implement image load and export.
- [ ] Implement dimension normalization:
  - [ ] resize to exact target canvas
  - [ ] preserve nearest-neighbor semantics where appropriate
- [ ] Implement palette quantization:
  - [ ] map to explicit palette file
  - [ ] reject uncontrolled colors
- [ ] Implement alpha cleanup:
  - [ ] remove unintended semi-transparent haze
  - [ ] snap alpha according to asset type
- [ ] Implement anti-mixel cleanup:
  - [ ] detect isolated off-palette fuzz
  - [ ] normalize noisy edge transitions
  - [ ] avoid turning intended contrast into mush

### Conversion Commands
- [ ] Add `repair-generated-png` CLI command.
- [ ] Add output-path selection consistent with the manifest/request flow.
- [ ] Add dry-run mode that reports what would be changed.
- [ ] Add optional side-by-side before/after preview output.

### Validation
- [ ] Add `validate-texture` CLI command.
- [ ] Validate:
  - [ ] dimensions
  - [ ] palette membership
  - [ ] alpha policy
  - [ ] forbidden pixels outside the mask
  - [ ] output path conventions
- [ ] Emit clear diagnostics instead of generic pass/fail only.

### Acceptance for Sprint 1
- [ ] A rough PNG can be converted into a true pixel-art output.
- [ ] The output is visibly cleaner and Minecraft-usable.
- [ ] The validator can explain why an output fails.
- [ ] The tool emits provenance for the conversion.

## Sprint 2: Pixel-Native Drawing MVP
Goal: the tool can generate pixel art directly through exact pixel placement and constrained rules.

### Mask System
- [ ] Replace placeholder mask metadata with a real mask format.
- [ ] Define mask semantics:
  - [ ] allowed pixels
  - [ ] forbidden pixels
  - [ ] optional zones
  - [ ] symmetry rules
  - [ ] reserved highlight/shadow regions
- [ ] Add first real masks for:
  - [ ] simple item icon
  - [ ] book cover
  - [ ] bench/block item silhouette

### Drawing Model
- [ ] Define a pixel-operation schema:
  - [ ] set pixel
  - [ ] fill region
  - [ ] shade zone
  - [ ] mirror/symmetry helper
- [ ] Add an internal canvas representation.
- [ ] Enforce:
  - [ ] exact palette use
  - [ ] exact coordinate placement
  - [ ] mask boundaries
  - [ ] allowed transparency rules

### Drawing Commands
- [ ] Add `paint-item-icon` or equivalent first drawing command.
- [ ] Add a JSON input shape for agent-driven pixel operations.
- [ ] Add output PNG export.
- [ ] Add manifest integration for pixel-native outputs.

### Acceptance for Sprint 2
- [ ] A small item icon can be created without any raster-image-generation step.
- [ ] The output contains only exact pixel placements.
- [ ] The tool can reject out-of-mask or out-of-palette drawing attempts.

## Sprint 3: Preview and Review Loop
Goal: make the outputs easy to inspect and iterate on.

### Preview Outputs
- [ ] Add magnified preview rendering.
- [ ] Add simple contact-sheet output for variants.
- [ ] Add optional grid overlay for debugging masks and pixel placement.

### Review Metadata
- [ ] Expand manifest review fields if needed:
  - [ ] reviewer
  - [ ] review timestamp
  - [ ] approved/rejected reason
- [ ] Add status transitions:
  - [ ] draft
  - [ ] approved
  - [ ] rejected

### Acceptance for Sprint 3
- [ ] A human can review an asset quickly from generated previews.
- [ ] The manifest can record review outcomes cleanly.

## Sprint 4: Agent and MCP Integration
Goal: expose the engine to Codex-style agents without turning MCP into the core.

### Stable Tool Surface
- [ ] Freeze a small CLI contract.
- [ ] Document the CLI commands clearly for agents.
- [ ] Add example requests and example pixel-op inputs.

### MCP Wrapper
- [ ] Design a thin wrapper around the CLI or core library.
- [ ] Expose only focused operations:
  - [ ] `repair_generated_png`
  - [ ] `paint_item_icon`
  - [ ] `validate_texture`
  - [ ] maybe `emit_manifest`
- [ ] Keep provenance and path validation mandatory even through MCP.

### Acceptance for Sprint 4
- [ ] A Codex-style agent can call the tool deterministically.
- [ ] MCP use does not bypass masks, palettes, or provenance.

## Sprint 5: First Real Asset Families
Goal: prove the tool works on actual Verbum-shaped assets, not just abstract test cases.

### Asset Families
- [ ] Book/manual cover flow
- [ ] Simple item icon flow
- [ ] Furniture/block texture flow

### Example Bundles
- [ ] one book/manual example
- [ ] one item example
- [ ] one block/furniture example

### Acceptance for Sprint 5
- [ ] At least three concrete assets can be produced through the tool flow.
- [ ] Outputs land in correct module resource paths.
- [ ] The assets are good enough for in-game review.

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
- [ ] Keep README aligned to actual implemented capabilities.
- [ ] Add example docs only after commands are real.
- [ ] Avoid promising image-generation features before they exist.

## Definition of "Complete Enough"
- [ ] Conversion path works on real PNG input and outputs true pixel art.
- [ ] Pixel-native drawing works for at least one asset family.
- [ ] Validation catches common mistakes automatically.
- [ ] Provenance and review metadata are preserved.
- [ ] A Codex-style agent can use the tool without bypassing repo guardrails.
