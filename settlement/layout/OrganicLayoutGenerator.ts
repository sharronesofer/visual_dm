import { Settlement } from '../Settlement';
import { LayoutPatternResult, ILayoutPatternGenerator } from './GridLayoutGenerator';

export class OrganicLayoutGenerator implements ILayoutPatternGenerator {
    generate(settlement: Settlement): LayoutPatternResult {
        const size = Math.max(8, settlement.size * 6);
        const grid: number[][] = Array.from({ length: size }, () => Array(size).fill(0));
        // Seed a few organic centers
        const numCenters = Math.max(2, settlement.size);
        const centers: { x: number; y: number }[] = [];
        for (let i = 0; i < numCenters; i++) {
            centers.push({
                x: Math.floor(Math.random() * (size - 4)) + 2,
                y: Math.floor(Math.random() * (size - 4)) + 2,
            });
        }
        // Grow organic clusters from each center using random walk
        for (let i = 0; i < centers.length; i++) {
            let { x, y } = centers[i];
            for (let j = 0; j < size * 2; j++) {
                grid[y][x] = i + 1;
                // Random walk
                const dir = Math.floor(Math.random() * 4);
                if (dir === 0 && x > 0) x--;
                else if (dir === 1 && x < size - 1) x++;
                else if (dir === 2 && y > 0) y--;
                else if (dir === 3 && y < size - 1) y++;
            }
        }
        // Create winding organic paths between centers
        const pathways: { x: number; y: number; type: 'main' | 'side' }[] = [];
        for (let i = 0; i < centers.length - 1; i++) {
            let { x, y } = centers[i];
            const target = centers[i + 1];
            while (x !== target.x || y !== target.y) {
                pathways.push({ x, y, type: 'main' });
                // Biased random walk toward target
                if (Math.random() < 0.5) {
                    if (x < target.x) x++;
                    else if (x > target.x) x--;
                } else {
                    if (y < target.y) y++;
                    else if (y > target.y) y--;
                }
            }
            pathways.push({ x: target.x, y: target.y, type: 'main' });
        }
        return {
            grid,
            pathways,
            description: `Organic layout: ${numCenters} centers with winding paths`,
        };
    }
} 