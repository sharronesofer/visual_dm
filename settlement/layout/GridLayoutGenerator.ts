import { Settlement } from '../Settlement';

export interface LayoutPatternResult {
    grid: number[][]; // 2D array representing district/block types
    pathways: { x: number; y: number; type: 'main' | 'side' }[]; // List of pathway coordinates
    description?: string;
}

export interface ILayoutPatternGenerator {
    generate(settlement: Settlement): LayoutPatternResult;
}

export class GridLayoutGenerator implements ILayoutPatternGenerator {
    generate(settlement: Settlement): LayoutPatternResult {
        // Grid size based on settlement size
        const size = Math.max(4, settlement.size * 5);
        const grid: number[][] = [];
        for (let y = 0; y < size; y++) {
            const row: number[] = [];
            for (let x = 0; x < size; x++) {
                row.push(0); // 0 = empty block, can be extended for district types
            }
            grid.push(row);
        }
        // Main roads every 3 blocks
        const pathways: { x: number; y: number; type: 'main' | 'side' }[] = [];
        for (let i = 0; i < size; i++) {
            if (i % 3 === 0) {
                for (let j = 0; j < size; j++) {
                    pathways.push({ x: i, y: j, type: 'main' });
                    pathways.push({ x: j, y: i, type: 'main' });
                }
            }
        }
        return {
            grid,
            pathways,
            description: `Grid layout: ${size}x${size} with main roads every 3 blocks`,
        };
    }
} 