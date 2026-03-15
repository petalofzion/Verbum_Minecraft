package com.verbum_minecraft.api.content;

import java.util.List;
import java.util.Objects;

/**
 * Pure workstation action request emitted by assembly-side UI wiring.
 */
public record WorkstationActionRequest(
    String actionId,
    List<WorkstationSlotInput> inputSlots,
    String playerName,
    boolean creativeMode,
    WorkstationBookDraft draftBook
) {
    public WorkstationActionRequest {
        if (actionId == null || actionId.isBlank()) {
            throw new IllegalArgumentException("actionId is blank");
        }
        Objects.requireNonNull(inputSlots, "inputSlots");
        if (playerName == null || playerName.isBlank()) {
            throw new IllegalArgumentException("playerName is blank");
        }
        inputSlots = List.copyOf(inputSlots);
    }
}
