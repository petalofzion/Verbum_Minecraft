package com.verbum_minecraft.features.library.bookenhancement;

import java.util.Objects;

public record BookId(String namespace, String path, String edition) {
    public static final String DEFAULT_EDITION = "1";

    public BookId {
        Objects.requireNonNull(namespace, "namespace");
        Objects.requireNonNull(path, "path");
        if (namespace.isBlank()) {
            throw new IllegalArgumentException("namespace is blank");
        }
        if (path.isBlank()) {
            throw new IllegalArgumentException("path is blank");
        }
        if (edition == null || edition.isBlank()) {
            edition = DEFAULT_EDITION;
        }
    }

    public static BookId of(String namespace, String path) {
        return new BookId(namespace, path, DEFAULT_EDITION);
    }

    public static BookId of(String namespace, String path, String edition) {
        return new BookId(namespace, path, edition);
    }

    public static BookId parse(String rawId) {
        Objects.requireNonNull(rawId, "rawId");
        int colon = rawId.indexOf(':');
        if (colon <= 0 || colon == rawId.length() - 1) {
            throw new IllegalArgumentException("Invalid book id: " + rawId);
        }
        String namespace = rawId.substring(0, colon);
        String remainder = rawId.substring(colon + 1);
        String path = remainder;
        String edition = DEFAULT_EDITION;
        int at = remainder.indexOf('@');
        if (at >= 0) {
            if (at == remainder.length() - 1) {
                throw new IllegalArgumentException("Invalid book edition: " + rawId);
            }
            path = remainder.substring(0, at);
            edition = remainder.substring(at + 1);
        }
        return new BookId(namespace, path, edition);
    }

    public String compactId() {
        if (DEFAULT_EDITION.equals(edition)) {
            return namespace + ":" + path;
        }
        return namespace + ":" + path + "@" + edition;
    }

    public String resourcePath() {
        if (DEFAULT_EDITION.equals(edition)) {
            return "assets/" + namespace + "/books/" + path + ".txt";
        }
        return "assets/" + namespace + "/books/" + path + "@" + edition + ".txt";
    }
}
