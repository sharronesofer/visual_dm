// AlignmentGuides.ts
import { Vector3 } from '../types';

export interface AlignmentGuide {
    type: 'edge' | 'center';
    axis: 'x' | 'y' | 'z';
    position: number;
}

export function getAlignmentGuides(
    pos: Vector3,
    existing: Vector3[],
    threshold: number = 0.1
): AlignmentGuide[] {
    const guides: AlignmentGuide[] = [];
    for (const other of existing) {
        // Edge alignment (x, y, z)
        if (Math.abs(pos.x - other.x) < threshold) {
            guides.push({ type: 'edge', axis: 'x', position: other.x });
        }
        if (Math.abs(pos.y - other.y) < threshold) {
            guides.push({ type: 'edge', axis: 'y', position: other.y });
        }
        if (Math.abs(pos.z - other.z) < threshold) {
            guides.push({ type: 'edge', axis: 'z', position: other.z });
        }
        // Center alignment (midpoint between pos and other)
        const centerX = (pos.x + other.x) / 2;
        if (Math.abs(pos.x - centerX) < threshold) {
            guides.push({ type: 'center', axis: 'x', position: centerX });
        }
        const centerY = (pos.y + other.y) / 2;
        if (Math.abs(pos.y - centerY) < threshold) {
            guides.push({ type: 'center', axis: 'y', position: centerY });
        }
        const centerZ = (pos.z + other.z) / 2;
        if (Math.abs(pos.z - centerZ) < threshold) {
            guides.push({ type: 'center', axis: 'z', position: centerZ });
        }
    }
    return guides;
} 