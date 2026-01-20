package com.verbum_minecraft.visions.client;

import com.verbum_minecraft.features.library.bookcore.BookId;
import net.fabricmc.api.EnvType;
import net.fabricmc.api.Environment;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.client.gui.screens.inventory.BookViewScreen;
import net.minecraft.network.chat.Component;

@Environment(EnvType.CLIENT)
final class LibraryBookView extends BookViewScreen {
    private static final int PAGE_BOX_WIDTH = 36;
    private static final int BUTTON_WIDTH = 28;
    private static final int MARK_WIDTH = 40;
    private static final int CONTROL_HEIGHT = 12;

    private final BookId bookId;
    private BookAccess access;
    private EditBox pageBox;
    private int currentPageIndex;
    private int bookmarkPage;

    LibraryBookView(BookId bookId, BookAccess access) {
        super(access);
        this.bookId = bookId;
        this.access = access;
    }

    static int textWidth() {
        return TEXT_WIDTH;
    }

    static int textHeight() {
        return TEXT_HEIGHT;
    }

    @Override
    public void setBookAccess(BookAccess access) {
        super.setBookAccess(access);
        this.access = access;
    }

    @Override
    protected void init() {
        super.init();
        int left = (width - IMAGE_WIDTH) / 2;
        int top = (height - IMAGE_HEIGHT) / 2;
        int totalWidth = PAGE_BOX_WIDTH + BUTTON_WIDTH + MARK_WIDTH + 8;
        int x = left + IMAGE_WIDTH - totalWidth;
        int y = top + 8;

        bookmarkPage = LibraryBookBookmarks.get(bookId);

        pageBox = new EditBox(font, x, y, PAGE_BOX_WIDTH, CONTROL_HEIGHT, Component.literal("Page"));
        pageBox.setMaxLength(6);
        pageBox.setFilter(value -> value.isEmpty() || value.chars().allMatch(Character::isDigit));
        updatePageHint();
        addRenderableWidget(pageBox);

        addRenderableWidget(Button.builder(Component.literal("Go"), button -> jumpToPage())
            .bounds(x + PAGE_BOX_WIDTH + 4, y, BUTTON_WIDTH, CONTROL_HEIGHT)
            .build());

        addRenderableWidget(Button.builder(Component.literal("Mark"), button -> saveBookmark())
            .bounds(x + PAGE_BOX_WIDTH + BUTTON_WIDTH + 8, y, MARK_WIDTH, CONTROL_HEIGHT)
            .build());
    }

    @Override
    public boolean setPage(int page) {
        boolean success = super.setPage(page);
        if (success) {
            currentPageIndex = page;
        }
        return success;
    }

    private void jumpToPage() {
        if (pageBox == null) {
            return;
        }
        String value = pageBox.getValue().trim();
        if (value.isEmpty()) {
            if (bookmarkPage > 0) {
                setPage(bookmarkPage - 1);
            }
            return;
        }
        try {
            int page = Integer.parseInt(value);
            if (page > 0) {
                setPage(page - 1);
            }
        } catch (NumberFormatException ignored) {
        }
    }

    private void saveBookmark() {
        bookmarkPage = currentPageIndex + 1;
        LibraryBookBookmarks.set(bookId, bookmarkPage);
        updatePageHint();
    }

    private void updatePageHint() {
        if (pageBox == null) {
            return;
        }
        if (bookmarkPage > 0) {
            pageBox.setHint(Component.literal("BM " + bookmarkPage));
        } else {
            pageBox.setHint(Component.literal("Page"));
        }
    }
}
