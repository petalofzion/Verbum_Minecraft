package com.verbum_minecraft.spi;

import com.verbum_minecraft.api.content.BlockWorkstationHandler;

/**
 * Service-loaded provider for capsule-owned workstation behavior.
 */
public interface BlockWorkstationBehaviorProvider {
    String behaviorId();

    BlockWorkstationHandler createHandler();
}
