package com.verbum_minecraft.features.library.bookenhancement;

import com.verbum_minecraft.api.content.FeatureContext;
import com.verbum_minecraft.spi.FeatureEntrypoint;

/**
 * Book enhancement entrypoint for library-backed book support.
 * Capsule logic remains pure; platform wiring lives in assemblies.
 */
public class BookEnhancementFeature implements FeatureEntrypoint {
    @Override
    public String id() {
        return "feature-book-enhancement";
    }

    @Override
    public void register(FeatureContext ctx) {
        // Book library wiring is handled by assemblies; no content registration yet.
    }

    @Override
    public void init() {
    }
}
