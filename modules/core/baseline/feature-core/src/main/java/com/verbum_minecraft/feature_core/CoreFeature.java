package com.verbum_minecraft.feature_core;

import com.verbum_minecraft.api.content.FeatureContext;
import com.verbum_minecraft.spi.FeatureEntrypoint;

public class CoreFeature implements FeatureEntrypoint {
    @Override
    public String id() {
        return "core-feature";
    }

    @Override
    public void register(FeatureContext ctx) {
        System.out.println("Core Feature: Registering content...");
    }

    @Override
    public void init() {
        System.out.println("Core Feature: Initializing logic...");
    }
}