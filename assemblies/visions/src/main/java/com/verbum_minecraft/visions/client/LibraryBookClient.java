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

        List<Component> formattedPages = toComponents(pages);
        BookViewScreen.BookAccess access = new BookViewScreen.BookAccess(formattedPages);
        Minecraft.getInstance().setScreen(new BookViewScreen(access));
    }

    private static void openError(String message) {
        List<Component> pages = List.of(Component.literal(message));
        BookViewScreen.BookAccess access = new BookViewScreen.BookAccess(pages);
        Minecraft.getInstance().setScreen(new BookViewScreen(access));
    }

    private static List<Component> toComponents(BookPages pages) {
        List<Component> formatted = new ArrayList<>(pages.pageCount());
        for (String page : pages.pages()) {
            formatted.add(Component.literal(page));
        }
        if (formatted.isEmpty()) {
            formatted.add(Component.literal(""));
        }
        if (pages.truncated()) {
            formatted.add(Component.literal("[Verbum] Book truncated to configured limits."));
        }
        return formatted;
    }
}
