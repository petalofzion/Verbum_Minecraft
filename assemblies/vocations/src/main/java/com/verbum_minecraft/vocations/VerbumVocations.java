package com.verbum_minecraft.vocations;

import com.verbum_minecraft.spi.FeatureEntrypoint;
import java.util.ServiceLoader;
import net.fabricmc.api.ModInitializer;
import com.verbum_minecraft.vocations.config.FeatureConfig;
import com.verbum_minecraft.vocations.registry.AssemblyFeatureContext;
import com.verbum_minecraft.vocations.registry.MinecraftContentRegistrar;

public class VerbumVocations implements ModInitializer {
    @Override
    public void onInitialize() {
        System.out.println("Verbum: Vocations Initializing...");
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
