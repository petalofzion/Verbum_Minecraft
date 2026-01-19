package com.verbum_minecraft.api.energy;

/**
 * High-performance energy storage interface.
 * Designed for sim-kernel hot paths: no boxing, no allocations.
 */
public interface Energy {
    long getStored();
    long getCapacity();

    /**
     * Attempts to insert energy.
     * @param amount The amount to insert.
     * @param simulate If true, the insertion is only simulated.
     * @return The amount actually inserted.
     */
    long insert(long amount, boolean simulate);

    /**
     * Attempts to extract energy.
     * @param amount The amount to extract.
     * @param simulate If true, the extraction is only simulated.
     * @return The amount actually extracted.
     */
    long extract(long amount, boolean simulate);
}