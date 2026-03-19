package com.verbum_minecraft.veritas.client;

import net.fabricmc.fabric.api.client.command.v2.ClientCommandRegistrationCallback;
import net.fabricmc.fabric.api.client.command.v2.ClientCommands;
import net.fabricmc.fabric.api.client.rendering.v1.PictureInPictureRendererRegistry;
import net.fabricmc.api.ClientModInitializer;
import net.minecraft.client.Minecraft;
import net.minecraft.network.chat.Component;

public final class AssetPreviewClient implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
        PictureInPictureRendererRegistry.register(context ->
            new HeldItemPictureInPictureRenderer(
                context.minecraft(),
                context.minecraft().getEntityRenderDispatcher().getItemInHandRenderer(),
                context.submitNodeCollector()
            )
        );
        ClientCommandRegistrationCallback.EVENT.register((dispatcher, buildContext) ->
            dispatcher.register(
                ClientCommands.literal("assetpreview")
                    .executes(context -> openPreview(context.getSource().getClient(), true))
                    .then(
                        ClientCommands.literal("open")
                            .executes(context -> openPreview(context.getSource().getClient(), true))
                    )
            )
        );
    }

    private static int openPreview(Minecraft client, boolean reportToChat) {
        client.execute(() -> client.setScreen(new AssetPreviewScreen()));
        if (reportToChat && client.player != null) {
            client.player.sendSystemMessage(Component.literal("Opened Asset Preview."));
        }
        return 1;
    }
}
