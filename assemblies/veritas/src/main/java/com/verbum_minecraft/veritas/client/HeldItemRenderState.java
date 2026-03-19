package com.verbum_minecraft.veritas.client;

import net.minecraft.client.gui.navigation.ScreenRectangle;
import net.minecraft.client.renderer.state.gui.pip.PictureInPictureRenderState;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;

record HeldItemRenderState(
    LivingEntity entity,
    ItemStack stack,
    ItemDisplayContext displayContext,
    int x0,
    int y0,
    int x1,
    int y1,
    float scale,
    ScreenRectangle scissorArea,
    ScreenRectangle bounds
) implements PictureInPictureRenderState {
    HeldItemRenderState(
        LivingEntity entity,
        ItemStack stack,
        ItemDisplayContext displayContext,
        int x0,
        int y0,
        int x1,
        int y1,
        float scale,
        ScreenRectangle scissorArea
    ) {
        this(entity, stack, displayContext, x0, y0, x1, y1, scale, scissorArea, PictureInPictureRenderState.getBounds(x0, y0, x1, y1, scissorArea));
    }
}
