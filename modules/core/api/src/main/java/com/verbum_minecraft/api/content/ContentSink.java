package com.verbum_minecraft.api.content;

/**
 * Sink for receiving content definitions from features.
 */
public interface ContentSink {
    void acceptItem(ItemDef def);

    void acceptBook(BookDef def);
}
