package com.verbum_minecraft.features.library.ruleofashes;

import com.verbum_minecraft.api.content.FeatureContext;
import com.verbum_minecraft.api.content.ItemDef;
import com.verbum_minecraft.api.content.LibraryBookDef;
import com.verbum_minecraft.api.content.VerbumId;
import com.verbum_minecraft.spi.FeatureEntrypoint;

public class RuleOfAshesFeature implements FeatureEntrypoint {
    private static final VerbumId RULE_OF_ASHES_ID = VerbumId.of("verbum", "rule_of_ashes");
    private static final String RULE_OF_ASHES_BOOK_ID = RULE_OF_ASHES_ID.namespace()
        + ":" + RULE_OF_ASHES_ID.path() + "@vorago";

    @Override
    public String id() {
        return "feature-rule-of-ashes";
    }

    @Override
    public void register(FeatureContext ctx) {
        ItemDef item = new ItemDef(
            RULE_OF_ASHES_ID,
            1,
            false,
            ItemDef.RARITY_UNCOMMON,
            "books"
        );

        ctx.content().acceptLibraryBook(new LibraryBookDef(
            item,
            RULE_OF_ASHES_BOOK_ID,
            "Rule of Ashes",
            "Vorago Manual",
            null
        ));
    }

    @Override
    public void init() {
    }
}
