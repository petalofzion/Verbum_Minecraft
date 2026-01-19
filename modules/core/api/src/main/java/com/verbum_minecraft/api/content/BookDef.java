package com.verbum_minecraft.api.content;

import java.util.Objects;

/**
 * Pure data definition for a written book item.
 */
public record BookDef(
    ItemDef item,
    String title,
    String author,
    String contentResourcePath
) {
    public static final String PAGE_SEPARATOR = "---PAGE---";

    public BookDef {
        Objects.requireNonNull(item, "item");
        Objects.requireNonNull(title, "title");
        Objects.requireNonNull(author, "author");
    }

    /**
     * Resolves the content resource path. If none is provided, uses a default
     * based on the item id: assets/<namespace>/books/<path>.txt
     */
    public String resolvedContentResourcePath() {
        if (contentResourcePath != null && !contentResourcePath.isBlank()) {
            return contentResourcePath;
        }
        VerbumId id = item.id();
        return "assets/" + id.namespace() + "/books/" + id.path() + ".txt";
    }
}
