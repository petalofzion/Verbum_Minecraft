---
title: "Book library contracts and assembly hooks needed"
date: 2026-01-19
type: issue
status: resolved
owner: codex
capsule: library/book-core
related: [modules/core/api, modules/core/spi, assemblies/vanilla-plus, assemblies/visions, modules/features/library/bible]
tags: [api, wiring, docs]
---

## Context
Book Core targets library-backed books with large offline content. Current BookDef wiring only supports vanilla written book content limits.

## Findings
- No core contract for a lightweight book handle (`book_id`) stored on the item.
- No library resolver contract for large packaged content or pagination cache.
- Assembly wiring currently renders vanilla book content only.

## Decision / Next Steps
Capability sweep (requires repo-agent follow-up):
- Add core API/SPI contracts: `BookId`, `BookHandle`, `BookManifest`, `BookLibrary`/`BookResolver`, pagination cache interface.
- Add assembly hooks: attach `book_id` component to items, intercept book open to use library resolver, enforce hard limits.
- Define packaged content layout and loader (offline-first).

Resolved (repo agent):
- Added `LibraryBookDef` contract to core API and wiring in both assemblies.
- Assemblies now register library-backed book items and open a reader screen using `BookViewScreen`.
- Library loader uses Book Core pagination and classpath resources.
