# Core API Contract Catalog (Capsule Reference)

This is the **canonical list** of core contracts that feature capsules may use.
If you need capabilities not listed here, run a **capability sweep**, log it in the capsule `docs/agent-logs/`, and stop.

For wiring coverage and status, see the auto-generated `docs/contracts/CONTRACT_INDEX.md`.
Repo agents maintain wiring notes in `docs/contracts/contract_wiring.tsv` and regenerate the index with `tools/scripts/update_contract_index.sh`.

## Content Registration (Capsule Path)
**Flow:** `FeatureEntrypoint.register()` → `FeatureContext.content()` → `ContentSink.acceptItem(ItemDef)` / `ContentSink.acceptBook(BookDef)`

### com.verbum_minecraft.spi.FeatureEntrypoint
**Purpose:** Standard entrypoint for feature capsules. Discovered via ServiceLoader.

**Use:**
- `id()` must be unique (e.g., `feature-bible`).
- `register(FeatureContext ctx)` is for **pure registration** (no Minecraft/Fabric classes).
- `init()` is for pure logic initialization after registration.

**Required file:** `src/main/resources/META-INF/services/com.verbum_minecraft.spi.FeatureEntrypoint`

### com.verbum_minecraft.api.content.FeatureContext
**Purpose:** Passed into `register()` to hand you a content sink.

**Use:** `ctx.content().acceptItem(...)`

### com.verbum_minecraft.api.content.ContentSink
**Purpose:** Sink for content definitions.

**Use:** 
- `acceptItem(ItemDef def)` for standard items.
- `acceptBook(BookDef def)` for written book items.

### com.verbum_minecraft.api.content.ItemDef
**Purpose:** Pure data definition for an item.

**Fields:**
- `VerbumId id`
- `int maxStackSize`
- `boolean fireproof`
- `int rarityOrdinal` (`RARITY_*` constants)
- `String creativeTabKey` (**not wired yet**; see repo wiring doc)

**Example:**
```java
ctx.content().acceptItem(new ItemDef(
    VerbumId.of("verbum", "bible"),
    1,
    false,
    ItemDef.RARITY_UNCOMMON,
    "books"
));
```

### com.verbum_minecraft.api.content.BookDef
**Purpose:** Pure data definition for a written book item backed by a resource file.

**Fields:**
- `ItemDef item` (all item properties)
- `String title` (plain string)
- `String author` (plain string)
- `String contentResourcePath` (optional; defaults to `assets/<namespace>/books/<path>.txt`)

**Resource format:**
- UTF‑8 text.
- Pages separated by a line containing `---PAGE---`.
- If no separator is present, the loader auto-chunks by page length.
- Pages beyond `WritableBookContent.MAX_PAGES` are truncated in wiring.

**Example:**
```java
ItemDef item = new ItemDef(
    VerbumId.of("verbum", "bible"),
    1,
    false,
    ItemDef.RARITY_UNCOMMON,
    "books"
);
ctx.content().acceptBook(new BookDef(
    item,
    "Holy Bible",
    "Verbum",
    null
));
```

### com.verbum_minecraft.api.content.VerbumId
**Purpose:** Pure identifier (`namespace:path`).

**Use:** `VerbumId.of("verbum", "bible")`

### com.verbum_minecraft.api.content.ContentType
**Purpose:** Enumerates content types (reserved for future expansion).

## Energy / Fluid (Kernel-Facing Interfaces)
These are available for features that interface with the kernel, but **do not yet have assembly wiring**.

### com.verbum_minecraft.api.energy.Energy
**Purpose:** High-performance energy storage interface (no boxing, no allocations).

### com.verbum_minecraft.api.fluid.Fluid
**Purpose:** High-performance fluid storage interface (no boxing, no allocations).

## Asset Checklist (for ItemDef)
Item registration requires assets in the capsule resources:
- `src/main/resources/assets/<namespace>/models/item/<path>.json`
- `src/main/resources/assets/<namespace>/textures/item/<path>.png`
- `src/main/resources/assets/<namespace>/lang/en_us.json`

**Lang entry:** `item.<namespace>.<path>` → display name

## Asset Checklist (for BookDef)
Book registration also requires:
- `src/main/resources/assets/<namespace>/books/<path>.txt`

## If You Need More
If you need new contracts (e.g., custom item behavior, GUI, book pages):
1. List all needed contracts in one log (capability sweep).
2. Stop and notify the repo agent.
