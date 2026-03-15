package com.verbum_minecraft.votum.client;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.reflect.TypeToken;
import com.verbum_minecraft.features.library.bookenhancement.BookBookmarkStore;
import com.verbum_minecraft.features.library.bookenhancement.BookId;
import java.io.IOException;
import java.io.Reader;
import java.io.Writer;
import java.lang.reflect.Type;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;
import net.fabricmc.api.EnvType;
import net.fabricmc.api.Environment;
import net.fabricmc.loader.api.FabricLoader;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Environment(EnvType.CLIENT)
final class LibraryBookBookmarks implements BookBookmarkStore {
    private static final Logger LOGGER = LoggerFactory.getLogger(LibraryBookBookmarks.class);
    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();
    private static final Type MAP_TYPE = new TypeToken<Map<String, Integer>>() { }.getType();
    private static final Object LOCK = new Object();

    private static final LibraryBookBookmarks INSTANCE = new LibraryBookBookmarks();
    private static Map<String, Integer> bookmarks = new HashMap<>();
    private static boolean loaded;

    private LibraryBookBookmarks() {
    }

    static BookBookmarkStore store() {
        return INSTANCE;
    }

    @Override
    public int get(BookId bookId) {
        ensureLoaded();
        return bookmarks.getOrDefault(bookId.compactId(), -1);
    }

    @Override
    public void set(BookId bookId, int page) {
        ensureLoaded();
        String key = bookId.compactId();
        if (page <= 0) {
            bookmarks.remove(key);
        } else {
            bookmarks.put(key, page);
        }
        save();
    }

    private static void ensureLoaded() {
        synchronized (LOCK) {
            if (loaded) {
                return;
            }
            loaded = true;
            Path path = bookmarksPath();
            if (!Files.exists(path)) {
                return;
            }
            try (Reader reader = Files.newBufferedReader(path, StandardCharsets.UTF_8)) {
                Map<String, Integer> data = GSON.fromJson(reader, MAP_TYPE);
                if (data != null) {
                    bookmarks = new HashMap<>(data);
                }
            } catch (IOException e) {
                LOGGER.warn("Failed to load bookmarks from {}", path, e);
            }
        }
    }

    private static void save() {
        Path path = bookmarksPath();
        try {
            Files.createDirectories(path.getParent());
            try (Writer writer = Files.newBufferedWriter(path, StandardCharsets.UTF_8)) {
                GSON.toJson(bookmarks, writer);
            }
        } catch (IOException e) {
            LOGGER.warn("Failed to save bookmarks to {}", path, e);
        }
    }

    private static Path bookmarksPath() {
        return FabricLoader.getInstance().getConfigDir().resolve("verbum-bookmarks.json");
    }
}
