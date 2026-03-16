# Asset Foundry Roadmap

The preset milestone is complete.

Current milestone:
- raster-backed templates
- image inspection and region analysis
- exact-base vanilla family templates
- promote generated assets into reusable templates

## Current End State
Asset Foundry should let you:
- take an existing PNG and turn it into a reusable template
- keep exact base-raster output when no edits are applied
- define or refine semantic regions on top of that base
- generate coherent variations from the same template through both engines
- repeat that flow for books and other vanilla-style item families

## Major Work Streams

### 1. Raster-Backed Template Layer
Templates are now the real family unit:
- base raster
- region map
- edit rules
- engine support

### 2. Image Analysis and Region Proposal
The tool should inspect a PNG, analyze connected regions/colors, and propose candidate editable regions before manual refinement.

### 3. Family-Variant Workflow
The same template should drive:
- PNG ingestion / constrained conversion
- pixel-native region editing
- promote-generated-asset workflows

### 4. Vanilla Family Onboarding
First-class families should include:
- vanilla book
- vanilla sword
- vanilla pickaxe
- vanilla bow

### 5. Future 3D Model Foundry
Only after the 2D template workflow feels stable:
- Minecraft model JSON generation
- UV-aware template families
- entity/block model foundry concepts

## Near-Term Target
The next "complete enough" version after this one should let you:
- load a vanilla or generated base image into a review UI or workflow
- refine region proposals with less manual JSON editing
- scale the same family approach across more item classes without ad hoc setup

## Scope Discipline
Do not start the 3D model foundry implementation in this milestone.
Keep the current work focused on 2D template analysis, refinement, and family variation.
