package com.verbum_minecraft.vanilla.config;

import java.util.Collections;
import java.util.Set;

/**
 * Assembly-level feature toggles. Loaded once at startup.
 */
public final class FeatureConfig {
    private static final Set<String> DISABLED = Collections.emptySet();

    private FeatureConfig() {
    }

    public static void load() {
        // TODO: Load from config/verbum_features.json once config is defined.
    }

    public static boolean isEnabled(String featureId) {
        return !DISABLED.contains(featureId);
    }
}
