package com.verbum_minecraft.features.library.dustydevotional;

import com.verbum_minecraft.api.content.FeatureContext;
import com.verbum_minecraft.api.content.ItemDef;
import com.verbum_minecraft.api.content.LibraryBookDef;
import com.verbum_minecraft.api.content.VerbumId;
import com.verbum_minecraft.spi.FeatureEntrypoint;

/**
 * Registers the Dusty Devotional manual for the Veritas profile.
 */
public class DustyDevotionalFeature implements FeatureEntrypoint {
    private static final VerbumId DUSTY_DEVOTIONAL_ID = VerbumId.of("verbum", "dusty_devotional");
    private static final String DUSTY_DEVOTIONAL_BOOK_ID = DUSTY_DEVOTIONAL_ID.namespace()
        + ":"
        + DUSTY_DEVOTIONAL_ID.path()
        + "@veritas";

    @Override
    public String id() {
        return "feature-dusty-devotional";
    }

    @Override
    public void register(FeatureContext ctx) {
        ItemDef item = new ItemDef(
            DUSTY_DEVOTIONAL_ID,
            1,
            false,
            ItemDef.RARITY_UNCOMMON,
            "books"
        );

        ctx.content().acceptLibraryBook(new LibraryBookDef(
            item,
            DUSTY_DEVOTIONAL_BOOK_ID,
            "Dusty Devotional",
            "Verbum",
            null
        ));
    }

    @Override
    public void init() {
    }
}
