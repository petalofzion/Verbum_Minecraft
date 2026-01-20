package com.verbum_minecraft.features.library.bookcore;

import com.verbum_minecraft.api.content.FeatureContext;
import com.verbum_minecraft.spi.FeatureEntrypoint;

/**
 * Book Core entrypoint for library-backed book support.
 * Capsule logic remains pure; platform wiring lives in assemblies.
 */
public class BookCoreFeature implements FeatureEntrypoint {
    @Override
    public String id() {
        return "feature-book-core";
    }

    @Override
    public void register(FeatureContext ctx) {
        // Book library wiring is handled by assemblies; no content registration yet.
    }

    @Override
    public void init() {
    }
}
