package com.verbum_minecraft.api.content;

/**
 * Pure interaction context passed from assembly wiring into capsule-owned block handlers.
 */
public record BlockInteractionContext(
    String heldItemId,
    boolean sneaking,
    boolean creativeMode
) {
}
