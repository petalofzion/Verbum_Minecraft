package com.verbum_minecraft.features.library.librariansdesk;

import com.verbum_minecraft.spi.BlockWorkstationBehaviorProvider;

public final class LibrariansDeskWorkstationBehaviorProvider implements BlockWorkstationBehaviorProvider {
    public static final String BEHAVIOR_ID = "verbum:librarians_desk";

    @Override
    public String behaviorId() {
        return BEHAVIOR_ID;
    }

    @Override
    public LibrariansDeskWorkstationHandler createHandler() {
        return new LibrariansDeskWorkstationHandler();
    }
}
