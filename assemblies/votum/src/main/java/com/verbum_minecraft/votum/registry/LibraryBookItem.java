package com.verbum_minecraft.votum.registry;

import com.verbum_minecraft.features.library.bookenhancement.BookId;
import java.lang.reflect.Method;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.WrittenBookItem;
import net.minecraft.world.level.Level;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

final class LibraryBookItem extends WrittenBookItem {
    private static final Logger LOGGER = LoggerFactory.getLogger(LibraryBookItem.class);
    private static final String CLIENT_HELPER = "com.verbum_minecraft.votum.client.LibraryBookClient";
    private static final String CLIENT_METHOD = "openBook";
    private static final Object CLIENT_LOCK = new Object();

    private static volatile Method clientOpenMethod;
    private static volatile boolean clientLookupFailed;

    private final BookId bookId;

    LibraryBookItem(Item.Properties settings, BookId bookId) {
        super(settings);
        this.bookId = bookId;
    }

    @Override
    public InteractionResult use(Level level, Player player, InteractionHand hand) {
        if (level.isClientSide()) {
            openClientBook();
        }
        return InteractionResult.SUCCESS;
    }

    private void openClientBook() {
        Method method = clientOpenMethod;
        if (method == null && !clientLookupFailed) {
            synchronized (CLIENT_LOCK) {
                method = clientOpenMethod;
                if (method == null && !clientLookupFailed) {
                    method = resolveClientMethod();
                    if (method == null) {
                        clientLookupFailed = true;
                        return;
                    }
                    clientOpenMethod = method;
                }
            }
        }

        if (method == null) {
            return;
        }

        try {
            method.invoke(null, bookId);
        } catch (ReflectiveOperationException e) {
            LOGGER.warn("Failed to open library book {}", bookId.compactId(), e);
        }
    }

    private static Method resolveClientMethod() {
        try {
            Class<?> helper = Class.forName(CLIENT_HELPER);
            return helper.getMethod(CLIENT_METHOD, BookId.class);
        } catch (ReflectiveOperationException e) {
            LOGGER.warn("Library book client helper not available", e);
            return null;
        }
    }
}
