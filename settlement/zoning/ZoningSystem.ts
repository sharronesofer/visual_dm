import { LayoutPatternResult } from '../layout/GridLayoutGenerator';
import { RoadNetwork } from '../layout/RoadNetwork';

export enum ZoneType {
    RESIDENTIAL = 'RESIDENTIAL',
    COMMERCIAL = 'COMMERCIAL',
    INDUSTRIAL = 'INDUSTRIAL',
    SPECIAL = 'SPECIAL',
}

export interface ZoneCell {
    x: number;
    y: number;
    zone: ZoneType;
    density: number; // 0-1, for gradient
}

export class ZoningSystem {
    grid: ZoneCell[][];
    size: number;

    constructor(size: number) {
        this.size = size;
        this.grid = Array.from({ length: size }, (_, y) =>
            Array.from({ length: size }, (_, x) => ({ x, y, zone: ZoneType.RESIDENTIAL, density: 0 }))
        );
    }

    generateZones(pattern: LayoutPatternResult, roadNetwork: RoadNetwork) {
        // Example: Commercial near main roads, industrial at periphery, special at center, rest residential
        const center = Math.floor(this.size / 2);
        for (let y = 0; y < this.size; y++) {
            for (let x = 0; x < this.size; x++) {
                // Distance from center for density gradient
                const dist = Math.sqrt((x - center) ** 2 + (y - center) ** 2);
                const maxDist = Math.sqrt(2) * center;
                let zone = ZoneType.RESIDENTIAL;
                let density = 1 - dist / maxDist;
                // Commercial: near main roads
                if (roadNetwork.nodes.has(`${x},${y}`) && roadNetwork.edges.some(e => (e.from === `${x},${y}` || e.to === `${x},${y}`) && e.type === 'main')) {
                    zone = ZoneType.COMMERCIAL;
                    density = Math.max(density, 0.8);
                }
                // Industrial: far from center
                if (dist > this.size * 0.4) {
                    zone = ZoneType.INDUSTRIAL;
                    density = Math.min(density, 0.5);
                }
                // Special: very center
                if (dist < this.size * 0.15) {
                    zone = ZoneType.SPECIAL;
                    density = 1;
                }
                this.grid[y][x] = { x, y, zone, density };
            }
        }
    }

    // For debugging/visualization
    getZoneMap(): ZoneType[][] {
        return this.grid.map(row => row.map(cell => cell.zone));
    }
} 