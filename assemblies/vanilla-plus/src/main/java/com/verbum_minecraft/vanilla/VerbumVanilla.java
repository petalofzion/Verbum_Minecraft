package com.verbum_minecraft.vanilla;

import net.fabricmc.api.ModInitializer;
import com.verbum_minecraft.spi.FeatureEntrypoint;
import com.verbum_minecraft.vanilla.config.FeatureConfig;
import com.verbum_minecraft.vanilla.registry.AssemblyFeatureContext;
import com.verbum_minecraft.vanilla.registry.MinecraftContentRegistrar;
import java.util.ServiceLoader;

public class VerbumVanilla implements ModInitializer {
    @Override
    public void onInitialize() {
        System.out.println("Verbum: Vanilla Initializing...");
        FeatureConfig.load();

        MinecraftContentRegistrar registrar = new MinecraftContentRegistrar();
        AssemblyFeatureContext context = new AssemblyFeatureContext(registrar);
        
        ServiceLoader<FeatureEntrypoint> loader = ServiceLoader.load(FeatureEntrypoint.class);
        for (FeatureEntrypoint feature : loader) {
            if (FeatureConfig.isEnabled(feature.id())) {
                System.out.println("Loading feature: " + feature.id());
                feature.register(context);
                feature.init();
            } else {
                System.out.println("Feature disabled: " + feature.id());
            }
        }
    }
}
