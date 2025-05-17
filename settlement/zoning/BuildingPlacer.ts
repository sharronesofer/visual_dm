import { ZoningSystem, ZoneType, ZoneCell } from './ZoningSystem';
import { Settlement, SettlementType } from '../Settlement';
import { RoadNetwork } from '../layout/RoadNetwork';

export interface PlacedBuilding {
    x: number;
    y: number;
    type: string;
    zone: ZoneType;
    orientation: number; // angle in degrees
    isLandmark?: boolean;
}

export class BuildingPlacer {
    placed: PlacedBuilding[] = [];

    placeBuildings(
        zoning: ZoningSystem,
        settlement: Settlement,
        roadNetwork: RoadNetwork,
        buildingTypes: { type: string; zone: ZoneType; isLandmark?: boolean }[]
    ) {
        // Place landmarks first in special/commercial zones near center/main roads
        for (const b of buildingTypes.filter(b => b.isLandmark)) {
            const candidates: ZoneCell[] = [];
            for (const row of zoning.grid) {
                for (const cell of row) {
                    if ((cell.zone === ZoneType.SPECIAL || cell.zone === ZoneType.COMMERCIAL) && cell.density > 0.8) {
                        candidates.push(cell);
                    }
                }
            }
            if (candidates.length > 0) {
                const chosen = candidates[Math.floor(Math.random() * candidates.length)];
                this.placed.push({ x: chosen.x, y: chosen.y, type: b.type, zone: chosen.zone, orientation: this.alignToRoad(chosen, roadNetwork), isLandmark: true });
            }
        }
        // Place other buildings by zone and density
        for (const b of buildingTypes.filter(b => !b.isLandmark)) {
            const candidates: ZoneCell[] = [];
            for (const row of zoning.grid) {
                for (const cell of row) {
                    if (cell.zone === b.zone && !this.placed.some(pb => pb.x === cell.x && pb.y === cell.y)) {
                        candidates.push(cell);
                    }
                }
            }
            // Sort by density (higher first)
            candidates.sort((a, b) => b.density - a.density);
            if (candidates.length > 0) {
                const chosen = candidates[0];
                this.placed.push({ x: chosen.x, y: chosen.y, type: b.type, zone: chosen.zone, orientation: this.alignToRoad(chosen, roadNetwork) });
            }
        }
    }

    alignToRoad(cell: ZoneCell, roadNetwork: RoadNetwork): number {
        // Find nearest road and align building to face it (simple: 0, 90, 180, 270)
        const directions = [
            { dx: 0, dy: -1, angle: 0 },
            { dx: 1, dy: 0, angle: 90 },
            { dx: 0, dy: 1, angle: 180 },
            { dx: -1, dy: 0, angle: 270 },
        ];
        for (const dir of directions) {
            const nx = cell.x + dir.dx;
            const ny = cell.y + dir.dy;
            if (roadNetwork.nodes.has(`${nx},${ny}`)) {
                return dir.angle;
            }
        }
        return 0; // Default orientation
    }

    // For extensibility: validate placement
    validatePlacement(cell: ZoneCell, settlement: Settlement): boolean {
        // Example: check terrain, accessibility, etc. (stub)
        return true;
    }
} 