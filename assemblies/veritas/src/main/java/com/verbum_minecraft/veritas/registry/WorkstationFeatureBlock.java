package com.verbum_minecraft.veritas.registry;

import com.verbum_minecraft.api.content.BlockWorkstationHandler;
import com.verbum_minecraft.api.content.ItemGrant;
import com.verbum_minecraft.api.content.WorkstationActionRequest;
import com.verbum_minecraft.api.content.WorkstationActionResult;
import com.verbum_minecraft.api.content.WorkstationBookSnapshot;
import com.verbum_minecraft.api.content.WorkstationPlayerBookGrant;
import com.verbum_minecraft.api.content.WorkstationSlotDelta;
import com.verbum_minecraft.api.content.WorkstationSlotInput;
import com.verbum_minecraft.runtime.content.ContentBehaviorResolver;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.server.network.Filterable;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.component.WritableBookContent;
import net.minecraft.world.item.component.WrittenBookContent;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

final class WorkstationFeatureBlock extends Block {
    private static final Logger LOGGER = LoggerFactory.getLogger(WorkstationFeatureBlock.class);
    private static final int MAX_WORKSTATION_INPUTS = 27;

    private final BlockWorkstationHandler handler;
    private final int inputSlots;

    WorkstationFeatureBlock(BlockBehaviour.Properties properties, String behaviorId) {
        super(properties);
        this.handler = ContentBehaviorResolver.resolveWorkstation(behaviorId);
        this.inputSlots = Math.min(this.handler.uiSpec().inputSlots(), MAX_WORKSTATION_INPUTS);
    }

    @Override
    protected InteractionResult useItemOn(
        ItemStack stack,
        BlockState state,
        Level level,
        net.minecraft.core.BlockPos pos,
        Player player,
        InteractionHand hand,
        BlockHitResult hit
    ) {
        if (level.isClientSide()) {
            return InteractionResult.SUCCESS;
        }

        List<ItemStack> inputs = collectInputSlots(player, inputSlots);
        WorkstationActionRequest request = new WorkstationActionRequest(
            "open",
            snapshotInputs(inputs),
            player.getName().getString(),
            player.getAbilities().instabuild,
            null
        );
        WorkstationActionResult result = handler.apply(request);
        if (!result.handled()) {
            return InteractionResult.PASS;
        }

        applyResult(player, inputs, result);
        if (result.message() != null) {
            player.sendSystemMessage(Component.literal(result.message()));
        }
        return InteractionResult.SUCCESS;
    }

    private static List<ItemStack> collectInputSlots(Player player, int inputSlots) {
        int available = player.getInventory().getContainerSize();
        int count = Math.min(inputSlots, available);
        List<ItemStack> slots = new ArrayList<>(count);
        for (int i = 0; i < count; i++) {
            slots.add(player.getInventory().getItem(i));
        }
        return slots;
    }

    private static List<WorkstationSlotInput> snapshotInputs(List<ItemStack> slots) {
        List<WorkstationSlotInput> snapshots = new ArrayList<>(slots.size());
        for (int i = 0; i < slots.size(); i++) {
            ItemStack stack = slots.get(i);
            snapshots.add(new WorkstationSlotInput(i, itemId(stack), stack.getCount(), snapshotBook(stack)));
        }
        return snapshots;
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

    private static String itemId(ItemStack stack) {
        if (stack.isEmpty()) {
            return "minecraft:air";
        }
        return BuiltInRegistries.ITEM.getKey(stack.getItem()).toString();
    }

    private static void applyResult(Player player, List<ItemStack> inputs, WorkstationActionResult result) {
        applySlotDeltas(inputs, result.slotDeltas());
        grantItems(player, result.itemGrants());
        grantPlayerOwnedBooks(player, result.playerBookGrants());
    }

    private static void applySlotDeltas(List<ItemStack> inputs, List<WorkstationSlotDelta> deltas) {
        for (WorkstationSlotDelta delta : deltas) {
            int slotIndex = delta.slotIndex();
            if (slotIndex < 0 || slotIndex >= inputs.size()) {
                LOGGER.warn("Ignoring workstation slot delta outside input range: {}", slotIndex);
                continue;
            }
            int consume = delta.consumeCount();
            if (consume <= 0) {
                continue;
            }
            inputs.get(slotIndex).shrink(consume);
        }
    }

    private static void grantItems(Player player, List<ItemGrant> grants) {
        for (ItemGrant grant : grants) {
            Item item = resolveItem(grant.itemId());
            if (item == null) {
                continue;
            }
            ItemStack stack = new ItemStack(item, grant.count());
            giveOrDrop(player, stack);
        }
    }

    private static void grantPlayerOwnedBooks(Player player, List<WorkstationPlayerBookGrant> grants) {
        for (WorkstationPlayerBookGrant grant : grants) {
            ItemStack stack = createPlayerOwnedBook(player, grant);
            giveOrDrop(player, stack);
        }
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

    private static void giveOrDrop(Player player, ItemStack stack) {
        boolean added = player.getInventory().add(stack);
        if (!added) {
            player.drop(stack, false);
        }
    }

    private static Item resolveItem(String itemId) {
        Identifier id = Identifier.tryParse(itemId);
        if (id == null) {
            LOGGER.warn("Invalid workstation grant item id {}", itemId);
            return null;
        }
        Item item = BuiltInRegistries.ITEM.getValue(id);
        if (item == null) {
            LOGGER.warn("Unknown workstation grant item id {}", itemId);
        }
        return item;
    }

    private static String truncate(String value, int maxLength) {
        if (value.length() <= maxLength) {
            return value;
        }
        return value.substring(0, maxLength);
    }
}
