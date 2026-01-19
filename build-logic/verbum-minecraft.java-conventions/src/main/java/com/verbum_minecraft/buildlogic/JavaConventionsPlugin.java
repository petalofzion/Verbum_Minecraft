package com.verbum_minecraft.buildlogic;

import org.gradle.api.Plugin;
import org.gradle.api.Project;
import org.gradle.api.plugins.JavaPluginExtension;
import org.gradle.jvm.toolchain.JavaLanguageVersion;

public class JavaConventionsPlugin implements Plugin<Project> {
    @Override
    public void apply(Project project) {
        project.getPlugins().apply("java-library");
        
        JavaPluginExtension java = project.getExtensions().getByType(JavaPluginExtension.class);
        java.getToolchain().getLanguageVersion().set(JavaLanguageVersion.of(21));
        
        project.getRepositories().mavenCentral();
        project.getRepositories().maven(repo -> repo.setUrl("https://maven.fabricmc.net/"));
    }
}