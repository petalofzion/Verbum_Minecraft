package com.verbum_minecraft.vorago.registry;

import com.verbum_minecraft.api.content.BlockWorkstationHandler;
import com.verbum_minecraft.api.content.ItemGrant;
import com.verbum_minecraft.api.content.WorkstationActionRequest;
import com.verbum_minecraft.api.content.WorkstationActionResult;
import com.verbum_minecraft.api.content.WorkstationBookDraft;
import com.verbum_minecraft.api.content.WorkstationBookSnapshot;
import com.verbum_minecraft.api.content.WorkstationPlayerBookGrant;
import com.verbum_minecraft.api.content.WorkstationSlotDelta;
import com.verbum_minecraft.api.content.WorkstationSlotInput;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicBoolean;
import net.fabricmc.api.EnvType;
import net.fabricmc.loader.api.FabricLoader;
import net.minecraft.core.Registry;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.server.network.Filterable;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.flag.FeatureFlags;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.MenuType;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.component.WritableBookContent;
import net.minecraft.world.item.component.WrittenBookContent;

public final class LibrariansDeskWorkstationMenu extends AbstractContainerMenu {
    public static final int ACTION_SALVAGE_ALL = 0;
    public static final int ACTION_COPY_BOOKS = 1;
    public static final int ACTION_EDIT_PLAYER_BOOK = 2;
    public static final int ACTION_WRITE_DRAFT = 3;
    public static final int GUI_WIDTH = 256;
    public static final int GUI_HEIGHT = 194;

    private static final AtomicBoolean CLIENT_SCREEN_REGISTERED = new AtomicBoolean(false);
    private static final int INPUT_SLOT_COUNT = 9;
    private static final int PLAYER_INV_ROWS = 3;
    private static final int PLAYER_INV_COLUMNS = 9;
    private static final int PLAYER_INV_SLOT_COUNT = PLAYER_INV_ROWS * PLAYER_INV_COLUMNS;
    private static final int HOTBAR_SLOT_COUNT = 9;
    private static final int INPUT_START = 0;
    private static final int PLAYER_INV_START = INPUT_START + INPUT_SLOT_COUNT;
    private static final int HOTBAR_START = PLAYER_INV_START + PLAYER_INV_SLOT_COUNT;
    private static final int HOTBAR_END = HOTBAR_START + HOTBAR_SLOT_COUNT;

    private static final Identifier MENU_ID = Identifier.fromNamespaceAndPath("verbum", "librarians_desk_workstation_vorago");
    private static final MenuType<LibrariansDeskWorkstationMenu> MENU_TYPE = Registry.register(
        BuiltInRegistries.MENU,
        MENU_ID,
        new MenuType<>(LibrariansDeskWorkstationMenu::new, FeatureFlags.VANILLA_SET)
    );

    private final SimpleContainer input = new SimpleContainer(INPUT_SLOT_COUNT);
    private final BlockWorkstationHandler handler;

    public LibrariansDeskWorkstationMenu(int containerId, Inventory playerInventory) {
        this(containerId, playerInventory, null);
    }

    public LibrariansDeskWorkstationMenu(int containerId, Inventory playerInventory, BlockWorkstationHandler handler) {
        super(MENU_TYPE, containerId);
        this.handler = handler;
        addInputSlots();
        addPlayerInventorySlots(playerInventory);
        addPlayerHotbarSlots(playerInventory);
    }

    public static MenuType<LibrariansDeskWorkstationMenu> menuType() {
        return MENU_TYPE;
    }

    static void ensureClientScreenRegistration() {
        if (FabricLoader.getInstance().getEnvironmentType() != EnvType.CLIENT) {
            return;
        }
        if (!CLIENT_SCREEN_REGISTERED.compareAndSet(false, true)) {
            return;
        }

        try {
            Class<?> bridgeClass = Class.forName("com.verbum_minecraft.vorago.client.LibrariansDeskWorkstationClient");
            Method register = bridgeClass.getMethod("registerScreen", MenuType.class);
            register.invoke(null, MENU_TYPE);
        } catch (ReflectiveOperationException e) {
            throw new IllegalStateException("Failed to register workstation screen", e);
        }
    }

