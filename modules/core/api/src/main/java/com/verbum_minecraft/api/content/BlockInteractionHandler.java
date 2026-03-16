package com.verbum_minecraft.api.content;

/**
 * Pure capsule-owned handler for block interactions.
 */
public interface BlockInteractionHandler {
    BlockInteractionResult use(BlockInteractionContext context);
}
