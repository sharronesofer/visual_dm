import { Settlement } from '../Settlement';
import { LayoutPatternResult, ILayoutPatternGenerator } from './GridLayoutGenerator';

export class ClusteredLayoutGenerator implements ILayoutPatternGenerator {
    generate(settlement: Settlement): LayoutPatternResult {
        // Number of clusters based on settlement size
        const numClusters = Math.max(2, settlement.size + 1);
        const size = Math.max(8, settlement.size * 6);
        const grid: number[][] = Array.from({ length: size }, () => Array(size).fill(0));
        const clusterCenters: { x: number; y: number }[] = [];
        // Place cluster centers
        for (let i = 0; i < numClusters; i++) {
            const x = Math.floor(Math.random() * (size - 4)) + 2;
            const y = Math.floor(Math.random() * (size - 4)) + 2;
            clusterCenters.push({ x, y });
            // Fill a small area around the center for the cluster
            for (let dx = -1; dx <= 1; dx++) {
                for (let dy = -1; dy <= 1; dy++) {
                    const nx = x + dx;
                    const ny = y + dy;
                    if (nx >= 0 && nx < size && ny >= 0 && ny < size) {
                        grid[ny][nx] = i + 1; // Cluster id
                    }
                }
            }
        }
        // Connect clusters with organic paths
        const pathways: { x: number; y: number; type: 'main' | 'side' }[] = [];
        for (let i = 0; i < clusterCenters.length - 1; i++) {
            const a = clusterCenters[i];
            const b = clusterCenters[i + 1];
            // Simple organic path: random walk between a and b
            let x = a.x, y = a.y;
            while (x !== b.x || y !== b.y) {
                pathways.push({ x, y, type: 'main' });
                if (Math.abs(b.x - x) > Math.abs(b.y - y)) {
                    x += b.x > x ? 1 : -1;
                } else if (b.y !== y) {
                    y += b.y > y ? 1 : -1;
                }
            }
            pathways.push({ x: b.x, y: b.y, type: 'main' });
        }
        return {
            grid,
            pathways,
            description: `Clustered layout: ${numClusters} clusters with organic connections`,
        };
    }
} 