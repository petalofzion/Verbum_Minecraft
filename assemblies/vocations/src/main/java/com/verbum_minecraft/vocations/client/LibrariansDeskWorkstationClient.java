package com.verbum_minecraft.vocations.client;

import com.verbum_minecraft.vocations.registry.LibrariansDeskWorkstationMenu;
import net.minecraft.client.gui.screens.MenuScreens;
import net.minecraft.world.inventory.MenuType;

public final class LibrariansDeskWorkstationClient {
    private LibrariansDeskWorkstationClient() {
    }

    public static void registerScreen(MenuType<LibrariansDeskWorkstationMenu> menuType) {
        MenuScreens.register(menuType, LibrariansDeskWorkstationScreen::new);
    }
}
