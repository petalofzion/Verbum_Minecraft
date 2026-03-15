package com.verbum_minecraft.api.content;

import java.util.List;

/**
 * Pure result emitted by a capsule-owned block interaction handler.
 */
public record BlockInteractionResult(
    boolean handled,
    boolean consumeHeldItem,
    List<ItemGrant> grants,
    String message
) {
    public BlockInteractionResult {
        grants = grants == null ? List.of() : List.copyOf(grants);
        if (message != null && message.isBlank()) {
            throw new IllegalArgumentException("message is blank");
        }
    }

    public static BlockInteractionResult pass() {
        return new BlockInteractionResult(false, false, List.of(), null);
    }

    public static BlockInteractionResult handled(boolean consumeHeldItem, List<ItemGrant> grants, String message) {
        return new BlockInteractionResult(true, consumeHeldItem, grants, message);
    }
}
