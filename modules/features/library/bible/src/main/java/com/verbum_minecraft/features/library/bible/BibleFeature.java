package com.verbum_minecraft.features.library.bible;

import com.verbum_minecraft.api.content.BookDef;
import com.verbum_minecraft.api.content.FeatureContext;
import com.verbum_minecraft.api.content.ItemDef;
import com.verbum_minecraft.api.content.VerbumId;
import com.verbum_minecraft.spi.FeatureEntrypoint;

/**
 * Implementation of the Bible feature.
 * Discovered via ServiceLoader.
 */
public class BibleFeature implements FeatureEntrypoint {
    private static final VerbumId BIBLE_ID = VerbumId.of("verbum", "bible");

    @Override
    public String id() {
        return "feature-bible";
    }

    @Override
    public void register(FeatureContext ctx) {
        ItemDef item = new ItemDef(
            BIBLE_ID,
            1,
            false,
            ItemDef.RARITY_UNCOMMON,
            "books"
        );

        ctx.content().acceptBook(new BookDef(
            item,
            "The Holy Bible",
            "Verbum",
            null
        ));
    }

    @Override
    public void init() {
    }
}

    
