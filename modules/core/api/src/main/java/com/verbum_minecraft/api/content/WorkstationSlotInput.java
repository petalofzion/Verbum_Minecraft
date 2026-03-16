package com.verbum_minecraft.api.content;

/**
 * Pure workstation input slot snapshot.
 */
public record WorkstationSlotInput(
    int slotIndex,
    String itemId,
    int count,
    WorkstationBookSnapshot book
) {
    public WorkstationSlotInput {
        if (slotIndex < 0) {
            throw new IllegalArgumentException("slotIndex must be >= 0");
        }
        if (itemId == null || itemId.isBlank()) {
            throw new IllegalArgumentException("itemId is blank");
        }
        if (count < 0) {
            throw new IllegalArgumentException("count must be >= 0");
        }
    }
}
