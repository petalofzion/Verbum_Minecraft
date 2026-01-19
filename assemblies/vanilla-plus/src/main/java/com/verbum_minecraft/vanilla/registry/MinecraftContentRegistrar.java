package com.verbum_minecraft.vanilla.registry;

import com.verbum_minecraft.api.content.BookDef;
import com.verbum_minecraft.api.content.ContentSink;
import com.verbum_minecraft.api.content.ItemDef;
import com.verbum_minecraft.api.content.VerbumId;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.StringReader;
import java.io.UncheckedIOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.Registry;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.network.Filterable;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.WrittenBookItem;
import net.minecraft.world.item.component.WritableBookContent;
import net.minecraft.world.item.component.WrittenBookContent;

public class MinecraftContentRegistrar implements ContentSink {
    @Override
    public void acceptItem(ItemDef def) {
        Identifier id = toIdentifier(def.id());
        Item.Properties settings = buildItemProperties(def, id);

        Item item = new Item(settings);
        Registry.register(BuiltInRegistries.ITEM, id, item);
    }

    @Override
    public void acceptBook(BookDef def) {
        ItemDef itemDef = def.item();
        Identifier id = toIdentifier(itemDef.id());
        WrittenBookContent content = buildWrittenBookContent(def);

        Item.Properties settings = buildItemProperties(itemDef, id)
            .component(DataComponents.WRITTEN_BOOK_CONTENT, content);

        Item item = new WrittenBookItem(settings);
        Registry.register(BuiltInRegistries.ITEM, id, item);
    }

    private static Identifier toIdentifier(VerbumId id) {
        return Identifier.fromNamespaceAndPath(id.namespace(), id.path());
    }

    private static Item.Properties buildItemProperties(ItemDef def, Identifier id) {
        Item.Properties settings = new Item.Properties()
            .setId(ResourceKey.create(Registries.ITEM, id))
            .stacksTo(def.maxStackSize());

        if (def.fireproof()) {
            settings = settings.fireResistant();
        }

        Rarity rarity = switch (def.rarityOrdinal()) {
            case ItemDef.RARITY_UNCOMMON -> Rarity.UNCOMMON;
            case ItemDef.RARITY_RARE -> Rarity.RARE;
            case ItemDef.RARITY_EPIC -> Rarity.EPIC;
            default -> Rarity.COMMON;
        };
        settings = settings.rarity(rarity);

        // TODO: Map creativeTabKey to actual ItemGroups

        return settings;
    }

    private static WrittenBookContent buildWrittenBookContent(BookDef def) {
        List<String> pages = enforcePageLength(loadPages(def));
        List<Filterable<Component>> pageComponents = toComponents(pages);
        String title = truncate(def.title(), WrittenBookContent.TITLE_MAX_LENGTH);

        return new WrittenBookContent(
            Filterable.passThrough(title),
            def.author(),
            0,
            pageComponents,
            true
        );
    }

    private static List<String> loadPages(BookDef def) {
        String raw = readResource(def.resolvedContentResourcePath());
        List<String> pages = splitPages(raw);
        if (pages.isEmpty()) {
            pages.add("");
        }
        return pages;
    }

    private static String readResource(String path) {
        try (InputStream input = MinecraftContentRegistrar.class.getClassLoader().getResourceAsStream(path)) {
            if (input == null) {
                throw new IllegalArgumentException("Missing book content resource: " + path);
            }
            byte[] bytes = input.readAllBytes();
            return new String(bytes, StandardCharsets.UTF_8);
        } catch (IOException e) {
            throw new UncheckedIOException("Failed to read book content resource: " + path, e);
        }
    }

    // Split by explicit ---PAGE--- markers; if none, treat the whole file as one page.
    private static List<String> splitPages(String content) {
        String normalized = content.replace("\r\n", "\n").trim();
        List<String> pages = new ArrayList<>();
        if (normalized.isEmpty()) {
            return pages;
        }

        StringBuilder current = new StringBuilder();
        try (BufferedReader reader = new BufferedReader(new StringReader(normalized))) {
            String line;
            while ((line = reader.readLine()) != null) {
                if (BookDef.PAGE_SEPARATOR.equals(line)) {
                    addPage(pages, current);
                    current.setLength(0);
                    continue;
                }
                if (current.length() > 0) {
                    current.append('\n');
                }
                current.append(line);
            }
            addPage(pages, current);
        } catch (IOException e) {
            throw new UncheckedIOException("Failed to parse book content", e);
        }

        return pages;
    }

    private static void addPage(List<String> pages, StringBuilder current) {
        String page = current.toString().trim();
        if (!page.isEmpty()) {
            pages.add(page);
        }
    }

    private static List<String> enforcePageLength(List<String> rawPages) {
        int maxLength = WrittenBookContent.PAGE_LENGTH;
        List<String> pages = new ArrayList<>();

        for (String page : rawPages) {
            if (page.length() <= maxLength) {
                pages.add(page);
                continue;
            }

            int index = 0;
            while (index < page.length()) {
                int end = Math.min(index + maxLength, page.length());
                int split = end;
                if (end < page.length()) {
                    int lastSpace = page.lastIndexOf(' ', end);
                    if (lastSpace > index + 20) {
                        split = lastSpace;
                    }
                }
                pages.add(page.substring(index, split).trim());
                index = split;
            }
        }

        return pages;
    }

    private static List<Filterable<Component>> toComponents(List<String> pages) {
        int maxPages = WritableBookContent.MAX_PAGES;
        List<Filterable<Component>> components = new ArrayList<>();

        for (String page : pages) {
            if (components.size() >= maxPages) {
                break;
            }
            components.add(Filterable.passThrough(Component.literal(page)));
        }

        if (components.isEmpty()) {
            components.add(Filterable.passThrough(Component.literal("")));
        }

        return components;
    }

    private static String truncate(String value, int maxLength) {
        if (value.length() <= maxLength) {
            return value;
        }
        return value.substring(0, maxLength);
    }
}
