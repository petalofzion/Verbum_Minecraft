# Assembly Wiring Map (Repo Agent)

This document maps **core contracts** to **Fabric/Minecraft wiring**.
Assemblies are the only layer allowed to touch Minecraft/Fabric classes.

Wiring coverage is tracked in `docs/contracts/contract_wiring.tsv` and summarized in the auto-generated `docs/contracts/CONTRACT_INDEX.md`.

## Feature Discovery & Registration Flow
**Entry points:**
- `assemblies/vanilla-plus/src/main/java/com/verbum_minecraft/vanilla/VerbumVanilla.java`
- `assemblies/visions/src/main/java/com/verbum_minecraft/visions/VerbumVisions.java`

**Flow:**
1. Assembly creates a `FeatureContext` backed by a `ContentSink`.
2. Features are discovered via `ServiceLoader<FeatureEntrypoint>`.
3. `FeatureEntrypoint.register(ctx)` is called for content registration.
4. `FeatureEntrypoint.init()` is called for pure logic init.

## ContentSink Wiring
**Implementations:**
- `assemblies/vanilla-plus/src/main/java/com/verbum_minecraft/vanilla/registry/MinecraftContentRegistrar.java`
- `assemblies/visions/src/main/java/com/verbum_minecraft/visions/registry/MinecraftContentRegistrar.java`

**Current mapping:**
- `ItemDef` → `Item.Properties` → `Registry.register(BuiltInRegistries.ITEM, id, item)`
- `maxStackSize`, `fireproof`, `rarityOrdinal` are mapped directly.
- `creativeTabKey` is **not wired yet** (TODO).
- `BookDef` → `WrittenBookItem` + `DataComponents.WRITTEN_BOOK_CONTENT` (vanilla book limits apply).

## Resource Expectations (Items)
Capsule resources must exist for any item:
- `assets/<namespace>/models/item/<path>.json`
- `assets/<namespace>/textures/item/<path>.png`
- `assets/<namespace>/lang/en_us.json`

Missing assets result in the purple/black missing‑texture cube.

**Resource loading:** Assemblies merge capsule `src/main/resources` into the final mod jar so client resource packs can see feature assets (excluding `META-INF/services/**`, which stays in module jars). If assets are missing in-game, this is the first wiring check.

## Resource Expectations (Books)
Written books also require:
- `assets/<namespace>/books/<path>.txt` (UTF‑8; pages split by `---PAGE---`)

Wiring enforces vanilla limits (`WrittenBookContent.PAGE_LENGTH`, `WritableBookContent.MAX_PAGES`).

## When Adding New Contracts
If you introduce new contracts in `modules/core/api` or `modules/core/spi`:
1. Implement the Fabric/Minecraft wiring in `assemblies/*`.
2. Update `docs/contracts/CORE_API.md` with usage guidance.
3. Update this document with the wiring path.
