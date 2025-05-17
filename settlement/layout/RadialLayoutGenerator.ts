import { Settlement } from '../Settlement';
import { LayoutPatternResult, ILayoutPatternGenerator } from './GridLayoutGenerator';

export class RadialLayoutGenerator implements ILayoutPatternGenerator {
    generate(settlement: Settlement): LayoutPatternResult {
        const size = Math.max(8, settlement.size * 6);
        const grid: number[][] = Array.from({ length: size }, () => Array(size).fill(0));
        const center = { x: Math.floor(size / 2), y: Math.floor(size / 2) };
        const numRings = Math.max(2, settlement.size + 1);
        const numRays = Math.max(4, settlement.size * 2);
        // Draw concentric rings
        for (let r = 1; r <= numRings; r++) {
            const radius = (r * size) / (2 * (numRings + 1));
            for (let theta = 0; theta < 2 * Math.PI; theta += Math.PI / (size * 2)) {
                const x = Math.round(center.x + radius * Math.cos(theta));
                const y = Math.round(center.y + radius * Math.sin(theta));
                if (x >= 0 && x < size && y >= 0 && y < size) {
                    grid[y][x] = r; // Ring id
                }
            }
        }
        // Draw radiating pathways
        const pathways: { x: number; y: number; type: 'main' | 'side' }[] = [];
        for (let i = 0; i < numRays; i++) {
            const angle = (2 * Math.PI * i) / numRays;
            for (let r = 1; r < size / 2; r++) {
                const x = Math.round(center.x + r * Math.cos(angle));
                const y = Math.round(center.y + r * Math.sin(angle));
                if (x >= 0 && x < size && y >= 0 && y < size) {
                    pathways.push({ x, y, type: 'main' });
                }
            }
        }
        return {
            grid,
            pathways,
            description: `Radial layout: ${numRings} rings and ${numRays} rays`,
        };
    }
} 