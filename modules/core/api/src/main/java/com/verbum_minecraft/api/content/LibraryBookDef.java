package com.verbum_minecraft.api.content;

import java.util.Objects;

/**
 * Pure data definition for a library-backed written book.
 */
public record LibraryBookDef(
    ItemDef item,
    String bookId,
    String title,
    String author,
    String contentResourcePath
) {
    public LibraryBookDef {
        Objects.requireNonNull(item, "item");
        Objects.requireNonNull(bookId, "bookId");
        Objects.requireNonNull(title, "title");
        Objects.requireNonNull(author, "author");

        bookId = bookId.trim();
        if (bookId.isEmpty()) {
            throw new IllegalArgumentException("bookId is blank");
        }
        if (!hasValidBookId(bookId)) {
            throw new IllegalArgumentException("Invalid bookId: " + bookId);
        }
        if (contentResourcePath != null && contentResourcePath.isBlank()) {
            throw new IllegalArgumentException("contentResourcePath is blank");
        }
    }

    private static boolean hasValidBookId(String bookId) {
        int colon = bookId.indexOf(':');
        return colon > 0 && colon < bookId.length() - 1;
    }
}
