// RotationSnap.ts
// Utility for snapping rotation angles

export function snapRotation(angle: number, increment: number = 45): number {
    return Math.round(angle / increment) * increment;
} 