package com.verbum_minecraft.veritas.client;

import com.mojang.authlib.GameProfile;
import java.lang.reflect.Field;
import java.util.UUID;
import java.util.function.Supplier;
import net.fabricmc.api.EnvType;
import net.fabricmc.api.Environment;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.CycleButton;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.client.gui.components.PlayerSkinWidget;
import net.minecraft.client.gui.navigation.ScreenRectangle;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.player.RemotePlayer;
import net.minecraft.client.renderer.state.gui.GuiRenderState;
import net.minecraft.core.ClientAsset;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.HumanoidArm;
import net.minecraft.world.entity.player.PlayerModelType;
import net.minecraft.world.entity.player.PlayerSkin;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;

@Environment(EnvType.CLIENT)
final class AssetPreviewScreen extends Screen {
    private static final Field GUI_RENDER_STATE_FIELD = resolveGuiRenderStateField();
    private static final String DEFAULT_SKIN_TEXTURE = "verbum_debug:textures/entity/preview/smoke_scribe_skin.png";
    private static final String DEFAULT_ITEM_TEXTURE = "verbum_debug:textures/item/preview/smoke_bible_icon.png";
    private static final String DEFAULT_ITEM_ID = "verbum:bible";
    private static final int PANEL_PADDING = 12;
    private static final int CONTROLS_PANEL_HEIGHT = 170;
    private static final int PREVIEW_INNER_PADDING = 12;

    private PreviewMode mode = PreviewMode.PLAYER_SKIN;
    private HeldPose heldPose = HeldPose.THIRD_PERSON_RIGHT_HAND;
    private EditBox textureIdBox;
    private EditBox itemIdBox;
    private CycleButton<PreviewMode> modeButton;
    private CycleButton<HeldPose> poseButton;
    private PlayerSkinWidget skinWidget;
    private PreviewRemotePlayer previewPlayer;
    private Component statusLine = Component.literal("Stage a debug asset, then paste its resource identifier here.");

    AssetPreviewScreen() {
        super(Component.literal("Verbum Asset Preview"));
    }

    @Override
    protected void init() {
        super.init();
        int left = settingsPanelLeft();
        int top = PANEL_PADDING;
        int fieldWidth = settingsPanelWidth() - 20;
        Minecraft minecraft = Minecraft.getInstance();

        this.modeButton = addRenderableWidget(
            CycleButton.builder(PreviewMode::label, mode)
                .withValues(PreviewMode.values())
                .create(left, top, fieldWidth, 20, Component.literal("Mode"), (button, value) -> {
                    mode = value;
                    updateStatusLine();
                    updateWidgetVisibility();
                })
        );

        this.poseButton = addRenderableWidget(
            CycleButton.builder(HeldPose::label, heldPose)
                .withValues(HeldPose.values())
                .create(left, top + 28, fieldWidth, 20, Component.literal("Held Pose"), (button, value) -> {
                    heldPose = value;
                    updateStatusLine();
                })
        );

        this.textureIdBox = new EditBox(font, left, top + 62, fieldWidth, 18, Component.literal("Texture"));
        this.textureIdBox.setMaxLength(256);
        this.textureIdBox.setValue(DEFAULT_SKIN_TEXTURE);
        addRenderableWidget(textureIdBox);

        this.itemIdBox = new EditBox(font, left, top + 94, fieldWidth, 18, Component.literal("Item"));
        this.itemIdBox.setMaxLength(256);
        this.itemIdBox.setValue(DEFAULT_ITEM_ID);
        addRenderableWidget(itemIdBox);

        addRenderableWidget(
            Button.builder(Component.literal("Defaults"), button -> resetDefaults())
                .bounds(left, top + 126, 72, 20)
                .build()
        );
        addRenderableWidget(
            Button.builder(Component.literal("Close"), button -> onClose())
                .bounds(left + fieldWidth - 72, top + 126, 72, 20)
                .build()
        );

        this.skinWidget = addRenderableWidget(
            new PlayerSkinWidget(
                previewInnerWidth(),
                previewInnerHeight(),
                minecraft.getEntityModels(),
                new Supplier<>() {
                    @Override
                    public PlayerSkin get() {
                        return resolvePreviewSkin();
                    }
                }
            )
        );
        this.skinWidget.setPosition(previewInnerLeft(), previewInnerTop());

        this.previewPlayer = createPreviewPlayer(minecraft);
        updateWidgetVisibility();
        updateStatusLine();
    }

