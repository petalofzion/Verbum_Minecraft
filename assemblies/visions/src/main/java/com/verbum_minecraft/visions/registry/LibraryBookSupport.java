package com.verbum_minecraft.visions.registry;

import com.verbum_minecraft.api.content.LibraryBookDef;
import com.verbum_minecraft.features.library.bookcore.BookId;
import com.verbum_minecraft.features.library.bookcore.BookLibrary;

public final class LibraryBookSupport {
    private static final BookLibrary LIBRARY = new BookLibrary();

    private LibraryBookSupport() {
    }

    public static BookId register(LibraryBookDef def) {
        BookId bookId = BookId.parse(def.bookId());
        String resourcePath = def.contentResourcePath();
        if (resourcePath != null && !resourcePath.isBlank()) {
            LIBRARY.register(bookId, resourcePath);
        }
        return bookId;
    }

    public static BookLibrary library() {
        return LIBRARY;
    }
}
