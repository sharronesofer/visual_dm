// GridSystem.ts
import { Vector3 } from '../types';

export class GridSystem {
    private gridSize: number;
    private snappingEnabled: boolean;

    constructor(gridSize: number = 1, snappingEnabled: boolean = true) {
        this.gridSize = gridSize;
        this.snappingEnabled = snappingEnabled;
    }

    setGridSize(size: number) {
        this.gridSize = size;
    }

    enableSnapping(enable: boolean) {
        this.snappingEnabled = enable;
    }

    getGridSize() {
        return this.gridSize;
    }

    isSnappingEnabled() {
        return this.snappingEnabled;
    }

    // Snap a position to the nearest grid point
    snapPosition(pos: Vector3): Vector3 {
        if (!this.snappingEnabled) return { ...pos };
        return {
            x: Math.round(pos.x / this.gridSize) * this.gridSize,
            y: Math.round(pos.y / this.gridSize) * this.gridSize,
            z: Math.round(pos.z / this.gridSize) * this.gridSize,
        };
    }

    // Check if two positions are aligned on the grid (within a threshold)
    isAligned(a: Vector3, b: Vector3, threshold: number = 0.01): boolean {
        return (
            Math.abs(a.x - b.x) < threshold &&
            Math.abs(a.y - b.y) < threshold &&
            Math.abs(a.z - b.z) < threshold
        );
    }
} 