    private void resetDefaults() {
        textureIdBox.setValue(mode == PreviewMode.PLAYER_SKIN ? DEFAULT_SKIN_TEXTURE : DEFAULT_ITEM_TEXTURE);
        itemIdBox.setValue(DEFAULT_ITEM_ID);
        heldPose = HeldPose.THIRD_PERSON_RIGHT_HAND;
        if (poseButton != null) {
            poseButton.setValue(heldPose);
        }
        updateStatusLine();
    }

    private void updateWidgetVisibility() {
        boolean heldMode = mode == PreviewMode.ITEM_HELD;
        if (poseButton != null) {
            poseButton.visible = heldMode;
            poseButton.active = heldMode;
        }
        if (textureIdBox != null) {
            textureIdBox.visible = true;
            textureIdBox.active = true;
        }
        if (itemIdBox != null) {
            itemIdBox.visible = mode != PreviewMode.PLAYER_SKIN;
            itemIdBox.active = mode != PreviewMode.PLAYER_SKIN;
        }
        if (skinWidget != null) {
            skinWidget.visible = mode == PreviewMode.PLAYER_SKIN;
            skinWidget.active = mode == PreviewMode.PLAYER_SKIN;
        }
    }

    @Override
    public void extractRenderState(GuiGraphicsExtractor guiGraphics, int mouseX, int mouseY, float delta) {
        extractTransparentBackground(guiGraphics);
        guiGraphics.fill(0, 0, width, height, 0xC0101010);
        super.extractRenderState(guiGraphics, mouseX, mouseY, delta);

        int left = PANEL_PADDING;
        guiGraphics.text(font, title, left, 6, 0xFFFFFF, false);
        guiGraphics.text(font, Component.literal("Texture"), left, 52, 0xA0A0A0, false);
        guiGraphics.text(font, Component.literal("Item Registry Id"), left, 84, 0xA0A0A0, false);
        guiGraphics.textWithWordWrap(font, statusLine, left, height - 52, settingsPanelWidth(), 0xD0D0D0);
        guiGraphics.fill(previewPanelLeft(), previewPanelTop(), previewPanelLeft() + previewPanelWidth(), previewPanelTop() + previewPanelHeight(), 0x90303036);
        guiGraphics.outline(previewPanelLeft(), previewPanelTop(), previewPanelWidth(), previewPanelHeight(), 0xFF6C6C78);
        guiGraphics.enableScissor(previewPanelLeft(), previewPanelTop(), previewPanelLeft() + previewPanelWidth(), previewPanelTop() + previewPanelHeight());
        renderPreview(guiGraphics);
        guiGraphics.disableScissor();
    }

    private void renderPreview(GuiGraphicsExtractor guiGraphics) {
        switch (mode) {
            case PLAYER_SKIN -> renderSkinPreview(guiGraphics);
            case ITEM_ICON -> renderItemIconPreview(guiGraphics);
            case ITEM_HELD -> renderHeldItemPreview(guiGraphics);
        }
    }

    private void renderSkinPreview(GuiGraphicsExtractor guiGraphics) {
        Identifier textureId = parseIdentifier(textureIdBox.getValue());
        if (textureId == null) {
            guiGraphics.textWithWordWrap(font, Component.literal("Enter a staged skin texture resource, e.g. verbum_debug:textures/entity/preview/smoke_scribe_skin.png"), previewPanelLeft() + 14, previewPanelTop() + 18, previewPanelWidth() - 28, 0xFF8888);
            return;
        }
        if (!resourceExists(textureId)) {
            guiGraphics.textWithWordWrap(font, Component.literal("Missing staged skin resource: " + textureId), previewInnerLeft(), previewInnerTop(), previewInnerWidth(), 0xFF8888);
            return;
        }
        guiGraphics.text(font, Component.literal(textureId.toString()), previewPanelLeft() + 12, previewPanelTop() - 16, 0xD0D0D0, false);
    }