    @Override
    public boolean clickMenuButton(Player player, int buttonId) {
        if (handler == null || player.level().isClientSide()) {
            return false;
        }

        String actionId = toActionId(buttonId);
        if (actionId == null) {
            return false;
        }

        WorkstationActionRequest request = new WorkstationActionRequest(
            actionId,
            snapshotInputSlots(),
            player.getName().getString(),
            player.getAbilities().instabuild,
            buildDraft(actionId)
        );
        WorkstationActionResult result = handler.apply(request);
        if (!result.handled()) {
            return false;
        }

        applyResult(player, result);
        if (result.message() != null) {
            player.displayClientMessage(Component.literal(result.message()), true);
        }
        broadcastChanges();
        return true;
    }

    @Override
    public ItemStack quickMoveStack(Player player, int slotIndex) {
        Slot slot = slots.get(slotIndex);
        if (!slot.hasItem()) {
            return ItemStack.EMPTY;
        }

        ItemStack source = slot.getItem();
        ItemStack copy = source.copy();

        if (slotIndex < INPUT_SLOT_COUNT) {
            if (!moveItemStackTo(source, PLAYER_INV_START, HOTBAR_END, true)) {
                return ItemStack.EMPTY;
            }
        } else if (!moveItemStackTo(source, INPUT_START, INPUT_SLOT_COUNT, false)) {
            return ItemStack.EMPTY;
        }

        if (source.isEmpty()) {
            slot.setByPlayer(ItemStack.EMPTY);
        } else {
            slot.setChanged();
        }
        return copy;
    }

    @Override
    public void removed(Player player) {
        super.removed(player);
        if (!player.level().isClientSide()) {
            clearContainer(player, input);
        }
    }

    @Override
    public boolean stillValid(Player player) {
        return true;
    }

    private void addInputSlots() {
        for (int row = 0; row < 3; row++) {
            for (int col = 0; col < 3; col++) {
                int index = col + row * 3;
                addSlot(new Slot(input, index, 26 + col * 18, 47 + row * 18));
            }
        }
    }

    private void addPlayerInventorySlots(Inventory inventory) {
        for (int row = 0; row < PLAYER_INV_ROWS; row++) {
            for (int col = 0; col < PLAYER_INV_COLUMNS; col++) {
                int slotIndex = col + row * PLAYER_INV_COLUMNS + HOTBAR_SLOT_COUNT;
                addSlot(new Slot(inventory, slotIndex, 8 + col * 18, 108 + row * 18));
            }
        }
    }

    private void addPlayerHotbarSlots(Inventory inventory) {
        for (int col = 0; col < HOTBAR_SLOT_COUNT; col++) {
            addSlot(new Slot(inventory, col, 8 + col * 18, 166));
        }
    }

    private List<WorkstationSlotInput> snapshotInputSlots() {
        List<WorkstationSlotInput> snapshots = new ArrayList<>(INPUT_SLOT_COUNT);
        for (int i = 0; i < INPUT_SLOT_COUNT; i++) {
            ItemStack stack = input.getItem(i);
            snapshots.add(new WorkstationSlotInput(i, itemId(stack), stack.getCount(), snapshotBook(stack)));
        }
        return snapshots;
    }

    private WorkstationBookDraft buildDraft(String actionId) {
        if (!"write_draft".equals(actionId)) {
            return null;
        }
        for (int i = 0; i < INPUT_SLOT_COUNT; i++) {
            ItemStack stack = input.getItem(i);
            if (stack.isEmpty()) {
                continue;
            }
            WorkstationBookSnapshot snapshot = snapshotBook(stack);
            String title = snapshot != null && !snapshot.title().isBlank() ? snapshot.title() : "Player Draft";
            List<String> pages = snapshot != null && !snapshot.pages().isEmpty()
                ? snapshot.pages()
                : List.of("New draft entry.");
            return new WorkstationBookDraft(title, pages);
        }
        return null;
    }

