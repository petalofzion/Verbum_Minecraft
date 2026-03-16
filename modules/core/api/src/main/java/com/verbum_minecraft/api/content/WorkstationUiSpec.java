package com.verbum_minecraft.api.content;

/**
 * Pure workstation UI capability description for assembly menu wiring.
 */
public record WorkstationUiSpec(
    int inputSlots,
    boolean batchSalvageEnabled,
    boolean playerCopyEnabled,
    boolean playerWriteEnabled
) {
    public WorkstationUiSpec {
        if (inputSlots <= 0) {
            throw new IllegalArgumentException("inputSlots must be > 0");
        }
    }
}
