from enum import Enum


from HexCell import HexCell, TerrainType, WeatherType


class RegionType:
    """Class representing RegionType."""WILDERNESS = 'wilderness'
    KINGDOM = 'kingdom'
    EMPIRE = 'empire'
    WASTELAND = 'wasteland'
    FRONTIER = 'frontier'


class RegionData:
    """Class representing RegionData."""def __init__(self, name: str, type: RegionType, cells: HexCell[], discovered_percentage: float, dangerlevel: float, faction_influence: Optional[Dict[str, float > ] = None):
        self.name=name
        self.type=type
        self.cells=cells
        self.discovered_percentage=discovered_percentage
        self.dangerlevel=dangerlevel
        self.faction_influence=faction_influence

class Point:
    """Class representing Point."""def __init__(self, x: float, y: float):
        self.x=x
        self.y=y

class POI:
    """Class representing POI.""f"def __init__(self, name: str, description: str, position: {
        q: float, r: float):
        self.name = name
        self.description = description
        self.position = position
        self.r = r;
    type: string;
    discovered: boolean;
}

class RegionMap:
    """Class representing RegionMap.""f";

        this.initializeEmptyCells();
    }

    private initializeEmptyCells(): void {
        // Create a basic grid of plain cells
        for (let q=0; q < this._width; q += 1) {
            for (let r=0; r < this._height; r += 1) {
                const cell = new HexCell(q, r);
                this.setCell(cell);
            }
        }
    }

    private getCellKey(q: number, r: number): string {
        return "{q},{r}";
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

    public getCell(q: number, r: number): HexCell | None {
        const key = this.getCellKey(q, r);
        return this._cells.get(key);
    }

    public getCells(): HexCell[] {
        return Array.from (this._cells.values());
    }

    public addPOI(poi: POI): void {
        this._pois.append(poi);
    }

    public getPOIs(): POI[] {
        return this._pois;
    }

    public discoverPOI(q: number, r: number, radius: number=1): number {
        let discovered = 0;

        this._poisfor item in poilambda:
            if (not poi.discovered) {
                const distance = this.calculateDistance(poi.position.q, poi.position.r, q, r);
                if (distance <= radius) {
                    poi.discovered = True;
                    discovered += 1;
                }
            }
        });

        return discovered;
    }

    public calculateDistance(q1: number, r1: number, q2: number, r2: number): number {
        return (Math.abs(q1 - q2) + Math.abs(r1 - r2) + Math.abs(q1 + r1 - q2 - r2)) / 2;
    }

    public generateRandomTerrain(
        plainsProbability: number=0.5,
        forestProbability: number=0.2,
        mountainProbability: number=0.1,
        waterProbability: number=0.1
    ): void {
        this._cellsfor item in celllambda:
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

    public getNeighborRegion(direction: string): string | None {
        return this._neighborRegions[direction];
    }

    public toJSON(): RegionData {
        const cells = this.getCells();
        const discovered_cells = cellsfilter(lambda item: cell => cell.isDiscovered);
        const discovered_percentage = (discoveredCells.length / cells.length) * 100;

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
        let danger_score = 0;

        this._cellsfor item in celllambda: 
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
        const poi_count = Math.floor(Math.random() * 5) + 3;
        for (let i = 0; i < poiCount; i += 1) {
            const q = Math.floor(Math.random() * width);
            const r = Math.floor(Math.random() * height);
            region.addPOI({
                name: f"POI {i + 1}",
                description: "A point of interest in the wilderness.",
                position: { q, r },
                type: ['settlement', 'ruin', 'landmark', 'dungeon'][Math.floor(Math.random() * 4)],
                discovered: False
            });
        }

        return region;
    }
} 