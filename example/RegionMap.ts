import { HexCell, TerrainType, WeatherType } from './HexCell';

export enum RegionType {
    WILDERNESS = 'wilderness',
    KINGDOM = 'kingdom',
    EMPIRE = 'empire',
    WASTELAND = 'wasteland',
    FRONTIER = 'frontier'
}

export interface RegionData {
    name: string;
    type: RegionType;
    cells: HexCell[];
    discoveredPercentage: number;
    dangerlevel: number;
    factionInfluence?: Record<string, number>;
}

export interface Point {
    x: number;
    y: number;
}

export interface POI {
    name: string;
    description: string;
    position: {
        q: number;
        r: number;
    };
    type: string;
    discovered: boolean;
}

export class RegionMap {
    private _name: string;
    private _type: RegionType;
    private _width: number;
    private _height: number;
    private _cells: Map<string, HexCell>;
    private _pois: POI[];
    private _neighborRegions: Record<string, string>;

    constructor(name: string, type: RegionType = RegionType.WILDERNESS, width: number = 20, height: number = 20) {
        this._name = name;
        this._type = type;
        this._width = width;
        this._height = height;
        this._cells = new Map<string, HexCell>();
        this._pois = [];
        this._neighborRegions = {};

        this.initializeEmptyCells();
    }

    private initializeEmptyCells(): void {
        // Create a basic grid of plain cells
        for (let q = 0; q < this._width; q++) {
            for (let r = 0; r < this._height; r++) {
                const cell = new HexCell(q, r);
                this.setCell(cell);
            }
        }
    }

    private getCellKey(q: number, r: number): string {
        return `${q},${r}`;
    }

    public get name(): string {
        return this._name;
    }

    public set name(value: string) {
        this._name = value;
    }

    public get type(): RegionType {
        return this._type;
    }

    public setCell(cell: HexCell): void {
        const key = this.getCellKey(cell.q, cell.r);
        this._cells.set(key, cell);
    }

    public getCell(q: number, r: number): HexCell | undefined {
        const key = this.getCellKey(q, r);
        return this._cells.get(key);
    }

    public getCells(): HexCell[] {
        return Array.from(this._cells.values());
    }

    public addPOI(poi: POI): void {
        this._pois.push(poi);
    }

    public getPOIs(): POI[] {
        return this._pois;
    }

    public discoverPOI(q: number, r: number, radius: number = 1): number {
        let discovered = 0;

        this._pois.forEach(poi => {
            if (!poi.discovered) {
                const distance = this.calculateDistance(poi.position.q, poi.position.r, q, r);
                if (distance <= radius) {
                    poi.discovered = true;
                    discovered++;
                }
            }
        });

        return discovered;
    }

    public calculateDistance(q1: number, r1: number, q2: number, r2: number): number {
        return (Math.abs(q1 - q2) + Math.abs(r1 - r2) + Math.abs(q1 + r1 - q2 - r2)) / 2;
    }

    public generateRandomTerrain(
        plainsProbability: number = 0.5,
        forestProbability: number = 0.2,
        mountainProbability: number = 0.1,
        waterProbability: number = 0.1
    ): void {
        this._cells.forEach(cell => {
            const rand = Math.random();

            if (rand < plainsProbability) {
                cell.terrain = 'plains';
            } else if (rand < plainsProbability + forestProbability) {
                cell.terrain = 'forest';
            } else if (rand < plainsProbability + forestProbability + mountainProbability) {
                cell.terrain = 'mountain';
            } else if (rand < plainsProbability + forestProbability + mountainProbability + waterProbability) {
                cell.terrain = 'water';
            } else {
                cell.terrain = 'desert';
            }

            // Set random elevation
            cell.elevation = Math.random();

            // Set random moisture
            cell.moisture = Math.random();

            // Set random temperature
            cell.temperature = Math.random();
        });
    }

    public addNeighborRegion(direction: string, regionName: string): void {
        this._neighborRegions[direction] = regionName;
    }

    public getNeighborRegion(direction: string): string | undefined {
        return this._neighborRegions[direction];
    }

    public toJSON(): RegionData {
        const cells = this.getCells();
        const discoveredCells = cells.filter(cell => cell.isDiscovered);
        const discoveredPercentage = (discoveredCells.length / cells.length) * 100;

        return {
            name: this._name,
            type: this._type,
            cells: cells,
            discoveredPercentage: discoveredPercentage,
            dangerlevel: this.calculateDangerLevel()
        };
    }

    private calculateDangerLevel(): number {
        // Calculate danger level based on terrain types and other factors
        let dangerScore = 0;

        this._cells.forEach(cell => {
            switch (cell.terrain) {
                case 'mountain':
                    dangerScore += 2;
                    break;
                case 'forest':
                    dangerScore += 1;
                    break;
                case 'water':
                    dangerScore += 1.5;
                    break;
                case 'desert':
                    dangerScore += 1.8;
                    break;
                default:
                    dangerScore += 0.5;
            }

            if (cell.hasFeature) {
                dangerScore += 1;
            }
        });

        // Normalize to a 1-10 scale
        return Math.min(10, Math.max(1, dangerScore / (this._cells.size / 10)));
    }

    // Static factory method
    public static createRandomWilderness(name: string, width: number = 20, height: number = 20): RegionMap {
        const region = new RegionMap(name, RegionType.WILDERNESS, width, height);
        region.generateRandomTerrain();

        // Add some random POIs
        const poiCount = Math.floor(Math.random() * 5) + 3;
        for (let i = 0; i < poiCount; i++) {
            const q = Math.floor(Math.random() * width);
            const r = Math.floor(Math.random() * height);
            region.addPOI({
                name: `POI ${i + 1}`,
                description: `A point of interest in the wilderness.`,
                position: { q, r },
                type: ['settlement', 'ruin', 'landmark', 'dungeon'][Math.floor(Math.random() * 4)],
                discovered: false
            });
        }

        return region;
    }
} 