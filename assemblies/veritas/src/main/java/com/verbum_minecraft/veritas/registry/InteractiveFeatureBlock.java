package com.verbum_minecraft.veritas.registry;

import com.verbum_minecraft.api.content.BlockInteractionContext;
import com.verbum_minecraft.api.content.BlockInteractionHandler;
import com.verbum_minecraft.api.content.BlockInteractionResult;
import com.verbum_minecraft.api.content.ItemGrant;
import com.verbum_minecraft.runtime.content.ContentBehaviorResolver;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

final class InteractiveFeatureBlock extends Block {
    private static final Logger LOGGER = LoggerFactory.getLogger(InteractiveFeatureBlock.class);

    private final BlockInteractionHandler handler;

    InteractiveFeatureBlock(BlockBehaviour.Properties properties, String behaviorId) {
        super(properties);
        this.handler = ContentBehaviorResolver.resolveInteraction(behaviorId);
    }

    @Override
    protected InteractionResult useItemOn(
        ItemStack stack,
        BlockState state,
        Level level,
        BlockPos pos,
        Player player,
        InteractionHand hand,
        BlockHitResult hit
    ) {
        BlockInteractionContext context = new BlockInteractionContext(
            itemId(stack),
            player.isShiftKeyDown(),
            player.getAbilities().instabuild
        );
        BlockInteractionResult result = handler.use(context);
        if (!result.handled()) {
            return InteractionResult.PASS;
        }

        if (!level.isClientSide()) {
            applyResult(player, stack, result);
        }
        return InteractionResult.SUCCESS;
    }

    private static String itemId(ItemStack stack) {
        if (stack.isEmpty()) {
            return "minecraft:air";
        }
        return BuiltInRegistries.ITEM.getKey(stack.getItem()).toString();
    }

    private static void applyResult(Player player, ItemStack held, BlockInteractionResult result) {
        if (result.consumeHeldItem() && !held.isEmpty()) {
            held.shrink(1);
        }

        grantItems(player, result.grants());

        if (result.message() != null) {
            player.displayClientMessage(Component.literal(result.message()), true);
        }
    }

    private static void grantItems(Player player, List<ItemGrant> grants) {
        for (ItemGrant grant : grants) {
            Item item = resolveItem(grant.itemId());
            if (item == null) {
                continue;
            }

            ItemStack stack = new ItemStack(item, grant.count());
            boolean added = player.getInventory().add(stack);
            if (!added) {
                player.drop(stack, false);
            }
        }
    }

    private static Item resolveItem(String itemId) {
        Identifier id = Identifier.tryParse(itemId);
        if (id == null) {
            LOGGER.warn("Invalid grant item id {}", itemId);
            return null;
        }
        Item item = BuiltInRegistries.ITEM.getValue(id);
        if (item == null) {
            LOGGER.warn("Unknown grant item id {}", itemId);
        }
        return item;
    }
}
