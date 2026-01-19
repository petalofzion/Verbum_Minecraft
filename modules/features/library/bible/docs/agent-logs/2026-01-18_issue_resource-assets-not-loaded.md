---
title: "Bible assets not loaded in client resource pack"
date: 2026-01-18
type: issue
status: open
owner: codex
capsule: library/bible
related: [modules/features/library/bible/src/main/resources/assets/verbum/models/item/bible.json, modules/features/library/bible/src/main/resources/assets/verbum/textures/item/bible.png, assemblies/vanilla-plus/build/resources/main]
tags: [assets, wiring]
---

## Context
The Bible item renders as the missing-texture purple/black cube even after adding
`assets/verbum/models/item/bible.json` and `assets/verbum/textures/item/bible.png`.

## Findings
- Capsule assets exist in the feature jar, but the assembly resource output does not
  include any `assets/` directories (`assemblies/vanilla-plus/build/resources/main` only
  contains `fabric.mod.json`).
- `runClient` uses the assembly as the mod resource pack; resources inside nested
  module jars are not being surfaced to the resource pack, so models/textures are missing.
- Book pages load because book content is read via classloader, not via resource packs.

## Decision / Next Steps
Capability sweep (wiring needed outside capsule):
- Provide an assembly/build hook to merge feature module resources into the mod resource pack.
- Or treat feature modules as mod resources in dev/runtime (e.g., `modImplementation` or
  equivalent resource-root registration for module jars).

This requires repo-agent wiring/build changes; capsule cannot resolve.
