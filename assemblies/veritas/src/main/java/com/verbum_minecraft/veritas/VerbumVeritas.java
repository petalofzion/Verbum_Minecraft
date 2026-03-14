package com.verbum_minecraft.veritas;

import com.verbum_minecraft.spi.FeatureEntrypoint;
import java.util.ServiceLoader;
import net.fabricmc.api.ModInitializer;
import com.verbum_minecraft.veritas.config.FeatureConfig;
import com.verbum_minecraft.veritas.registry.AssemblyFeatureContext;
import com.verbum_minecraft.veritas.registry.MinecraftContentRegistrar;

public class VerbumVeritas implements ModInitializer {
    @Override
    public void onInitialize() {
        System.out.println("Verbum: Veritas Initializing...");
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
