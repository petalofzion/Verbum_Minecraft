package com.verbum_minecraft.features.library.bookenhancement;

import java.io.IOException;

public interface BookContentSource {
    String load(String resourcePath, long maxBytes) throws IOException;
}
