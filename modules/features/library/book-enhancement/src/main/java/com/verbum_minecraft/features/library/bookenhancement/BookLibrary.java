package com.verbum_minecraft.features.library.bookenhancement;

import java.io.IOException;
import java.util.Objects;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;

public final class BookLibrary {
    private final BookContentSource contentSource;
    private final BookPageLimits limits;
    private final ConcurrentMap<BookPaginationKey, BookPages> cache;
    private final ConcurrentMap<BookId, String> resourceOverrides;

    public BookLibrary(BookContentSource contentSource) {
        this(contentSource, BookPageLimits.PRD_DEFAULTS);
    }

    public BookLibrary(BookContentSource contentSource, BookPageLimits limits) {
        this.contentSource = Objects.requireNonNull(contentSource, "contentSource");
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
        String normalized = normalizeResourcePath(resourcePath);
        String text = contentSource.load(normalized, limits.maxRawBytes());
        return BookPages.paginate(text, limits);
    }

    private static String normalizeResourcePath(String resourcePath) {
        if (resourcePath.startsWith("/")) {
            return resourcePath.substring(1);
        }
        return resourcePath;
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
