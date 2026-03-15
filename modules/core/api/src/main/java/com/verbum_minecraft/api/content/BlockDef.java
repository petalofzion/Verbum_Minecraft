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
    String interactionBehaviorId,
    String workstationBehaviorId
) {
    public BlockDef(
        VerbumId id,
        float destroyTime,
        float explosionResistance,
        String creativeTabKey,
        String soundTypeKey,
        String interactionBehaviorId
    ) {
        this(id, destroyTime, explosionResistance, creativeTabKey, soundTypeKey, interactionBehaviorId, null);
    }

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
        if (interactionBehaviorId != null && interactionBehaviorId.isBlank()) {
            throw new IllegalArgumentException("interactionBehaviorId is blank");
        }
        if (workstationBehaviorId != null && workstationBehaviorId.isBlank()) {
            throw new IllegalArgumentException("workstationBehaviorId is blank");
        }
        if (interactionBehaviorId != null && workstationBehaviorId != null) {
            throw new IllegalArgumentException("BlockDef cannot define both interaction and workstation behaviors");
        }
    }

    public boolean hasInteractionBehavior() {
        return interactionBehaviorId != null;
    }

    public boolean hasWorkstationBehavior() {
        return workstationBehaviorId != null;
    }
}
