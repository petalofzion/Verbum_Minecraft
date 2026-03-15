package com.verbum_minecraft.spi;

import com.verbum_minecraft.api.content.BlockInteractionHandler;

/**
 * Service-loaded provider for capsule-owned block interaction behavior.
 */
public interface BlockInteractionBehaviorProvider {
    String behaviorId();

    BlockInteractionHandler createHandler();
}
