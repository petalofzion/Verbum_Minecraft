# Assembly Wiring Map (Repo Agent)

This document maps **core contracts** to **Fabric/Minecraft wiring**.
Assemblies are the only layer allowed to touch Minecraft/Fabric classes.

Wiring coverage is tracked in `docs/contracts/contract_wiring.tsv` and summarized in the auto-generated `docs/contracts/CONTRACT_INDEX.md`.

## Feature Discovery & Registration Flow
**Entry points:**
- `assemblies/veritas/src/main/java/com/verbum_minecraft/veritas/VerbumVeritas.java`
- `assemblies/vocations/src/main/java/com/verbum_minecraft/vocations/VerbumVocations.java`
- `assemblies/visions/src/main/java/com/verbum_minecraft/visions/VerbumVisions.java`
- `assemblies/vorago/src/main/java/com/verbum_minecraft/vorago/VerbumVorago.java`

**Flow:**
1. Assembly creates a `FeatureContext` backed by a `ContentSink`.
2. Features are discovered via `ServiceLoader<FeatureEntrypoint>`.
3. `FeatureEntrypoint.register(ctx)` is called for content registration.
4. `FeatureEntrypoint.init()` is called for pure logic init.

## ContentSink Wiring
**Implementations:**
- `assemblies/veritas/src/main/java/com/verbum_minecraft/veritas/registry/MinecraftContentRegistrar.java`
- `assemblies/vocations/src/main/java/com/verbum_minecraft/vocations/registry/MinecraftContentRegistrar.java`
- `assemblies/visions/src/main/java/com/verbum_minecraft/visions/registry/MinecraftContentRegistrar.java`
- `assemblies/vorago/src/main/java/com/verbum_minecraft/vorago/registry/MinecraftContentRegistrar.java`

**Current mapping:**
- `ItemDef` → `Item.Properties` → `Registry.register(BuiltInRegistries.ITEM, id, item)`
- `BlockDef` → `BlockBehaviour.Properties` → `Registry.register(BuiltInRegistries.BLOCK, id, block)` plus a same-id `BlockItem`
  - If `workstationBehaviorId` is set, assemblies resolve a `BlockWorkstationBehaviorProvider` through SPI and create a `WorkstationFeatureBlock`.
  - If `interactionBehaviorId` is set, assemblies resolve a `BlockInteractionBehaviorProvider` through SPI and create an `InteractiveFeatureBlock`.
- `maxStackSize`, `fireproof`, `rarityOrdinal` are mapped directly.
- `creativeTabKey` is wired via Fabric ItemGroupEvents.
  - Supported keys: `books`, `tools`, `ingredients`, `combat`, `food`, `building`, `functional`, `redstone`, `spawn_eggs`
  - Mapping uses vanilla creative tabs (e.g., `books` → `TOOLS_AND_UTILITIES`).
- `BookDef` → `WrittenBookItem` + `DataComponents.WRITTEN_BOOK_CONTENT` (vanilla book limits apply).
- `LibraryBookDef` → library-backed `WrittenBookItem` that opens `BookViewScreen` with pages loaded from the Book Enhancement library (offline, classpath resources). Item content uses a tiny placeholder page to avoid large NBT payloads. The client paginates text to `BookViewScreen` text width/height so pages are not truncated.
- `BlockInteractionHandler` → generic `InteractiveFeatureBlock` wiring in assemblies. The assembly constructs a pure `BlockInteractionContext` from held item id / sneaking / creative mode, calls the capsule-owned handler, and applies `BlockInteractionResult` grants or messages server-side.
- `BlockWorkstationHandler` → workstation wiring in assemblies.
  - Veritas currently uses a direct `WorkstationFeatureBlock` action path.
  - Vocations, Visions, and Vorago route workstation blocks through `LibrariansDeskWorkstationMenu` + client screen registration so explicit actions (`salvage_all`, `copy_books`, `edit_player_book`, `write_draft`) are dispatched from a real menu/container flow.
  - Assembly wiring applies `WorkstationSlotDelta` consumption for batch operations, resolves `ItemGrant` outputs, and materializes `WorkstationPlayerBookGrant` outputs as player-owned `minecraft:written_book` stacks without mutating shipped library resources.
- `BlockInteractionBehaviorProvider` / `BlockWorkstationBehaviorProvider` → SPI seam used by assemblies to resolve capsule-owned behavior ids without exposing implementation class names through `modules/core/api`.