    private void renderItemIconPreview(GuiGraphicsExtractor guiGraphics) {
        ItemStack stack = resolvePreviewItemStack();
        int panelLeft = previewPanelLeft();
        int panelTop = previewPanelTop();
        int innerLeft = previewInnerLeft();
        int innerTop = previewInnerTop();
        int innerWidth = previewInnerWidth();
        int innerHeight = previewInnerHeight();
        if (!stack.isEmpty()) {
            guiGraphics.text(font, Component.literal("Registered item icon"), innerLeft, innerTop, 0xD0D0D0, false);
            int nativeX = innerLeft;
            int nativeY = innerTop + 28;
            guiGraphics.item(stack, nativeX, nativeY);
            guiGraphics.itemDecorations(font, stack, nativeX, nativeY);
            float inspectScale = Math.min(Math.max((innerHeight - 48) / 16.0F, 3.0F), 7.0F);
            int inspectX = nativeX + 88;
            int inspectY = innerTop + Math.max(28, (innerHeight / 2) - Math.round((16 * inspectScale) / 2.0F));
            renderScaledItem(guiGraphics, stack, inspectX, inspectY, inspectScale);
            return;
        }

        Identifier textureId = parseIdentifier(textureIdBox.getValue());
        if (textureId == null || !resourceExists(textureId)) {
            guiGraphics.textWithWordWrap(font, Component.literal("Enter either a registered item id or a staged item texture resource."), innerLeft, innerTop, innerWidth, 0xFF8888);
            return;
        }

        guiGraphics.text(font, Component.literal("Staged icon texture"), innerLeft, innerTop, 0xD0D0D0, false);
        int smallSize = Math.min(64, Math.max(24, innerHeight / 3));
        int largeSize = Math.min(innerWidth - 96, innerHeight - 36);
        largeSize = Math.max(48, largeSize);
        guiGraphics.blit(textureId, innerLeft, innerTop + 28, smallSize, smallSize, 0.0F, 0.0F, 1.0F, 1.0F);
        guiGraphics.blit(textureId, innerLeft + smallSize + 24, innerTop + Math.max(20, (innerHeight - largeSize) / 2), largeSize, largeSize, 0.0F, 0.0F, 1.0F, 1.0F);
    }

    private void renderHeldItemPreview(GuiGraphicsExtractor guiGraphics) {
        ItemStack stack = resolvePreviewItemStack();
        if (stack.isEmpty()) {
            guiGraphics.textWithWordWrap(font, Component.literal("Held-item preview requires a registered item id."), previewPanelLeft() + 18, previewPanelTop() + 18, previewPanelWidth() - 24, 0xFF8888);
            return;
        }
        if (previewPlayer == null) {
            guiGraphics.textWithWordWrap(font, Component.literal("Held-item preview requires an active client level."), previewPanelLeft() + 18, previewPanelTop() + 18, previewPanelWidth() - 24, 0xFF8888);
            return;
        }

        previewPlayer.setItemInHand(InteractionHand.MAIN_HAND, stack.copy());
        int panelLeft = previewPanelLeft();
        int panelTop = previewPanelTop();
        int innerLeft = previewInnerLeft();
        int innerTop = previewInnerTop();
        int innerWidth = previewInnerWidth();
        int innerHeight = previewInnerHeight();
        if (heldPose == HeldPose.THIRD_PERSON_RIGHT_HAND) {
            guiGraphics.text(font, Component.literal("Third-person held preview"), panelLeft + 12, panelTop - 16, 0xD0D0D0, false);
            renderHeldItemPictureInPicture(
                guiGraphics,
                stack,
                ItemDisplayContext.THIRD_PERSON_RIGHT_HAND,
                innerLeft,
                innerTop,
                innerLeft + innerWidth,
                innerTop + innerHeight,
                Math.min(innerWidth, innerHeight) / 30.0F
            );
            renderScaledItem(guiGraphics, stack, innerLeft + innerWidth - 64, innerTop + innerHeight - 64, 2.5F);
            return;
        }

        guiGraphics.text(font, Component.literal("First-person right-hand review"), panelLeft + 12, panelTop - 16, 0xD0D0D0, false);
        renderHeldItemPictureInPicture(
            guiGraphics,
            stack,
            ItemDisplayContext.FIRST_PERSON_RIGHT_HAND,
            innerLeft,
            innerTop,
            innerLeft + innerWidth,
            innerTop + innerHeight,
            Math.min(innerWidth, innerHeight) / 24.0F
        );
        renderScaledItem(guiGraphics, stack, innerLeft + 8, innerTop + innerHeight - 44, 2.0F);
        renderScaledItem(guiGraphics, stack, innerLeft + 48, innerTop + innerHeight - 52, 3.0F);
    }

