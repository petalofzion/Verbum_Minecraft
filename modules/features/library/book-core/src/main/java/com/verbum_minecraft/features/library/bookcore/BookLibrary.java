package com.verbum_minecraft.features.library.bookcore;

import java.io.ByteArrayOutputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.Objects;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;

public final class BookLibrary {
    private static final int READ_BUFFER_SIZE = 8192;

    private final ClassLoader classLoader;
    private final BookPageLimits limits;
    private final ConcurrentMap<BookPaginationKey, BookPages> cache;
    private final ConcurrentMap<BookId, String> resourceOverrides;

    public BookLibrary() {
        this(defaultClassLoader(), BookPageLimits.PRD_DEFAULTS);
    }

    public BookLibrary(ClassLoader classLoader, BookPageLimits limits) {
        this.classLoader = Objects.requireNonNull(classLoader, "classLoader");
        this.limits = Objects.requireNonNull(limits, "limits");
        this.cache = new ConcurrentHashMap<>();
        this.resourceOverrides = new ConcurrentHashMap<>();
    }

    public BookPageLimits limits() {
        return limits;
    }

    public void register(BookId id, String resourcePath) {
        Objects.requireNonNull(id, "id");
        Objects.requireNonNull(resourcePath, "resourcePath");
        if (resourcePath.isBlank()) {
            throw new IllegalArgumentException("resourcePath is blank");
        }
        resourceOverrides.put(id, normalizeResourcePath(resourcePath));
    }

    public BookPages load(BookId id) throws IOException {
        return load(BookPaginationKey.defaultFor(id));
    }

    public BookPages load(BookPaginationKey key) throws IOException {
        Objects.requireNonNull(key, "key");
        BookPages cached = cache.get(key);
        if (cached != null) {
            return cached;
        }
        BookPages loaded = loadPages(key.bookId());
        BookPages existing = cache.putIfAbsent(key, loaded);
        return existing != null ? existing : loaded;
    }

    public boolean isCached(BookPaginationKey key) {
        return cache.containsKey(key);
    }

    public void clearCache() {
        cache.clear();
    }

    private BookPages loadPages(BookId id) throws IOException {
        String resourcePath = resourceOverrides.getOrDefault(id, id.resourcePath());
        try (InputStream input = classLoader.getResourceAsStream(resourcePath)) {
            if (input == null) {
                throw new FileNotFoundException("Book resource not found: " + resourcePath);
            }
            byte[] bytes = readToLimit(input, limits.maxRawBytes());
            String text = new String(bytes, StandardCharsets.UTF_8);
            return BookPages.paginate(text, limits);
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

    private static String normalizeResourcePath(String resourcePath) {
        if (resourcePath.startsWith("/")) {
            return resourcePath.substring(1);
        }
        return resourcePath;
    }

    private static ClassLoader defaultClassLoader() {
        ClassLoader loader = Thread.currentThread().getContextClassLoader();
        if (loader == null) {
            loader = BookLibrary.class.getClassLoader();
        }
        return loader;
    }

    public static record BookHandle(BookId bookId, int bookmarkPage) {
        public BookHandle {
            Objects.requireNonNull(bookId, "bookId");
            if (bookmarkPage < 0) {
                throw new IllegalArgumentException("bookmarkPage must be >= 0");
            }
        }

        public static BookHandle of(BookId bookId) {
            return new BookHandle(bookId, 0);
        }
    }

    public static record BookPaginationKey(
        BookId bookId,
        String locale,
        String fontKey,
        int guiScale,
        int wrapWidth
    ) {
        public BookPaginationKey {
            Objects.requireNonNull(bookId, "bookId");
            Objects.requireNonNull(locale, "locale");
            Objects.requireNonNull(fontKey, "fontKey");
            if (guiScale < 0) {
                throw new IllegalArgumentException("guiScale must be >= 0");
            }
            if (wrapWidth < 0) {
                throw new IllegalArgumentException("wrapWidth must be >= 0");
            }
        }

        public static BookPaginationKey defaultFor(BookId bookId) {
            return new BookPaginationKey(bookId, "und", "default", 0, 0);
        }
    }
}
