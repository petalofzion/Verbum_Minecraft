# Core API Contract Catalog (Capsule Reference)

This is the **canonical list** of core contracts that feature capsules may use.
If you need capabilities not listed here, run a **capability sweep**, log it in the capsule `docs/agent-logs/`, and stop.

Repo agents: when you add a new capsule-usable contract or make an unwired contract available, update this file in the same change as the code and refresh the generated wiring index.

For wiring coverage and status, see the auto-generated `docs/contracts/CONTRACT_INDEX.md`.
Repo agents maintain wiring notes in `docs/contracts/contract_wiring.tsv` and regenerate the index with `tools/scripts/update_contract_index.sh`.

## Content Registration (Capsule Path)
**Flow:** `FeatureEntrypoint.register()` → `FeatureContext.content()` → `ContentSink.acceptItem(ItemDef)` / `ContentSink.acceptBlock(BlockDef)` / `ContentSink.acceptBook(BookDef)` / `ContentSink.acceptLibraryBook(LibraryBookDef)`

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
- `acceptBlock(BlockDef def)` for placeable blocks with item forms.
- `acceptBook(BookDef def)` for written book items.
- `acceptLibraryBook(LibraryBookDef def)` for library-backed books.

### com.verbum_minecraft.api.content.ItemDef
**Purpose:** Pure data definition for an item.

**Fields:**
- `VerbumId id`
- `int maxStackSize`
- `boolean fireproof`
- `int rarityOrdinal` (`RARITY_*` constants)
- `String creativeTabKey` (wired in assemblies; see `docs/wiring/ASSEMBLY_WIRING.md`)

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

### com.verbum_minecraft.api.content.BlockDef
**Purpose:** Pure data definition for a placeable block with an item form.

**Fields:**
- `VerbumId id`
- `float destroyTime`
- `float explosionResistance`
- `String creativeTabKey`
- `String soundTypeKey` (`wood`, `stone`, `metal`, `glass`, `gravel`, `wool`, `sand`)
- `String interactionHandlerClass` (optional pure handler class name for assembly-side block use wiring)

**Example:**
```java
ctx.content().acceptBlock(new BlockDef(
    VerbumId.of("verbum", "librarians_desk"),
    2.5F,
    3.0F,
    "functional",
    "wood",
    "com.verbum_minecraft.features.library.librariansdesk.LibrariansDeskInteractionHandler"
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

### com.verbum_minecraft.api.content.LibraryBookDef
**Purpose:** Pure data definition for a library-backed written book that reads large content from packaged resources.

**Fields:**
- `ItemDef item`
- `String bookId` (`namespace:path[@edition]`)
- `String title`
- `String author`
- `String contentResourcePath` (optional override; defaults to `assets/<namespace>/books/<path>.txt`)

**Example:**
```java
ItemDef item = new ItemDef(
    VerbumId.of("verbum", "bible"),
    1,
    false,
    ItemDef.RARITY_UNCOMMON,
    "books"
);
ctx.content().acceptLibraryBook(new LibraryBookDef(
    item,
    "verbum:bible",
    "The Holy Bible",
    "Douay-Rheims",
    null
));
```

### com.verbum_minecraft.api.content.VerbumId
**Purpose:** Pure identifier (`namespace:path`).

**Use:** `VerbumId.of("verbum", "bible")`

### com.verbum_minecraft.api.content.BlockInteractionHandler
**Purpose:** Pure capsule-owned block interaction hook called by assembly wiring.

**Use:** implement `use(BlockInteractionContext context)` and return a `BlockInteractionResult`.

### com.verbum_minecraft.api.content.BlockInteractionContext
**Purpose:** Pure interaction input describing the held item and basic player posture.

**Fields:**
- `String heldItemId`
- `boolean sneaking`
- `boolean creativeMode`

### com.verbum_minecraft.api.content.BlockInteractionResult
**Purpose:** Pure interaction output consumed by assembly wiring.

**Fields:**
- `boolean handled`
- `boolean consumeHeldItem`
- `List<ItemGrant> grants`
- `String message` (optional status text)

**Helpers:**
- `BlockInteractionResult.pass()`
- `BlockInteractionResult.handled(...)`

### com.verbum_minecraft.api.content.ItemGrant
**Purpose:** Pure item-stack grant description used by block interaction results.

**Fields:**
- `String itemId`
- `int count`

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
- `src/main/resources/assets/<namespace>/items/<path>.json`
- `src/main/resources/assets/<namespace>/models/item/<path>.json`
- `src/main/resources/assets/<namespace>/textures/item/<path>.png`
- `src/main/resources/assets/<namespace>/lang/en_us.json`

**Lang entry:** `item.<namespace>.<path>` → display name

**1.21.11 note:** The `items/<path>.json` file is required in 1.21.11 to map
the item to its model. In older versions the `models/item/<path>.json` alone
was sufficient. Missing the `items/<path>.json` file produces missing-texture
items even when the model and PNG exist.

## Asset Checklist (for BookDef)
Book registration also requires:
- `src/main/resources/assets/<namespace>/books/<path>.txt`

## Asset Checklist (for LibraryBookDef)
Library-backed books also require:
- `src/main/resources/assets/<namespace>/books/<path>.txt`

## If You Need More
If you need new contracts (e.g., custom item behavior, GUI, book pages):
1. List all needed contracts in one log (capability sweep).
2. Stop and notify the repo agent.
