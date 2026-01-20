package com.verbum_minecraft.features.library.bookenhancement;

@FunctionalInterface
public interface BookLineBreaker {
    String fit(String text, int maxWidth);
}
