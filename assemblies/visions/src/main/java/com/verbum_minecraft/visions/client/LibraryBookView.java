package com.verbum_minecraft.visions.client;

import net.fabricmc.api.EnvType;
import net.fabricmc.api.Environment;
import net.minecraft.client.gui.screens.inventory.BookViewScreen;

@Environment(EnvType.CLIENT)
final class LibraryBookView extends BookViewScreen {
    LibraryBookView(BookAccess access) {
        super(access);
    }

    static int textWidth() {
        return TEXT_WIDTH;
    }

    static int textHeight() {
        return TEXT_HEIGHT;
    }
}
