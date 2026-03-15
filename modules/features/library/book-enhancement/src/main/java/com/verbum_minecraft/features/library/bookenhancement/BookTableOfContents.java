package com.verbum_minecraft.features.library.bookenhancement;

import java.util.List;
import java.util.Objects;

public final class BookTableOfContents {
    private final List<BookChapter> chapters;

    public BookTableOfContents(List<BookChapter> chapters) {
        Objects.requireNonNull(chapters, "chapters");
        List<BookChapter> copy = List.copyOf(chapters);
        validate(copy);
        this.chapters = copy;
    }

    public List<BookChapter> chapters() {
        return chapters;
    }

    public int size() {
        return chapters.size();
    }

    public boolean isEmpty() {
        return chapters.isEmpty();
    }

    public BookChapter chapterForPage(int page) {
        if (page < 0) {
            throw new IllegalArgumentException("page must be >= 0");
        }
        if (chapters.isEmpty()) {
            return null;
        }
        int low = 0;
        int high = chapters.size() - 1;
        int result = -1;
        while (low <= high) {
            int mid = (low + high) >>> 1;
            int startPage = chapters.get(mid).startPage();
            if (startPage <= page) {
                result = mid;
                low = mid + 1;
            } else {
                high = mid - 1;
            }
        }
        return result >= 0 ? chapters.get(result) : null;
    }

    private static void validate(List<BookChapter> chapters) {
        int lastStart = -1;
        for (BookChapter chapter : chapters) {
            Objects.requireNonNull(chapter, "chapter");
            int start = chapter.startPage();
            if (start <= lastStart) {
                throw new IllegalArgumentException(
                    "Chapters must be in strictly increasing startPage order"
                );
            }
            lastStart = start;
        }
    }
}
