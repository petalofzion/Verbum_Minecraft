package com.verbum_minecraft.api.content;

import java.util.Objects;

/**
 * Pure data definition for a placeable block with an item form.
 */
public record BlockDef(
    VerbumId id,
    float destroyTime,
    float explosionResistance,
    String creativeTabKey,
    String soundTypeKey,
    String interactionHandlerClass
) {
    public BlockDef {
        Objects.requireNonNull(id, "id");
        if (destroyTime < 0.0F) {
            throw new IllegalArgumentException("destroyTime must be >= 0");
        }
        if (explosionResistance < 0.0F) {
            throw new IllegalArgumentException("explosionResistance must be >= 0");
        }
        if (creativeTabKey == null || creativeTabKey.isBlank()) {
            throw new IllegalArgumentException("creativeTabKey is blank");
        }
        if (soundTypeKey == null || soundTypeKey.isBlank()) {
            soundTypeKey = "stone";
        }
        if (interactionHandlerClass != null && interactionHandlerClass.isBlank()) {
            throw new IllegalArgumentException("interactionHandlerClass is blank");
        }
    }

    public boolean hasInteractionHandler() {
        return interactionHandlerClass != null;
    }
}
