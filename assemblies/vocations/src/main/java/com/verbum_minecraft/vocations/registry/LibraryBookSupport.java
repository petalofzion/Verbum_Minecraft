package com.verbum_minecraft.vocations.registry;

import com.verbum_minecraft.api.content.LibraryBookDef;
import com.verbum_minecraft.features.library.bookenhancement.BookContentSource;
import com.verbum_minecraft.features.library.bookenhancement.BookId;
import com.verbum_minecraft.features.library.bookenhancement.BookLibrary;

import java.io.ByteArrayOutputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;

public final class LibraryBookSupport {
    private static final BookContentSource CONTENT_SOURCE = new ClasspathBookContentSource();
    private static final BookLibrary LIBRARY = new BookLibrary(CONTENT_SOURCE);

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

    private static final class ClasspathBookContentSource implements BookContentSource {
        private static final int READ_BUFFER_SIZE = 8192;

        @Override
        public String load(String resourcePath, long maxBytes) throws IOException {
            try (InputStream input = classLoader().getResourceAsStream(resourcePath)) {
                if (input == null) {
                    throw new FileNotFoundException("Book resource not found: " + resourcePath);
                }
                byte[] bytes = readToLimit(input, maxBytes);
                return new String(bytes, StandardCharsets.UTF_8);
            }
        }

        private static byte[] readToLimit(InputStream input, long maxBytes) throws IOException {
            ByteArrayOutputStream output = new ByteArrayOutputStream();
            byte[] buffer = new byte[READ_BUFFER_SIZE];
            long total = 0;
            int read;
            while ((read = input.read(buffer)) != -1) {
                total += read;
                if (total > maxBytes) {
                    throw new IOException("Book text exceeds max bytes: " + maxBytes);
                }
                output.write(buffer, 0, read);
            }
            return output.toByteArray();
        }

        private static ClassLoader classLoader() {
            ClassLoader loader = Thread.currentThread().getContextClassLoader();
            if (loader == null) {
                loader = LibraryBookSupport.class.getClassLoader();
            }
            return loader;
        }
    }
}
