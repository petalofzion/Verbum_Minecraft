package com.verbum_minecraft.api.content;

/**
 * Pure data definition for an Item.
 */
public record ItemDef(
    VerbumId id,
    int maxStackSize,
    boolean fireproof,
    int rarityOrdinal,
    String creativeTabKey
) {
    public static final int RARITY_COMMON = 0;
    public static final int RARITY_UNCOMMON = 1;
    public static final int RARITY_RARE = 2;
    public static final int RARITY_EPIC = 3;
}
