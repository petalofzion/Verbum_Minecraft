package com.verbum_minecraft.api.content;

/**
 * Pure capsule-owned handler for block workstation requests.
 */
public interface BlockWorkstationHandler {
    WorkstationUiSpec uiSpec();

    WorkstationActionResult apply(WorkstationActionRequest request);
}