    private void updateStatusLine() {
        statusLine = switch (mode) {
            case PLAYER_SKIN -> Component.literal("Paste a staged skin texture identifier such as verbum_debug:textures/entity/preview/smoke_scribe_skin.png. Drag the model to inspect rotation.");
            case ITEM_ICON -> Component.literal("Use a registered item id for GUI rendering, or paste a staged texture identifier for raw icon inspection. The panel shows both a native-size icon and a larger review render.");
            case ITEM_HELD -> Component.literal("Held preview uses a registered item id and now renders through the real first-person and third-person right-hand in-hand renderer path. The larger item renders remain for readability checks.");
        };
    }

    private ItemStack resolvePreviewItemStack() {
        Identifier itemId = parseIdentifier(itemIdBox.getValue());
        if (itemId == null) {
            return ItemStack.EMPTY;
        }
        Item item = BuiltInRegistries.ITEM.getValue(itemId);
        if (item == null) {
            return ItemStack.EMPTY;
        }
        return new ItemStack(item);
    }

    private PlayerSkin resolvePreviewSkin() {
        Identifier textureId = parseIdentifier(textureIdBox.getValue());
        if (textureId == null) {
            textureId = Identifier.fromNamespaceAndPath("minecraft", "textures/entity/steve.png");
        }
        ClientAsset.Texture body = new ClientAsset.ResourceTexture(textureId, textureId);
        return PlayerSkin.insecure(body, body, body, PlayerModelType.WIDE);
    }

    private PreviewRemotePlayer createPreviewPlayer(Minecraft minecraft) {
        ClientLevel level = minecraft.level;
        if (level == null) {
            return null;
        }
        PreviewRemotePlayer player = new PreviewRemotePlayer(level, new GameProfile(UUID.fromString("b5eecf15-6cbe-458b-bf7f-e348c8c317b2"), "verbum_preview"));
        player.setNoGravity(true);
        player.setOnGround(true);
        player.setItemInHand(InteractionHand.MAIN_HAND, ItemStack.EMPTY);
        player.setItemInHand(InteractionHand.OFF_HAND, ItemStack.EMPTY);
        return player;
    }

    private Identifier parseIdentifier(String value) {
        if (value == null || value.isBlank()) {
            return null;
        }
        return Identifier.tryParse(value.trim());
    }

    private boolean resourceExists(Identifier textureId) {
        return Minecraft.getInstance().getResourceManager().getResource(textureId).isPresent();
    }

    private void renderScaledItem(GuiGraphicsExtractor guiGraphics, ItemStack stack, int x, int y, float scale) {
        guiGraphics.pose().pushMatrix();
        guiGraphics.pose().translate(x, y);
        guiGraphics.pose().scale(scale, scale);
        guiGraphics.item(stack, 0, 0);
        guiGraphics.pose().popMatrix();
    }

