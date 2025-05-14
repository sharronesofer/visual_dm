from typing import Dict, List, Optional, Any, Union

    Region,
    RegionCell,
    RegionGeneratorOptions,
    TerrainType,
    POI,
    Resource
} from './RegionGeneratorInterfaces';
/**
 * Implementation of a procedural region generator
 */
class ProceduralRegionGenerator extends BaseRegionGenerator {
    /**
     * Create a new procedural region generator
     */
    constructor() {
        super(GeneratorType.PROCEDURAL);
    }
    /**
     * Generate a region procedurally
     * @param options The generation options
     * @param random The random number generator
     * @returns The generated region
     */
    protected generateRegion(options: RegionGeneratorOptions, random: IRandomGenerator): Region {
        const width = options.width;
        const height = options.height;
        const terrainRng = random.createChild('terrain');
        const poiRng = random.createChild('poi');
        const resourceRng = random.createChild('resource');
        const cells = this.generateTerrainCells(width, height, options, terrainRng);
        const pointsOfInterest = this.generatePOIs(cells, options, poiRng);
        const resources = this.generateResources(cells, pointsOfInterest, options, resourceRng);
        return {
            id: this.generateRegionId(options, random),
            name: this.generateRegionName(options, random),
            description: `A procedurally generated region of size ${width}x${height}.`,
            width,
            height,
            cells,
            pointsOfInterest,
            resources,
            metadata: {
                seed: random.getSeedConfig().seed,
                generatorType: this.generatorType,
                parameters: {
                    width,
                    height,
                    terrain: options.terrain || {},
                    pointsOfInterest: options.pointsOfInterest || {},
                    resources: options.resources || {}
                }
            }
        };
    }
    /**
     * Generate terrain cells for the region
     * @param width Region width
     * @param height Region height
     * @param options Generation options
     * @param random Random number generator
     * @returns Array of cells
     */
    private generateTerrainCells(
        width: number,
        height: number,
        options: RegionGeneratorOptions,
        random: IRandomGenerator
    ): RegionCell[] {
        const cells: RegionCell[] = [];
        const terrainOptions = options.terrain || {};
        const waterThreshold = terrainOptions.waterThreshold || 0.05;
        const mountainThreshold = terrainOptions.mountainThreshold || 0.7;
        const forestThreshold = terrainOptions.forestThreshold || 0.4;
        const desertThreshold = terrainOptions.desertThreshold || 0.1;
        const urbanChance = terrainOptions.urbanChance || 0.1;
        const found = {
            water: false,
            mountain: false,
            forest: false,
            desert: false,
            urban: false,
            plains: false
        };
        const elevationRng = random.createChild('elevation');
        const moistureRng = random.createChild('moisture');
        for (let y = 0; y < height; y++) {
            for (let x = 0; x < width; x++) {
                const elevationRngForCell = elevationRng.createChild(`x${x}y${y}`);
                const elevation = elevationRngForCell.random();
                const moistureRngForCell = moistureRng.createChild(`x${x}y${y}`);
                const moisture = moistureRngForCell.random();
                const noiseValue = (elevation * 0.6) + (moisture * 0.4);
                let terrain: TerrainType;
                if (noiseValue < waterThreshold) {
                    terrain = 'water';
                    found.water = true;
                } else if (noiseValue > mountainThreshold) {
                    terrain = 'mountain';
                    found.mountain = true;
                } else if (noiseValue > forestThreshold) {
                    terrain = 'forest';
                    found.forest = true;
                } else if (noiseValue < desertThreshold) {
                    terrain = 'desert';
                    found.desert = true;
                } else if (((x + y) % Math.floor(1 / urbanChance) === 0)) {
                    terrain = 'urban';
                    found.urban = true;
                } else {
                    terrain = 'plains';
                    found.plains = true;
                }
                cells.push({
                    x,
                    y,
                    terrain,
                    elevation,
                    moisture
                });
            }
        }
        this.ensureAllTerrainTypes(cells, found, random);
        return cells;
    }
    /**
     * Ensure that at least one of each terrain type exists
     * @param cells Array of cells
     * @param found Record of which terrain types we've found
     * @param random Random number generator
     */
    private ensureAllTerrainTypes(
        cells: RegionCell[],
        found: Record<TerrainType | string, boolean>,
        random: IRandomGenerator
    ): void {
        const terrainTypes: TerrainType[] = ['water', 'mountain', 'forest', 'desert', 'urban', 'plains'];
        const assignRng = random.createChild('terrain-assign');
        const candidateCells = cells.filter(cell =>
            cell.x > 1 && cell.y > 1 &&
            cell.x < cells[0].x - 1 && cell.y < cells[0].y - 1
        );
        for (const terrainType of terrainTypes) {
            if (!found[terrainType]) {
                const cellIndex = assignRng.randomInt(0, candidateCells.length - 1);
                const cell = candidateCells[cellIndex];
                const targetCell = cells.find(c => c.x === cell.x && c.y === cell.y);
                if (targetCell) {
                    targetCell.terrain = terrainType;
                }
                candidateCells.splice(cellIndex, 1);
            }
        }
    }
    /**
     * Generate points of interest
     * @param cells Array of cells
     * @param options Generation options
     * @param random Random number generator
     * @returns Array of points of interest
     */
    private generatePOIs(
        cells: RegionCell[],
        options: RegionGeneratorOptions,
        random: IRandomGenerator
    ): POI[] {
        const poiOptions = options.pointsOfInterest || {};
        const maxPOIs = poiOptions.maxPOIs || 10;
        const allowedTerrains = poiOptions.allowedTerrains || ['plains', 'forest', 'mountain', 'desert'];
        const pois: POI[] = [];
        let poiCount = 0;
        let attempt = 0;
        const maxAttempts = maxPOIs * 20;
        const poiTemplates = [
            { id: 'ruins', weight: 0.7, minDistance: 3 },
            { id: 'cave', weight: 0.5, minDistance: 4 },
            { id: 'settlement', weight: 0.3, minDistance: 5 },
            { id: 'shrine', weight: 0.8, minDistance: 2 },
            { id: 'dungeon', weight: 0.2, minDistance: 6 }
        ];
        const attemptRng = random.createChild('poi-attempts');
        const templateRng = random.createChild('poi-templates');
        const positionRng = random.createChild('poi-positions');
        while (poiCount < maxPOIs && attempt < maxAttempts) {
            attempt++;
            const currentAttemptRng = attemptRng.createChild(`attempt-${attempt}`);
            const templateWeights = poiTemplates.map(t => t.weight);
            const template = templateRng.randomWeightedElement(poiTemplates, templateWeights);
            const x = positionRng.randomInt(0, options.width - 1);
            const y = positionRng.randomInt(0, options.height - 1);
            const cell = cells.find(c => c.x === x && c.y === y);
            if (!cell || !allowedTerrains.includes(cell.terrain)) {
                continue;
            }
            let tooClose = false;
            for (const poi of pois) {
                const distance = Math.sqrt(Math.pow(poi.x - x, 2) + Math.pow(poi.y - y, 2));
                if (distance < template.minDistance) {
                    tooClose = true;
                    break;
                }
            }
            if (tooClose) {
                continue;
            }
            pois.push({
                id: `poi-${poiCount}`,
                templateId: template.id,
                x,
                y,
                discovered: false
            });
            poiCount++;
        }
        return pois;
    }
    /**
     * Generate resources
     * @param cells Array of cells
     * @param pois Array of points of interest
     * @param options Generation options
     * @param random Random number generator
     * @returns Array of resources
     */
    private generateResources(
        cells: RegionCell[],
        pois: POI[],
        options: RegionGeneratorOptions,
        random: IRandomGenerator
    ): Resource[] {
        const resourceOptions = options.resources || {};
        const maxResources = resourceOptions.maxResources || 30;
        const allowedTerrains = resourceOptions.allowedTerrains ||
            ['water', 'mountain', 'forest', 'desert', 'plains'];
        const resources: Resource[] = [];
        let resourceCount = 0;
        let attempt = 0;
        const maxAttempts = maxResources * 20;
        const resourceTemplates = [
            { id: 'wood', weight: 0.8, terrains: ['forest'] },
            { id: 'stone', weight: 0.7, terrains: ['mountain'] },
            { id: 'herbs', weight: 0.6, terrains: ['forest', 'plains'] },
            { id: 'ore', weight: 0.4, terrains: ['mountain'] },
            { id: 'fish', weight: 0.5, terrains: ['water'] },
            { id: 'gems', weight: 0.2, terrains: ['mountain', 'cave'] },
            { id: 'fruit', weight: 0.6, terrains: ['forest', 'plains'] }
        ];
        const attemptRng = random.createChild('resource-attempts');
        const templateRng = random.createChild('resource-templates');
        const positionRng = random.createChild('resource-positions');
        const amountRng = random.createChild('resource-amounts');
        while (resourceCount < maxResources && attempt < maxAttempts) {
            attempt++;
            const currentAttemptRng = attemptRng.createChild(`attempt-${attempt}`);
            const templateWeights = resourceTemplates.map(t => t.weight);
            const template = templateRng.randomWeightedElement(resourceTemplates, templateWeights);
            const x = positionRng.randomInt(0, options.width - 1);
            const y = positionRng.randomInt(0, options.height - 1);
            const cell = cells.find(c => c.x === x && c.y === y);
            if (!cell || !template.terrains.includes(cell.terrain)) {
                continue;
            }
            const amount = amountRng.random() * 0.5 + 0.5; 
            resources.push({
                id: `resource-${resourceCount}`,
                templateId: template.id,
                x,
                y,
                amount,
                harvested: false
            });
            resourceCount++;
        }
        return resources;
    }
} 