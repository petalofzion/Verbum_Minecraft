package com.verbum_minecraft.features.library.bookenhancement;

import java.util.Objects;

public record BookChapter(String title, int startPage) {
    public BookChapter {
        Objects.requireNonNull(title, "title");
        if (title.isBlank()) {
            throw new IllegalArgumentException("title is blank");
        }
        if (startPage < 0) {
            throw new IllegalArgumentException("startPage must be >= 0");
        }
    }
}
