package com.verbum_minecraft.features.library.bookenhancement;

public final class BookNavigation {
    private BookNavigation() {
    }

    public static int resolvePageIndex(String input, int fallbackPageNumber, int pageCount) {
        if (pageCount <= 0) {
            return -1;
        }
        int pageNumber = parsePageNumber(input);
        if (pageNumber <= 0) {
            pageNumber = fallbackPageNumber;
        }
        if (pageNumber <= 0) {
            return -1;
        }
        if (pageNumber > pageCount) {
            pageNumber = pageCount;
        }
        return pageNumber - 1;
    }

    public static int toPageNumber(int pageIndex) {
        return pageIndex + 1;
    }

    public static int parsePageNumber(String input) {
        if (input == null) {
            return -1;
        }
        String trimmed = input.trim();
        if (trimmed.isEmpty()) {
            return -1;
        }
        int value = 0;
        for (int i = 0; i < trimmed.length(); i++) {
            char c = trimmed.charAt(i);
            if (!Character.isDigit(c)) {
                return -1;
            }
            value = value * 10 + (c - '0');
            if (value < 0) {
                return -1;
            }
        }
        return value;
    }
}
