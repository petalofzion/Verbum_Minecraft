# Asset Foundry Roadmap

The previous milestone is complete:
- preview-first PNG conversion works
- pixel-native item drawing works
- validation, manifests, and the thin MCP wrapper exist

This roadmap is now for the **preset/template upgrade**.

## Next End State
Asset Foundry should support reusable preset families that both engines can load and obey.

That means:
- one base preset can define a whole family such as vanilla-style books
- rough PNG conversion can be constrained by the preset
- pixel-native drawing can paint by region and role instead of only raw coordinates
- approved base assets can become reusable templates for fast variation generation

## Major Work Streams

### 1. Preset Family Layer
Add a new preset schema and preset loader above asset types and masks.

### 2. Role-Aware Palettes
Upgrade palettes so presets can refer to semantic color roles, not just flat lists.

### 3. Region-Aware Engines
Teach both the PNG-ingest path and the pixel-native path to work through preset regions and region rules.

### 4. Family Variation Workflow
Support turning a successful base asset into a reusable preset and generating variants from it.

### 5. First-Class Book Family
Implement the first robust family:
- vanilla-like book preset
- manual/codex preset
- reusable Bible/manual variation flow

## Near-Term Target
The next "complete enough" version should let you:
- create a preset from a base asset concept
- load the preset by id
- generate multiple consistent book variations from it
- use the same preset in both the conversion and drawing engines

## Scope Discipline
Do not start the 3D model foundry in this milestone.
Finish the 2D preset/template system first.
