import { LayoutPatternResult } from './GridLayoutGenerator';

export class PatternBlender {
    static blend(
        patterns: LayoutPatternResult[],
        weights: number[]
    ): LayoutPatternResult {
        if (patterns.length === 0) {
            throw new Error('No patterns to blend');
        }
        if (patterns.length !== weights.length) {
            throw new Error('Patterns and weights must have the same length');
        }
        // Normalize weights
        const totalWeight = weights.reduce((a, b) => a + b, 0);
        const normWeights = weights.map(w => w / totalWeight);
        // Assume all grids are the same size
        const size = patterns[0].grid.length;
        const grid: number[][] = Array.from({ length: size }, () => Array(size).fill(0));
        // Weighted average for grid values
        for (let y = 0; y < size; y++) {
            for (let x = 0; x < size; x++) {
                let blended = 0;
                for (let i = 0; i < patterns.length; i++) {
                    blended += patterns[i].grid[y][x] * normWeights[i];
                }
                grid[y][x] = Math.round(blended);
            }
        }
        // Merge pathways (deduplicate by x/y/type)
        const allPaths = patterns.flatMap(p => p.pathways);
        const pathSet = new Set<string>();
        const pathways = allPaths.filter(p => {
            const key = `${p.x},${p.y},${p.type}`;
            if (pathSet.has(key)) return false;
            pathSet.add(key);
            return true;
        });
        return {
            grid,
            pathways,
            description: `Blended pattern of ${patterns.length} layouts`,
        };
    }
} 