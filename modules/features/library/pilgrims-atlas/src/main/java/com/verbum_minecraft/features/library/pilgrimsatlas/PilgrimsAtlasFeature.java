package com.verbum_minecraft.features.library.pilgrimsatlas;

import com.verbum_minecraft.api.content.FeatureContext;
import com.verbum_minecraft.api.content.ItemDef;
import com.verbum_minecraft.api.content.LibraryBookDef;
import com.verbum_minecraft.api.content.VerbumId;
import com.verbum_minecraft.spi.FeatureEntrypoint;

/**
 * Registers the Pilgrim's Atlas manual for the Visions profile.
 */
public class PilgrimsAtlasFeature implements FeatureEntrypoint {
    private static final VerbumId PILGRIMS_ATLAS_ID = VerbumId.of("verbum", "pilgrims_atlas");
    private static final String PILGRIMS_ATLAS_BOOK_ID = PILGRIMS_ATLAS_ID.namespace()
        + ":"
        + PILGRIMS_ATLAS_ID.path()
        + "@visions";

    @Override
    public String id() {
        return "feature-pilgrims-atlas";
    }

    @Override
    public void register(FeatureContext ctx) {
        ItemDef item = new ItemDef(
            PILGRIMS_ATLAS_ID,
            1,
            false,
            ItemDef.RARITY_UNCOMMON,
            "books"
        );

        ctx.content().acceptLibraryBook(new LibraryBookDef(
            item,
            PILGRIMS_ATLAS_BOOK_ID,
            "Pilgrim's Atlas",
            "Verbum Cartographium",
            null
        ));
    }

    @Override
    public void init() {
    }
}
