package com.verbum_minecraft.visions.client;

import com.verbum_minecraft.features.library.bookcore.BookId;
import com.verbum_minecraft.features.library.bookcore.BookPages;
import com.verbum_minecraft.visions.registry.LibraryBookSupport;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import net.fabricmc.api.EnvType;
import net.fabricmc.api.Environment;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.screens.inventory.BookViewScreen;
import net.minecraft.network.chat.Component;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Environment(EnvType.CLIENT)
public final class LibraryBookClient {
    private static final Logger LOGGER = LoggerFactory.getLogger(LibraryBookClient.class);

    private LibraryBookClient() {
    }

    public static void openBook(BookId bookId) {
        BookPages pages;
        try {
            pages = LibraryBookSupport.library().load(bookId);
        } catch (IOException e) {
            LOGGER.warn("Failed to load library book {}", bookId.compactId(), e);
            openError("Failed to load book content.");
            return;
        }

        List<Component> formattedPages = paginateForBookView(pages, Minecraft.getInstance().font);
        BookViewScreen.BookAccess access = new BookViewScreen.BookAccess(formattedPages);
        Minecraft.getInstance().setScreen(new LibraryBookView(access));
    }

    private static void openError(String message) {
        List<Component> pages = List.of(Component.literal(message));
        BookViewScreen.BookAccess access = new BookViewScreen.BookAccess(pages);
        Minecraft.getInstance().setScreen(new LibraryBookView(access));
    }

    private static List<Component> paginateForBookView(BookPages pages, Font font) {
        int textWidth = Math.max(1, LibraryBookView.textWidth());
        int textHeight = Math.max(1, LibraryBookView.textHeight());
        int lineHeight = Math.max(1, font.lineHeight);
        int linesPerPage = Math.max(1, textHeight / lineHeight);

        List<Component> formatted = new ArrayList<>();
        List<String> lineBuffer = new ArrayList<>(linesPerPage);
        List<String> segments = toSegments(pages);

        for (int i = 0; i < segments.size(); i++) {
            wrapSegment(segments.get(i), textWidth, font, linesPerPage, lineBuffer, formatted);
            if (pages.usedExplicitBreaks() && i < segments.size() - 1) {
                flushLines(lineBuffer, formatted);
            }
        }

        flushLines(lineBuffer, formatted);

        if (formatted.isEmpty()) {
            formatted.add(Component.literal(""));
        }
        if (pages.truncated()) {
            formatted.add(Component.literal("[Verbum] Book truncated to configured limits."));
        }
        return formatted;
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
        int width,
        Font font,
        int linesPerPage,
        List<String> lineBuffer,
        List<Component> output
    ) {
        String[] paragraphs = segment.split("\n", -1);
        for (String paragraph : paragraphs) {
            if (paragraph.isEmpty()) {
                appendLine("", linesPerPage, lineBuffer, output);
                continue;
            }
            String remaining = paragraph;
            while (!remaining.isEmpty()) {
                String slice = font.plainSubstrByWidth(remaining, width);
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
                line = line.stripTrailing();
                appendLine(line, linesPerPage, lineBuffer, output);
                remaining = remaining.substring(consumed).stripLeading();
            }
        }
    }

    private static void appendLine(
        String line,
        int linesPerPage,
        List<String> lineBuffer,
        List<Component> output
    ) {
        lineBuffer.add(line);
        if (lineBuffer.size() >= linesPerPage) {
            flushLines(lineBuffer, output);
        }
    }

    private static void flushLines(List<String> lineBuffer, List<Component> output) {
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
        output.add(Component.literal(page.toString()));
        lineBuffer.clear();
    }
}
