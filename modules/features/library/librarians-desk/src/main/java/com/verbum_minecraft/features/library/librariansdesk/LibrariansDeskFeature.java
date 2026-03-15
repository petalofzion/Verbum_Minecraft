package com.verbum_minecraft.features.library.librariansdesk;

import com.verbum_minecraft.api.content.BlockDef;
import com.verbum_minecraft.api.content.FeatureContext;
import com.verbum_minecraft.api.content.VerbumId;
import com.verbum_minecraft.spi.FeatureEntrypoint;

/**
 * Registers the Librarian's Desk utility block for Vocations.
 */
public class LibrariansDeskFeature implements FeatureEntrypoint {
    private static final VerbumId LIBRARIANS_DESK_ID = VerbumId.of("verbum", "librarians_desk");

    @Override
    public String id() {
        return "feature-librarians-desk";
    }

    @Override
    public void register(FeatureContext ctx) {
        ctx.content().acceptBlock(new BlockDef(
            LIBRARIANS_DESK_ID,
            2.5F,
            3.0F,
            "functional",
            "wood",
            LibrariansDeskInteractionHandler.class.getName()
        ));
    }

    @Override
    public void init() {
    }
}
