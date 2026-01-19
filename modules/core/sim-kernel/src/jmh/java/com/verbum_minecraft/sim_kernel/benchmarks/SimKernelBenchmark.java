package com.verbum_minecraft.sim_kernel.benchmarks;

import org.openjdk.jmh.annotations.*;
import java.util.concurrent.TimeUnit;

@State(Scope.Benchmark)
@BenchmarkMode(Mode.Throughput)
@OutputTimeUnit(TimeUnit.SECONDS)
public class SimKernelBenchmark {

    private long[] data;

    @Setup
    public void setup() {
        data = new long[1024];
        for (int i = 0; i < data.length; i++) {
            data[i] = i;
        }
    }

    @Benchmark
    public long measureBaselineSum() {
        long sum = 0;
        for (long value : data) {
            sum += value;
        }
        return sum;
    }
}
