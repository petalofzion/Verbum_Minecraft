package com.verbum_minecraft.api.content;

import java.util.List;

/**
 * Pure source-book snapshot for workstation copy workflows.
 */
public record WorkstationBookSnapshot(
    String title,
    String author,
    List<String> pages,
    String sourceBookId
) {
    public WorkstationBookSnapshot {
        if (title == null || title.isBlank()) {
            throw new IllegalArgumentException("title is blank");
        }
        if (author == null || author.isBlank()) {
            throw new IllegalArgumentException("author is blank");
        }
        if (pages == null) {
            throw new IllegalArgumentException("pages is null");
        }
        pages = List.copyOf(pages);
        if (sourceBookId != null && sourceBookId.isBlank()) {
            throw new IllegalArgumentException("sourceBookId is blank");
        }
    }
}
