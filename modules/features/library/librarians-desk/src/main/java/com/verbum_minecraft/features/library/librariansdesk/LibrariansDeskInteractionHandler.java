package com.verbum_minecraft.features.library.librariansdesk;

import com.verbum_minecraft.api.content.BlockInteractionContext;
import com.verbum_minecraft.api.content.BlockInteractionHandler;
import com.verbum_minecraft.api.content.BlockInteractionResult;
import com.verbum_minecraft.api.content.ItemGrant;
import java.util.List;
import java.util.Set;

/**
 * Salvage-only interaction rules for Librarian's Desk.
 */
public final class LibrariansDeskInteractionHandler implements BlockInteractionHandler {
    private static final String BOOK_ID = "minecraft:book";
    private static final String WRITABLE_BOOK_ID = "minecraft:writable_book";
    private static final String WRITTEN_BOOK_ID = "minecraft:written_book";
    private static final String PAPER_ID = "minecraft:paper";
    private static final String LEATHER_ID = "minecraft:leather";
    private static final int SALVAGE_PAPER_COUNT = 3;

    private static final Set<String> MANUAL_BOOK_IDS = Set.of(
        "verbum:bible",
        "verbum:book_of_hours",
        "verbum:dusty_devotional",
        "verbum:pilgrims_atlas",
        "verbum:rule_of_ashes"
    );

    @Override
    public BlockInteractionResult use(BlockInteractionContext context) {
        String heldItemId = context.heldItemId();
        if (heldItemId == null || heldItemId.isBlank()) {
            return BlockInteractionResult.pass();
        }

        if (BOOK_ID.equals(heldItemId)) {
            return salvageWithBinding();
        }

        if (WRITABLE_BOOK_ID.equals(heldItemId) || WRITTEN_BOOK_ID.equals(heldItemId)) {
            if (!context.sneaking()) {
                return BlockInteractionResult.handled(false, List.of(), "Sneak to salvage written books.");
            }
            return salvagePaperOnly("Recovered paper.");
        }

        if (MANUAL_BOOK_IDS.contains(heldItemId)) {
            if (!context.sneaking()) {
                return BlockInteractionResult.handled(false, List.of(), "Sneak to salvage manuals.");
            }
            return salvagePaperOnly("Recovered paper.");
        }

        return BlockInteractionResult.pass();
    }

    private static BlockInteractionResult salvageWithBinding() {
        return BlockInteractionResult.handled(
            true,
            List.of(
                new ItemGrant(PAPER_ID, SALVAGE_PAPER_COUNT),
                new ItemGrant(LEATHER_ID, 1)
            ),
            "Recovered paper and binding."
        );
    }

    private static BlockInteractionResult salvagePaperOnly(String message) {
        return BlockInteractionResult.handled(
            true,
            List.of(new ItemGrant(PAPER_ID, SALVAGE_PAPER_COUNT)),
            message
        );
    }
}
