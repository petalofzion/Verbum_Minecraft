package com.verbum_minecraft.votum;

import com.verbum_minecraft.spi.FeatureEntrypoint;
import java.util.ServiceLoader;
import net.fabricmc.api.ModInitializer;
import com.verbum_minecraft.votum.config.FeatureConfig;
import com.verbum_minecraft.votum.registry.AssemblyFeatureContext;
import com.verbum_minecraft.votum.registry.MinecraftContentRegistrar;

public class VerbumVotum implements ModInitializer {
    @Override
    public void onInitialize() {
        System.out.println("Verbum: Votum Initializing...");
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
