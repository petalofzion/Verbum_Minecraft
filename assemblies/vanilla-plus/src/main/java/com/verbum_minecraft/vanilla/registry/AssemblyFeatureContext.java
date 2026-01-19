package com.verbum_minecraft.vanilla.registry;

import com.verbum_minecraft.api.content.ContentSink;
import com.verbum_minecraft.api.content.FeatureContext;

public class AssemblyFeatureContext implements FeatureContext {
    private final ContentSink contentSink;

    public AssemblyFeatureContext(ContentSink contentSink) {
        this.contentSink = contentSink;
    }

    @Override
    public ContentSink content() {
        return contentSink;
    }
}
