package com.verbum_minecraft.api.fluid;

/**
 * High-performance fluid storage interface.
 * Designed for sim-kernel hot paths: no boxing, no allocations.
 */
public interface Fluid {
    long getAmount();
    long getCapacity();

    /**
     * Attempts to insert fluid.
     * @param amount The amount to insert.
     * @param simulate If true, the insertion is only simulated.
     * @return The amount actually inserted.
     */
    long insert(long amount, boolean simulate);

    /**
     * Attempts to extract fluid.
     * @param amount The amount to extract.
     * @param simulate If true, the extraction is only simulated.
     * @return The amount actually extracted.
     */
    long extract(long amount, boolean simulate);
}