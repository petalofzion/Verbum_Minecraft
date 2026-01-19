package com.verbum_minecraft.spi;

import com.verbum_minecraft.api.content.FeatureContext;

/**
 * The standard entrypoint for Verbum feature modules.
 * Features are discovered via ServiceLoader in the assembly projects.
 */
public interface FeatureEntrypoint {
    /**
     * @return The unique ID of this feature.
     */
    String id();

    /**
     * Called during mod initialization to register content (blocks, items, etc.).
     * This is pure logic and should not touch Minecraft/Fabric classes.
     */
    void register(FeatureContext ctx);

    /**
     * Called after registration for logic initialization.
     */
    void init();
}