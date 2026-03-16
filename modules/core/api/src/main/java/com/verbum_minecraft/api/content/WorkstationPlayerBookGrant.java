package com.verbum_minecraft.api.content;

import java.util.List;

/**
 * Pure player-owned written book output for workstation copy/write workflows.
 */
public record WorkstationPlayerBookGrant(
    String title,
    List<String> pages
) {
    public WorkstationPlayerBookGrant {
        if (title == null || title.isBlank()) {
            throw new IllegalArgumentException("title is blank");
        }
        if (pages == null) {
            throw new IllegalArgumentException("pages is null");
        }
        pages = List.copyOf(pages);
    }
}