## UI Modifications
### Library Book Reader Enhancements
- Adds page jump + bookmark controls to the book reader UI.
- Opens `BookViewScreen` with library-backed pages, paginated for the current text area.
- Assembly files:
  - `assemblies/veritas/src/main/java/com/verbum_minecraft/veritas/client/LibraryBookClient.java`
  - `assemblies/veritas/src/main/java/com/verbum_minecraft/veritas/client/LibraryBookView.java`
  - `assemblies/veritas/src/main/java/com/verbum_minecraft/veritas/client/LibraryBookBookmarks.java`
  - `assemblies/vocations/src/main/java/com/verbum_minecraft/vocations/client/LibraryBookClient.java`
  - `assemblies/vocations/src/main/java/com/verbum_minecraft/vocations/client/LibraryBookView.java`
  - `assemblies/vocations/src/main/java/com/verbum_minecraft/vocations/client/LibraryBookBookmarks.java`
  - `assemblies/vocations/src/main/java/com/verbum_minecraft/vocations/client/LibrariansDeskWorkstationClient.java`
  - `assemblies/vocations/src/main/java/com/verbum_minecraft/vocations/client/LibrariansDeskWorkstationScreen.java`
  - `assemblies/visions/src/main/java/com/verbum_minecraft/visions/client/LibraryBookClient.java`
  - `assemblies/visions/src/main/java/com/verbum_minecraft/visions/client/LibraryBookView.java`
  - `assemblies/visions/src/main/java/com/verbum_minecraft/visions/client/LibraryBookBookmarks.java`
  - `assemblies/visions/src/main/java/com/verbum_minecraft/visions/client/LibrariansDeskWorkstationClient.java`
  - `assemblies/visions/src/main/java/com/verbum_minecraft/visions/client/LibrariansDeskWorkstationScreen.java`
  - `assemblies/vorago/src/main/java/com/verbum_minecraft/vorago/client/LibraryBookClient.java`
  - `assemblies/vorago/src/main/java/com/verbum_minecraft/vorago/client/LibraryBookView.java`
  - `assemblies/vorago/src/main/java/com/verbum_minecraft/vorago/client/LibraryBookBookmarks.java`
  - `assemblies/vorago/src/main/java/com/verbum_minecraft/vorago/client/LibrariansDeskWorkstationClient.java`
  - `assemblies/vorago/src/main/java/com/verbum_minecraft/vorago/client/LibrariansDeskWorkstationScreen.java`

## Resource Expectations (Items)
Capsule resources must exist for any item:
- `assets/<namespace>/items/<path>.json`
- `assets/<namespace>/models/item/<path>.json`
- `assets/<namespace>/textures/item/<path>.png`
- `assets/<namespace>/lang/en_us.json`

Missing assets result in the purple/black missing‑texture cube.

## Resource Expectations (Blocks)
Placeable blocks also require:
- `assets/<namespace>/blockstates/<path>.json`
- `assets/<namespace>/models/block/<path>.json`
- `assets/<namespace>/models/item/<path>.json`
- `assets/<namespace>/items/<path>.json`
- `assets/<namespace>/lang/en_us.json`

**26.1-pre-3 note:** The `items/<path>.json` file is required to map the item to
its model. Missing it will show the missing-texture cube even if the model and
texture files exist.

**Resource loading:** Assemblies merge capsule `src/main/resources` into the final mod jar so client resource packs can see feature assets (excluding `META-INF/services/**`, which stays in module jars). If assets are missing in-game, this is the first wiring check.
**Dev runs:** Assemblies also add module `src/main/resources` as resource roots for `runClient`/`runServer`, excluding `META-INF/services/**` to avoid duplicate `ServiceLoader` entries.

## Resource Expectations (Books)
Written books also require:
- `assets/<namespace>/books/<path>.txt` (UTF‑8; pages split by `---PAGE---`)

`BookDef` wiring enforces vanilla limits (`WrittenBookContent.PAGE_LENGTH`, `WritableBookContent.MAX_PAGES`).
`LibraryBookDef` uses Book Enhancement limits (`BookPageLimits`) instead.

## When Adding New Contracts
If you introduce new contracts in `modules/core/api` or `modules/core/spi`:
1. Implement the Fabric/Minecraft wiring in `assemblies/*`.
2. Update `docs/contracts/CORE_API.md` with usage guidance.
3. Update this document with the wiring path.
4. Keep implementation addressing out of `modules/core/api`; prefer symbolic ids resolved through SPI providers.