    private static String toActionId(int buttonId) {
        return switch (buttonId) {
            case ACTION_SALVAGE_ALL -> "salvage_all";
            case ACTION_COPY_BOOKS -> "copy_books";
            case ACTION_EDIT_PLAYER_BOOK -> "edit_player_book";
            case ACTION_WRITE_DRAFT -> "write_draft";
            default -> null;
        };
    }

    private static String itemId(ItemStack stack) {
        if (stack.isEmpty()) {
            return "minecraft:air";
        }
        return BuiltInRegistries.ITEM.getKey(stack.getItem()).toString();
    }

    private static WorkstationBookSnapshot snapshotBook(ItemStack stack) {
        if (!stack.has(DataComponents.WRITTEN_BOOK_CONTENT)) {
            return null;
        }
        String title = stack.getHoverName().getString();
        if (title == null || title.isBlank()) {
            title = "Untitled";
        }
        return new WorkstationBookSnapshot(title, "unknown", List.of(), null);
    }

    private void applyResult(Player player, WorkstationActionResult result) {
        for (WorkstationSlotDelta delta : result.slotDeltas()) {
            int slotIndex = delta.slotIndex();
            if (slotIndex < 0 || slotIndex >= INPUT_SLOT_COUNT) {
                continue;
            }
            int consumeCount = delta.consumeCount();
            if (consumeCount <= 0) {
                continue;
            }
            input.getItem(slotIndex).shrink(consumeCount);
        }

        for (ItemGrant grant : result.itemGrants()) {
            Item item = resolveItem(grant.itemId());
            if (item == null) {
                continue;
            }
            giveOrDrop(player, new ItemStack(item, grant.count()));
        }

        for (WorkstationPlayerBookGrant grant : result.playerBookGrants()) {
            giveOrDrop(player, createPlayerOwnedBook(player, grant));
        }
    }

    private static Item resolveItem(String itemId) {
        Identifier id = Identifier.tryParse(itemId);
        if (id == null) {
            return null;
        }
        return BuiltInRegistries.ITEM.getValue(id);
    }

    private static ItemStack createPlayerOwnedBook(Player player, WorkstationPlayerBookGrant grant) {
        String title = truncate(grant.title(), WrittenBookContent.TITLE_MAX_LENGTH);
        List<Filterable<Component>> pages = toBookPages(grant.pages());
        WrittenBookContent content = new WrittenBookContent(
            Filterable.passThrough(title),
            player.getName().getString(),
            0,
            pages,
            true
        );
        ItemStack stack = new ItemStack(Items.WRITTEN_BOOK, 1);
        stack.set(DataComponents.WRITTEN_BOOK_CONTENT, content);
        return stack;
    }

    private static List<Filterable<Component>> toBookPages(List<String> pages) {
        List<Filterable<Component>> components = new ArrayList<>();
        int maxPages = WritableBookContent.MAX_PAGES;
        for (String page : pages) {
            if (components.size() >= maxPages) {
                break;
            }
            String bounded = page;
            if (bounded.length() > WrittenBookContent.PAGE_LENGTH) {
                bounded = bounded.substring(0, WrittenBookContent.PAGE_LENGTH);
            }
            components.add(Filterable.passThrough(Component.literal(bounded)));
        }
        if (components.isEmpty()) {
            components.add(Filterable.passThrough(Component.literal("")));
        }
        return components;
    }

    private static String truncate(String value, int maxLength) {
        if (value == null || value.isBlank()) {
            return "Untitled";
        }
        if (value.length() <= maxLength) {
            return value;
        }
        return value.substring(0, maxLength);
    }

    private static void giveOrDrop(Player player, ItemStack stack) {
        if (stack.isEmpty()) {
            return;
        }
        boolean added = player.getInventory().add(stack);
        if (!added) {
            player.drop(stack, false);
        }
    }
}
