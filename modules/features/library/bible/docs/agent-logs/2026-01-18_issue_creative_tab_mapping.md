---
title: "Creative tab mapping missing for ItemDef.creativeTabKey"
date: 2026-01-18
type: issue
status: open
owner: codex-cli
capsule: library/bible
related: [assemblies/vanilla-plus/src/main/java/com/verbum_minecraft/vanilla/registry/MinecraftContentRegistrar.java, assemblies/visions/src/main/java/com/verbum_minecraft/visions/registry/MinecraftContentRegistrar.java]
tags: [wiring, assets]
---

## Context
Bible item uses `ItemDef.creativeTabKey = "books"` but assemblies do not map this to a Minecraft item group.

## Findings
`MinecraftContentRegistrar` contains a TODO for creative tab mapping; item may not appear in creative inventory without wiring support.

## Decision / Next Steps
Escalate to repo agent to implement creative tab mapping in assemblies.
