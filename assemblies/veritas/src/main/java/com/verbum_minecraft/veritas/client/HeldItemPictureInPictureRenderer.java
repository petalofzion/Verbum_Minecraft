package com.verbum_minecraft.veritas.client;

import com.mojang.blaze3d.platform.Lighting;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.render.pip.PictureInPictureRenderer;
import net.minecraft.client.renderer.ItemInHandRenderer;
import net.minecraft.client.renderer.SubmitNodeCollector;

final class HeldItemPictureInPictureRenderer extends PictureInPictureRenderer<HeldItemRenderState> {
    private final Minecraft minecraft;
    private final ItemInHandRenderer itemInHandRenderer;
    private final SubmitNodeCollector submitNodeCollector;

    HeldItemPictureInPictureRenderer(Minecraft minecraft, ItemInHandRenderer itemInHandRenderer, SubmitNodeCollector submitNodeCollector) {
        super(minecraft.renderBuffers().bufferSource());
        this.minecraft = minecraft;
        this.itemInHandRenderer = itemInHandRenderer;
        this.submitNodeCollector = submitNodeCollector;
    }

    @Override
    public Class<HeldItemRenderState> getRenderStateClass() {
        return HeldItemRenderState.class;
    }

    @Override
    protected void renderToTexture(HeldItemRenderState state, PoseStack poseStack) {
        if (state.entity() == null || state.stack().isEmpty()) {
            return;
        }

        minecraft.gameRenderer.getLighting().setupFor(Lighting.Entry.ITEMS_3D);
        poseStack.translate(0.15F, -0.10F, 0.0F);
        itemInHandRenderer.renderItem(
            state.entity(),
            state.stack(),
            state.displayContext(),
            poseStack,
            submitNodeCollector,
            minecraft.getEntityRenderDispatcher().getPackedLightCoords(state.entity(), 1.0F)
        );
    }

    @Override
    protected String getTextureLabel() {
        return "held_item_preview";
    }
}
