package com.verbum_minecraft.api.content;

import java.util.List;
import java.util.Objects;

/**
 * Pure player-authored draft content captured by workstation UI.
 */
public record WorkstationBookDraft(
    String title,
    List<String> pages
) {
    public WorkstationBookDraft {
        if (title == null || title.isBlank()) {
            throw new IllegalArgumentException("title is blank");
        }
        Objects.requireNonNull(pages, "pages");
        pages = List.copyOf(pages);
    }
}
