// AssetReferenceManager.ts
// Tracks asset references by chunk/system and enforces a global memory budget.

interface AssetReference {
    count: number;
    estimatedBytes: number;
    lastAccess: number;
}

export class AssetReferenceManager {
    private references: Map<string, AssetReference> = new Map();
    private memoryBudget: number;
    private currentMemory: number = 0;

    constructor(memoryBudget: number = 256 * 1024 * 1024) { // Default: 256MB
        this.memoryBudget = memoryBudget;
    }

    /**
     * Add a reference to an asset. Increments count and updates memory usage.
     */
    addReference(assetId: string, estimatedBytes: number) {
        let ref = this.references.get(assetId);
        if (!ref) {
            ref = { count: 1, estimatedBytes, lastAccess: Date.now() };
            this.references.set(assetId, ref);
            this.currentMemory += estimatedBytes;
        } else {
            ref.count++;
            ref.lastAccess = Date.now();
        }
        this.enforceBudget();
    }

    /**
     * Remove a reference to an asset. Decrements count and unloads if zero.
     */
    removeReference(assetId: string) {
        const ref = this.references.get(assetId);
        if (!ref) return;
        ref.count--;
        ref.lastAccess = Date.now();
        if (ref.count <= 0) {
            this.currentMemory -= ref.estimatedBytes;
            this.references.delete(assetId);
            this.unloadAsset(assetId);
        }
    }

    /**
     * Get the current reference count for an asset.
     */
    getReferenceCount(assetId: string): number {
        return this.references.get(assetId)?.count || 0;
    }

    /**
     * Get the current memory usage (bytes).
     */
    getCurrentMemory(): number {
        return this.currentMemory;
    }

    /**
     * Set a new memory budget (bytes).
     */
    setMemoryBudget(bytes: number) {
        this.memoryBudget = bytes;
        this.enforceBudget();
    }

    /**
     * Enforce the memory budget by unloading least-recently-used assets.
     */
    private enforceBudget() {
        if (this.currentMemory <= this.memoryBudget) return;
        // Sort by lastAccess ascending (oldest first)
        const sorted = Array.from(this.references.entries()).sort((a, b) => a[1].lastAccess - b[1].lastAccess);
        for (const [assetId, ref] of sorted) {
            if (this.currentMemory <= this.memoryBudget) break;
            if (ref.count > 0) continue; // Only unload unreferenced assets
            this.currentMemory -= ref.estimatedBytes;
            this.references.delete(assetId);
            this.unloadAsset(assetId);
        }
    }

    /**
     * Unload the asset from memory (stub for integration with AssetManager).
     */
    private unloadAsset(assetId: string) {
        // Integrate with AssetManager or actual asset unloading logic here
        // Example: AssetManager.getInstance().unloadAsset(assetId);
    }

    /**
     * Get all tracked assets (for debugging/integration).
     */
    getAllReferences() {
        return Array.from(this.references.entries()).map(([id, ref]) => ({ id, ...ref }));
    }
} 