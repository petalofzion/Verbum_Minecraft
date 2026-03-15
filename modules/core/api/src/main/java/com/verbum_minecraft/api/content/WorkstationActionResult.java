package com.verbum_minecraft.api.content;

import java.util.List;

/**
 * Pure workstation action output consumed by assembly wiring.
 */
public record WorkstationActionResult(
    boolean handled,
    List<WorkstationSlotDelta> slotDeltas,
    List<ItemGrant> itemGrants,
    List<WorkstationPlayerBookGrant> playerBookGrants,
    String message
) {
    public WorkstationActionResult {
        if (slotDeltas == null) {
            throw new IllegalArgumentException("slotDeltas is null");
        }
        if (itemGrants == null) {
            throw new IllegalArgumentException("itemGrants is null");
        }
        if (playerBookGrants == null) {
            throw new IllegalArgumentException("playerBookGrants is null");
        }
        slotDeltas = List.copyOf(slotDeltas);
        itemGrants = List.copyOf(itemGrants);
        playerBookGrants = List.copyOf(playerBookGrants);
        if (message != null && message.isBlank()) {
            throw new IllegalArgumentException("message is blank");
        }
    }

    public static WorkstationActionResult pass() {
        return new WorkstationActionResult(false, List.of(), List.of(), List.of(), null);
    }

    public static WorkstationActionResult handled(
        List<WorkstationSlotDelta> slotDeltas,
        List<ItemGrant> itemGrants,
        List<WorkstationPlayerBookGrant> playerBookGrants,
        String message
    ) {
        return new WorkstationActionResult(true, slotDeltas, itemGrants, playerBookGrants, message);
    }
}
