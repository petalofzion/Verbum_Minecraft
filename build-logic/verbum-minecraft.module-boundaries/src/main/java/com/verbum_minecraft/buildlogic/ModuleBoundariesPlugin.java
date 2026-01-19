package com.verbum_minecraft.buildlogic;

import org.gradle.api.Plugin;
import org.gradle.api.Project;
import org.gradle.api.artifacts.ProjectDependency;
import org.gradle.api.GradleException;

/**
 * Enforces strict Tier-based dependency firewalls.
 * 
 * Rules:
 * 1. modules:core:* (Tier 0/1) cannot depend on features or assemblies.
 * 2. modules:features:* (Tier 2) can depend on core, but not assemblies or other features (unless declared).
 * 3. assemblies:* (Tier 3) can depend on anything.
 * 
 * This ensures that core logic remains pure and swarm agents stay in their folders.
 */
public class ModuleBoundariesPlugin implements Plugin<Project> {
    @Override
    public void apply(Project project) {
        project.getConfigurations().all(conf -> {
            conf.getDependencies().withType(ProjectDependency.class).all(dep -> {
                String targetPath = dep.getDependencyProject().getPath();
                String sourcePath = project.getPath();

                validateBoundary(sourcePath, targetPath);
            });
        });
    }

    private void validateBoundary(String source, String target) {
        // Rule 1: Core cannot reach up
        if (source.startsWith(":modules:core") && (target.startsWith(":modules:features") || target.startsWith(":assemblies"))) {
            throw new GradleException("Boundary Violation: Core module '" + source + "' cannot depend on higher-tier module '" + target + "'");
        }

        // Rule 2: Features cannot reach assemblies or across features (simpler version)
        if (source.startsWith(":modules:features") && target.startsWith(":assemblies")) {
            throw new GradleException("Boundary Violation: Feature module '" + source + "' cannot depend on assembly module '" + target + "'");
        }
        
        // Rule 3: No cross-feature imports (enforcing encapsulated swarm)
        if (source.startsWith(":modules:features") && target.startsWith(":modules:features")) {
            String sourceFeature = getFeatureName(source);
            String targetFeature = getFeatureName(target);
            if (!sourceFeature.equals(targetFeature)) {
                throw new GradleException("Boundary Violation: Feature '" + sourceFeature + "' cannot depend on sibling feature '" + targetFeature + "'. Use core:api instead.");
            }
        }
    }

    private String getFeatureName(String path) {
        String[] parts = path.split(":");
        return parts.length > 3 ? parts[3] : path;
    }
}