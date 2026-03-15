package com.verbum_minecraft.features.library.bookenhancement;

import java.util.Objects;

public record BookBookmark(BookId bookId, int page) {
    public BookBookmark {
        Objects.requireNonNull(bookId, "bookId");
        if (page < 0) {
            throw new IllegalArgumentException("page must be >= 0");
        }
    }

    public static BookBookmark atStart(BookId bookId) {
        return new BookBookmark(bookId, 0);
    }
}
