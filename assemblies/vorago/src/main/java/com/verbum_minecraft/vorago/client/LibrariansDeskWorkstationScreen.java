package com.verbum_minecraft.vorago.client;

import com.verbum_minecraft.vorago.registry.LibrariansDeskWorkstationMenu;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.entity.player.Inventory;

final class LibrariansDeskWorkstationScreen extends AbstractContainerScreen<LibrariansDeskWorkstationMenu> {
    private static final int PANEL_OUTER = 0xFF7B6A53;
    private static final int PANEL_INNER = 0xFF2D241A;
    private static final int SLOT_BORDER = 0xFFB49C7B;
    private static final int SLOT_FILL = 0xFF18130E;

    LibrariansDeskWorkstationScreen(
        LibrariansDeskWorkstationMenu menu,
        Inventory playerInventory,
        Component title
    ) {
        super(menu, playerInventory, title);
        this.imageWidth = LibrariansDeskWorkstationMenu.GUI_WIDTH;
        this.imageHeight = LibrariansDeskWorkstationMenu.GUI_HEIGHT;
        this.titleLabelX = 8;
        this.titleLabelY = 8;
        this.inventoryLabelX = 8;
        this.inventoryLabelY = 96;
    }

    @Override
    protected void init() {
        super.init();
        int buttonX = leftPos + 172;
        addRenderableWidget(actionButton("Salvage", buttonX, topPos + 24, LibrariansDeskWorkstationMenu.ACTION_SALVAGE_ALL));
        addRenderableWidget(actionButton("Copy Text", buttonX, topPos + 46, LibrariansDeskWorkstationMenu.ACTION_COPY_BOOKS));
        addRenderableWidget(actionButton("Edit Book", buttonX, topPos + 68, LibrariansDeskWorkstationMenu.ACTION_EDIT_PLAYER_BOOK));
        addRenderableWidget(actionButton("Write Draft", buttonX, topPos + 90, LibrariansDeskWorkstationMenu.ACTION_WRITE_DRAFT));
    }

    @Override
    public void render(GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {
        renderBackground(graphics, mouseX, mouseY, partialTick);
        super.render(graphics, mouseX, mouseY, partialTick);
        renderTooltip(graphics, mouseX, mouseY);
    }

    @Override
    protected void renderBg(GuiGraphics graphics, float partialTick, int mouseX, int mouseY) {
        graphics.fill(leftPos, topPos, leftPos + imageWidth, topPos + imageHeight, PANEL_OUTER);
        graphics.fill(leftPos + 1, topPos + 1, leftPos + imageWidth - 1, topPos + imageHeight - 1, PANEL_INNER);
        for (Slot slot : menu.slots) {
            int slotLeft = leftPos + slot.x - 1;
            int slotTop = topPos + slot.y - 1;
            graphics.fill(slotLeft, slotTop, slotLeft + 18, slotTop + 18, SLOT_BORDER);
            graphics.fill(slotLeft + 1, slotTop + 1, slotLeft + 17, slotTop + 17, SLOT_FILL);
        }
    }

    @Override
    protected void renderLabels(GuiGraphics graphics, int mouseX, int mouseY) {
        super.renderLabels(graphics, mouseX, mouseY);
        int color = 0xFFE6D7C3;
        graphics.drawString(font, "Input Grid", 24, 34, color, false);
        graphics.drawString(font, "Actions", 172, 12, color, false);
        graphics.drawString(font, "Shift-click moves between grid and inventory", 8, 184, color, false);
    }

    private Button actionButton(String label, int x, int y, int actionId) {
        return Button.builder(Component.literal(label), button -> sendAction(actionId))
            .bounds(x, y, 76, 18)
            .build();
    }

    private void sendAction(int actionId) {
        if (minecraft == null || minecraft.gameMode == null) {
            return;
        }
        minecraft.gameMode.handleInventoryButtonClick(menu.containerId, actionId);
    }
}
