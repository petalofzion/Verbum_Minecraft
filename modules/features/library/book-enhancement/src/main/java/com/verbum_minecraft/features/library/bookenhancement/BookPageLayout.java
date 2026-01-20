package com.verbum_minecraft.features.library.bookenhancement;

import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

public final class BookPageLayout {
    private BookPageLayout() {
    }

    public static List<String> paginate(
        BookPages pages,
        int textWidth,
        int linesPerPage,
        BookLineBreaker lineBreaker
    ) {
        Objects.requireNonNull(pages, "pages");
        Objects.requireNonNull(lineBreaker, "lineBreaker");
        if (textWidth <= 0) {
            throw new IllegalArgumentException("textWidth must be > 0");
        }
        if (linesPerPage <= 0) {
            throw new IllegalArgumentException("linesPerPage must be > 0");
        }

        List<String> output = new ArrayList<>();
        List<String> lineBuffer = new ArrayList<>(linesPerPage);
        List<String> segments = toSegments(pages);

        for (int i = 0; i < segments.size(); i++) {
            wrapSegment(segments.get(i), textWidth, linesPerPage, lineBreaker, lineBuffer, output);
            if (pages.usedExplicitBreaks() && i < segments.size() - 1) {
                flushLines(lineBuffer, output);
            }
        }

        flushLines(lineBuffer, output);
        if (output.isEmpty()) {
            output.add("");
        }

        if (pages.truncated()) {
            output.add("[Verbum] Book truncated to configured limits.");
        }

        return output;
    }

    private static List<String> toSegments(BookPages pages) {
        if (pages.usedExplicitBreaks()) {
            return pages.pages();
        }
        StringBuilder combined = new StringBuilder();
        for (String page : pages.pages()) {
            combined.append(page);
        }
        return List.of(combined.toString());
    }

    private static void wrapSegment(
        String segment,
        int textWidth,
        int linesPerPage,
        BookLineBreaker lineBreaker,
        List<String> lineBuffer,
        List<String> output
    ) {
        String[] paragraphs = segment.split("\n", -1);
        for (String paragraph : paragraphs) {
            if (paragraph.isEmpty()) {
                appendLine("", linesPerPage, lineBuffer, output);
                continue;
            }
            String remaining = paragraph;
            while (!remaining.isEmpty()) {
                String slice = lineBreaker.fit(remaining, textWidth);
                if (slice.isEmpty()) {
                    slice = remaining.substring(0, 1);
                }
                String line = slice;
                int consumed = slice.length();
                if (consumed < remaining.length()) {
                    int lastSpace = slice.lastIndexOf(' ');
                    if (lastSpace > 0) {
                        line = slice.substring(0, lastSpace);
                        consumed = lastSpace + 1;
                    }
                }
                line = stripTrailing(line);
                appendLine(line, linesPerPage, lineBuffer, output);
                remaining = stripLeading(remaining.substring(consumed));
            }
        }
    }

    private static void appendLine(
        String line,
        int linesPerPage,
        List<String> lineBuffer,
        List<String> output
    ) {
        lineBuffer.add(line);
        if (lineBuffer.size() >= linesPerPage) {
            flushLines(lineBuffer, output);
        }
    }

    private static void flushLines(List<String> lineBuffer, List<String> output) {
        if (lineBuffer.isEmpty()) {
            return;
        }
        StringBuilder page = new StringBuilder();
        for (int i = 0; i < lineBuffer.size(); i++) {
            if (i > 0) {
                page.append('\n');
            }
            page.append(lineBuffer.get(i));
        }
        output.add(page.toString());
        lineBuffer.clear();
    }

    private static String stripLeading(String value) {
        int index = 0;
        while (index < value.length() && Character.isWhitespace(value.charAt(index))) {
            index++;
        }
        return value.substring(index);
    }

    private static String stripTrailing(String value) {
        int index = value.length() - 1;
        while (index >= 0 && Character.isWhitespace(value.charAt(index))) {
            index--;
        }
        return value.substring(0, index + 1);
    }
}
