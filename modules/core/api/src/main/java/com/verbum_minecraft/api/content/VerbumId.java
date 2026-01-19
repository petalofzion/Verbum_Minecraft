package com.verbum_minecraft.api.content;

import java.util.Objects;

/**
 * Pure identifier for Verbum content.
 * Lightweight wrapper around a string (e.g., "verbum:bible").
 */
public record VerbumId(String namespace, String path) {
    public VerbumId {
        Objects.requireNonNull(namespace);
        Objects.requireNonNull(path);
    }

    public static VerbumId of(String namespace, String path) {
        return new VerbumId(namespace, path);
    }

    public static VerbumId parse(String id) {
        int colonIndex = id.indexOf(':');
        if (colonIndex == -1) {
            throw new IllegalArgumentException("Invalid VerbumId: " + id);
        }
        return new VerbumId(id.substring(0, colonIndex), id.substring(colonIndex + 1));
    }

    @Override
    public String toString() {
        return namespace + ":" + path;
    }
}