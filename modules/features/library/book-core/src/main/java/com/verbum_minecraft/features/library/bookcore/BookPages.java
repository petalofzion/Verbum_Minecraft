package com.verbum_minecraft.features.library.bookcore;

import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

public final class BookPages {
    public static final String PAGE_BREAK_MARKER = "---PAGE---";

    private final List<String> pages;
    private final boolean truncated;
    private final boolean usedExplicitBreaks;

    private BookPages(List<String> pages, boolean truncated, boolean usedExplicitBreaks) {
        this.pages = List.copyOf(pages);
        this.truncated = truncated;
        this.usedExplicitBreaks = usedExplicitBreaks;
    }

    public List<String> pages() {
        return pages;
    }

    public int pageCount() {
        return pages.size();
    }

    public String page(int index) {
        return pages.get(index);
    }

    public boolean truncated() {
        return truncated;
    }

    public boolean usedExplicitBreaks() {
        return usedExplicitBreaks;
    }

    public static BookPages paginate(String rawText, BookPageLimits limits) {
        Objects.requireNonNull(rawText, "rawText");
        Objects.requireNonNull(limits, "limits");

        List<String> pages = new ArrayList<>();
        StringBuilder current = new StringBuilder();
        boolean truncated = false;
        boolean usedExplicitBreaks = false;

        String[] lines = rawText.split("\n", -1);
        for (int i = 0; i < lines.length; i++) {
            String line = stripCarriageReturn(lines[i]);
            if (PAGE_BREAK_MARKER.equals(line)) {
                usedExplicitBreaks = true;
                if (!appendPage(pages, current, limits)) {
                    truncated = true;
                    break;
                }
                current.setLength(0);
                continue;
            }

            String piece = line;
            if (i < lines.length - 1) {
                piece = line + "\n";
            }

            if (!appendText(pages, current, piece, limits)) {
                truncated = true;
                break;
            }
        }

        if (!truncated) {
            if (!appendPage(pages, current, limits)) {
                truncated = true;
            }
        }

        return new BookPages(pages, truncated, usedExplicitBreaks);
    }

    private static boolean appendPage(
        List<String> pages,
        StringBuilder current,
        BookPageLimits limits
    ) {
        if (pages.size() >= limits.maxPages()) {
            return false;
        }
        pages.add(current.toString());
        return true;
    }

    private static boolean appendText(
        List<String> pages,
        StringBuilder current,
        String text,
        BookPageLimits limits
    ) {
        int maxChars = limits.maxPageChars();
        int offset = 0;
        while (offset < text.length()) {
            int remaining = maxChars - current.length();
            if (remaining == 0) {
                if (!appendPage(pages, current, limits)) {
                    return false;
                }
                current.setLength(0);
                remaining = maxChars;
            }
            int take = Math.min(remaining, text.length() - offset);
            current.append(text, offset, offset + take);
            offset += take;
            if (current.length() == maxChars) {
                if (!appendPage(pages, current, limits)) {
                    return false;
                }
                current.setLength(0);
            }
        }
        return true;
    }

    private static String stripCarriageReturn(String line) {
        if (!line.isEmpty() && line.charAt(line.length() - 1) == '\r') {
            return line.substring(0, line.length() - 1);
        }
        return line;
    }
}