    private void renderHeldItemPictureInPicture(
        GuiGraphicsExtractor guiGraphics,
        ItemStack stack,
        ItemDisplayContext displayContext,
        int x0,
        int y0,
        int x1,
        int y1,
        float scale
    ) {
        GuiRenderState renderState = guiRenderState(guiGraphics);
        if (renderState == null) {
            return;
        }
        renderState.addPicturesInPictureState(
            new HeldItemRenderState(
                previewPlayer,
                stack.copy(),
                displayContext,
                x0,
                y0,
                x1,
                y1,
                scale,
                new ScreenRectangle(previewPanelLeft(), previewPanelTop(), previewPanelWidth(), previewPanelHeight())
            )
        );
    }

    private GuiRenderState guiRenderState(GuiGraphicsExtractor guiGraphics) {
        if (GUI_RENDER_STATE_FIELD == null) {
            return null;
        }
        try {
            return (GuiRenderState) GUI_RENDER_STATE_FIELD.get(guiGraphics);
        } catch (IllegalAccessException ignored) {
            return null;
        }
    }

    private static Field resolveGuiRenderStateField() {
        try {
            Field field = GuiGraphicsExtractor.class.getDeclaredField("guiRenderState");
            field.setAccessible(true);
            return field;
        } catch (ReflectiveOperationException ignored) {
            return null;
        }
    }

    private int settingsPanelLeft() {
        return PANEL_PADDING;
    }

    private int settingsPanelWidth() {
        if (useStackedLayout()) {
            return Math.max(1, width - (PANEL_PADDING * 2));
        }
        int available = width - (PANEL_PADDING * 2) - 18;
        return Mth.clamp(width / 3, Math.max(1, Math.min(180, available)), Math.max(1, Math.min(300, available)));
    }

    private int previewPanelLeft() {
        if (useStackedLayout()) {
            return PANEL_PADDING;
        }
        return settingsPanelLeft() + settingsPanelWidth() + 18;
    }

    private int previewPanelTop() {
        if (useStackedLayout()) {
            return PANEL_PADDING + CONTROLS_PANEL_HEIGHT;
        }
        return 34;
    }

    private int previewPanelWidth() {
        return Math.max(1, width - previewPanelLeft() - PANEL_PADDING);
    }

    private int previewPanelHeight() {
        return Math.max(1, height - previewPanelTop() - PANEL_PADDING);
    }

    private int previewInnerLeft() {
        return previewPanelLeft() + PREVIEW_INNER_PADDING;
    }

    private int previewInnerTop() {
        return previewPanelTop() + PREVIEW_INNER_PADDING;
    }

    private int previewInnerWidth() {
        return Math.max(1, previewPanelWidth() - (PREVIEW_INNER_PADDING * 2));
    }

    private int previewInnerHeight() {
        return Math.max(1, previewPanelHeight() - (PREVIEW_INNER_PADDING * 2));
    }

    private boolean useStackedLayout() {
        return false;
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }

    private enum PreviewMode {
        ITEM_ICON("Item Icon"),
        ITEM_HELD("Item Held"),
        PLAYER_SKIN("Player Skin");

        private final Component label;

        PreviewMode(String label) {
            this.label = Component.literal(label);
        }

        Component label() {
            return label;
        }
    }

    private enum HeldPose {
        FIRST_PERSON_RIGHT_HAND("First Person"),
        THIRD_PERSON_RIGHT_HAND("Third Person");

        private final Component label;

        HeldPose(String label) {
            this.label = Component.literal(label);
        }

        Component label() {
            return label;
        }
    }

    private final class PreviewRemotePlayer extends RemotePlayer {
        PreviewRemotePlayer(ClientLevel level, GameProfile gameProfile) {
            super(level, gameProfile);
        }

        @Override
        public PlayerSkin getSkin() {
            return resolvePreviewSkin();
        }

        @Override
        public boolean isModelPartShown(net.minecraft.world.entity.player.PlayerModelPart playerModelPart) {
            return true;
        }

        @Override
        public HumanoidArm getMainArm() {
            return HumanoidArm.RIGHT;
        }
    }
}
