// DistanceIndicator.ts
import { Vector3 } from '../types';

// Calculate Euclidean distance between two points
export function getDistance(a: Vector3, b: Vector3): number {
    return Math.sqrt(
        Math.pow(a.x - b.x, 2) +
        Math.pow(a.y - b.y, 2) +
        Math.pow(a.z - b.z, 2)
    );
}

// Format distance for display (e.g., 2.35m)
export function formatDistance(distance: number, decimals: number = 2): string {
    return `${distance.toFixed(decimals)}m`;
} 