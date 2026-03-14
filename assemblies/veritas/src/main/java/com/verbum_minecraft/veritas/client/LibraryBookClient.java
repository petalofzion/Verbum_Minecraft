package com.verbum_minecraft.veritas.client;

import com.verbum_minecraft.features.library.bookenhancement.BookId;
import com.verbum_minecraft.features.library.bookenhancement.BookPageLayout;
import com.verbum_minecraft.features.library.bookenhancement.BookPages;
import com.verbum_minecraft.veritas.registry.LibraryBookSupport;
import java.io.IOException;
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
            openError(bookId, "Failed to load book content.");
            return;
        }

        List<Component> formattedPages = paginateForBookView(pages, Minecraft.getInstance().font);
        BookViewScreen.BookAccess access = new BookViewScreen.BookAccess(formattedPages);
        Minecraft.getInstance().setScreen(new LibraryBookView(bookId, access));
    }

    private static void openError(BookId bookId, String message) {
        List<Component> pages = List.of(Component.literal(message));
        BookViewScreen.BookAccess access = new BookViewScreen.BookAccess(pages);
        Minecraft.getInstance().setScreen(new LibraryBookView(bookId, access));
    }

    private static List<Component> paginateForBookView(BookPages pages, Font font) {
        int textWidth = Math.max(1, LibraryBookView.textWidth());
        int textHeight = Math.max(1, LibraryBookView.textHeight());
        int lineHeight = Math.max(1, font.lineHeight);
        int linesPerPage = Math.max(1, textHeight / lineHeight);

        List<String> pageStrings = BookPageLayout.paginate(
            pages,
            textWidth,
            linesPerPage,
            (text, width) -> font.plainSubstrByWidth(text, width)
        );
        return toComponents(pageStrings);
    }

    private static List<Component> toComponents(List<String> pageStrings) {
        List<Component> pages = new java.util.ArrayList<>(pageStrings.size());
        for (String page : pageStrings) {
            pages.add(Component.literal(page));
        }
        return List.copyOf(pages);
    }
}
