package com.verbum_minecraft.runtime.content;

import com.verbum_minecraft.api.content.BlockInteractionHandler;
import com.verbum_minecraft.api.content.BlockWorkstationHandler;
import com.verbum_minecraft.spi.BlockInteractionBehaviorProvider;
import com.verbum_minecraft.spi.BlockWorkstationBehaviorProvider;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.ServiceLoader;

/**
 * Resolves capsule-owned behavior ids through SPI rather than API-level class names.
 */
public final class ContentBehaviorResolver {
    private ContentBehaviorResolver() {
    }

    public static BlockInteractionHandler resolveInteraction(String behaviorId) {
        BlockInteractionBehaviorProvider provider = interactionProviders().get(behaviorId);
        if (provider == null) {
            throw new IllegalStateException("No block interaction behavior provider for id: " + behaviorId);
        }
        return provider.createHandler();
    }

    public static BlockWorkstationHandler resolveWorkstation(String behaviorId) {
        BlockWorkstationBehaviorProvider provider = workstationProviders().get(behaviorId);
        if (provider == null) {
            throw new IllegalStateException("No block workstation behavior provider for id: " + behaviorId);
        }
        return provider.createHandler();
    }

    private static Map<String, BlockInteractionBehaviorProvider> interactionProviders() {
        Map<String, BlockInteractionBehaviorProvider> providers = new LinkedHashMap<>();
        for (BlockInteractionBehaviorProvider provider : ServiceLoader.load(BlockInteractionBehaviorProvider.class)) {
            BlockInteractionBehaviorProvider previous = providers.put(provider.behaviorId(), provider);
            if (previous != null) {
                throw new IllegalStateException("Duplicate block interaction behavior id: " + provider.behaviorId());
            }
        }
        return providers;
    }

    private static Map<String, BlockWorkstationBehaviorProvider> workstationProviders() {
        Map<String, BlockWorkstationBehaviorProvider> providers = new LinkedHashMap<>();
        for (BlockWorkstationBehaviorProvider provider : ServiceLoader.load(BlockWorkstationBehaviorProvider.class)) {
            BlockWorkstationBehaviorProvider previous = providers.put(provider.behaviorId(), provider);
            if (previous != null) {
                throw new IllegalStateException("Duplicate block workstation behavior id: " + provider.behaviorId());
            }
        }
        return providers;
    }
}
