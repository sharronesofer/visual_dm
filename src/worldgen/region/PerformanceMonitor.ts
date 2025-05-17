// PerformanceMonitor.ts
// Instruments and logs performance metrics for building generation

export interface ChunkPerformanceMetrics {
    chunkKey: string;
    generationTimeMs: number;
    memoryUsageBytes: number;
    buildingsGenerated: number;
    timestamp: number;
}

export class PerformanceMonitor {
    private chunkMetrics: ChunkPerformanceMetrics[] = [];
    private globalStart: number = 0;
    private globalEnd: number = 0;

    /**
     * Start global timing
     */
    startGlobal() {
        this.globalStart = performance.now();
    }

    /**
     * End global timing
     */
    endGlobal() {
        this.globalEnd = performance.now();
    }

    /**
     * Log per-chunk metrics
     */
    logChunkMetrics(metrics: ChunkPerformanceMetrics) {
        this.chunkMetrics.push(metrics);
    }

    /**
     * Get all chunk metrics
     */
    getChunkMetrics(): ChunkPerformanceMetrics[] {
        return this.chunkMetrics;
    }

    /**
     * Get global generation time
     */
    getGlobalGenerationTime(): number {
        return this.globalEnd - this.globalStart;
    }

    /**
     * Print summary to console
     */
    printSummary() {
        console.log('--- Performance Summary ---');
        console.log('Global generation time (ms):', this.getGlobalGenerationTime());
        const avgChunkTime = this.chunkMetrics.length
            ? this.chunkMetrics.reduce((a, b) => a + b.generationTimeMs, 0) / this.chunkMetrics.length
            : 0;
        console.log('Average chunk generation time (ms):', avgChunkTime);
        const totalBuildings = this.chunkMetrics.reduce((a, b) => a + b.buildingsGenerated, 0);
        console.log('Total buildings generated:', totalBuildings);
        // Add more as needed
    }

    /**
     * Hook for visualization tools (can be extended)
     */
    onMetricsUpdate(callback: (metrics: ChunkPerformanceMetrics[]) => void) {
        // Call callback whenever metrics are updated (not implemented here)
    }
} 