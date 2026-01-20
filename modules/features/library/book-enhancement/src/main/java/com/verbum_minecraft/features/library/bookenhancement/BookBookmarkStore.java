package com.verbum_minecraft.features.library.bookenhancement;

public interface BookBookmarkStore {
    int get(BookId bookId);

    void set(BookId bookId, int pageNumber);
}
