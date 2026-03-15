package com.verbum_minecraft.api.content;

/**
 * Pure description of an item stack granted by an interaction.
 */
public record ItemGrant(String itemId, int count) {
    public ItemGrant {
        if (itemId == null || itemId.isBlank()) {
            throw new IllegalArgumentException("itemId is blank");
        }
        if (count <= 0) {
            throw new IllegalArgumentException("count must be > 0");
        }
    }
}
