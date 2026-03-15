package com.verbum_minecraft.features.library.bookofhours;

import com.verbum_minecraft.api.content.FeatureContext;
import com.verbum_minecraft.api.content.ItemDef;
import com.verbum_minecraft.api.content.LibraryBookDef;
import com.verbum_minecraft.api.content.VerbumId;
import com.verbum_minecraft.spi.FeatureEntrypoint;

/**
 * Book of Hours profile manual for the Vocations line.
 */
public class BookOfHoursFeature implements FeatureEntrypoint {
    private static final VerbumId BOOK_OF_HOURS_ID = VerbumId.of("verbum", "book_of_hours");
    private static final String BOOK_OF_HOURS_BOOK_ID = BOOK_OF_HOURS_ID.namespace()
        + ":"
        + BOOK_OF_HOURS_ID.path()
        + "@vocations";

    @Override
    public String id() {
        return "feature-book-of-hours";
    }

    @Override
    public void register(FeatureContext ctx) {
        ItemDef item = new ItemDef(
            BOOK_OF_HOURS_ID,
            1,
            false,
            ItemDef.RARITY_UNCOMMON,
            "books"
        );

        ctx.content().acceptLibraryBook(new LibraryBookDef(
            item,
            BOOK_OF_HOURS_BOOK_ID,
            "Book of Hours",
            "Vocations Almanac",
            null
        ));
    }

    @Override
    public void init() {
    }
}
