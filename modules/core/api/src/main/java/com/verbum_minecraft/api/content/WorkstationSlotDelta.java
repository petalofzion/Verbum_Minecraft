package com.verbum_minecraft.api.content;

/**
 * Pure slot consumption directive for workstation results.
 */
public record WorkstationSlotDelta(
    int slotIndex,
    int consumeCount
) {
    public WorkstationSlotDelta {
        if (slotIndex < 0) {
            throw new IllegalArgumentException("slotIndex must be >= 0");
        }
        if (consumeCount < 0) {
            throw new IllegalArgumentException("consumeCount must be >= 0");
        }
    }
}
