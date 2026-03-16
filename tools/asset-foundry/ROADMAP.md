# Asset Foundry Roadmap

The preset milestone is complete.

Current milestone:
- neutral PNG analysis artifacts
- semantic template authoring on top of those artifacts
- exact-base vanilla family templates
- promote generated assets into reusable templates
- true template variations that remap base-raster pixel groups instead of painting overlays

## Current End State
Asset Foundry should let you:
- take an existing PNG and turn it into a reusable template
- keep exact base-raster output when no edits are applied
- inspect and review a mechanically neutral analysis artifact
- define or refine semantic regions/groups on top of that base
- generate coherent variations from the same template through both engines
- repeat that flow for books and other vanilla-style item families

## Major Work Streams

### 1. Raster-Backed Template Layer
Templates are now the real family unit:
- base raster
- region map
- edit rules
- engine support

### 2. Neutral Image Analysis
The tool should inspect a PNG and emit only mechanical facts:
- connected components
- color inventory
- tone ramps
- detail candidates
- zone candidates
- topology maps

Meaning is added later during template authoring.

### 3. Template Authoring and Family-Variant Workflow
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
- load a vanilla or generated base image into a review workflow
- refine analysis proposals with less manual JSON editing
- scale the same family approach across more item classes without ad hoc setup
- onboard more vanilla families using the same pixel-group reskin workflow

## Scope Discipline
Do not start the 3D model foundry implementation in this milestone.
Keep the current work focused on 2D template analysis, refinement, and family variation.
