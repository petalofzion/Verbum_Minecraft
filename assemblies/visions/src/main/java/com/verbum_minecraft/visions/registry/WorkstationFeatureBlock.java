package com.verbum_minecraft.visions.registry;

import com.verbum_minecraft.api.content.BlockWorkstationHandler;
import com.verbum_minecraft.runtime.content.ContentBehaviorResolver;
import net.minecraft.network.chat.Component;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.SimpleMenuProvider;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;

final class WorkstationFeatureBlock extends Block {
    private final BlockWorkstationHandler handler;

    WorkstationFeatureBlock(BlockBehaviour.Properties properties, String behaviorId) {
        super(properties);
        this.handler = ContentBehaviorResolver.resolveWorkstation(behaviorId);
        LibrariansDeskWorkstationMenu.ensureClientScreenRegistration();
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

        player.openMenu(new SimpleMenuProvider(
            (containerId, playerInventory, ignored) -> new LibrariansDeskWorkstationMenu(containerId, playerInventory, handler),
            Component.translatable("container.verbum.librarians_desk")
        ));
        return InteractionResult.CONSUME;
    }

}
