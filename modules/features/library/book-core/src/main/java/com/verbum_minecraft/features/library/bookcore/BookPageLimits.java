package com.verbum_minecraft.features.library.bookcore;

public record BookPageLimits(long maxRawBytes, int maxPages, int maxPageChars) {
    public static final long PRD_MAX_RAW_BYTES = 128L * 1024L * 1024L;
    public static final int PRD_MAX_PAGES = 100_000;
    public static final int PRD_MAX_PAGE_CHARS = 16_384;
    public static final BookPageLimits PRD_DEFAULTS =
        new BookPageLimits(PRD_MAX_RAW_BYTES, PRD_MAX_PAGES, PRD_MAX_PAGE_CHARS);

    public BookPageLimits {
        if (maxRawBytes <= 0) {
            throw new IllegalArgumentException("maxRawBytes must be > 0");
        }
        if (maxPages <= 0) {
            throw new IllegalArgumentException("maxPages must be > 0");
        }
        if (maxPageChars <= 0) {
            throw new IllegalArgumentException("maxPageChars must be > 0");
        }
    }

    public static BookPageLimits prdDefaults() {
        return PRD_DEFAULTS;
    }
}
