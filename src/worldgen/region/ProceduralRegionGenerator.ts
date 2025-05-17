import { GeneratorType, IRandomGenerator } from '../core/IWorldGenerator';
import { BaseRegionGenerator } from './BaseRegionGenerator';
import {
    Region,
    RegionCell,
    RegionGeneratorOptions,
    TerrainType,
    POI,
    Resource,
    Building,
    BuildingPlacementRule,
    BuildingMaterialStyle,
    PlacementRule,
    PlacementRuleContext,
    PlacementRuleResult
} from './RegionGeneratorInterfaces';
import { DefaultPlacementRuleEngine } from './PlacementRuleEngine';
import { BuildingCustomizationAPIInstance } from './BuildingCustomizationAPI';
import { selectMaterialAndStyle } from './StyleMaterialSystem';

/**
 * Implementation of a procedural region generator
 */
export class ProceduralRegionGenerator extends BaseRegionGenerator {
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

        // Create child RNGs for different aspects of generation
        const terrainRng = random.createChild('terrain');
        const poiRng = random.createChild('poi');
        const resourceRng = random.createChild('resource');
        const buildingRng = random.createChild('building');

        // Generate cells with terrain
        const cells = this.generateTerrainCells(width, height, options, terrainRng);

        // Generate points of interest
        const pointsOfInterest = this.generatePOIs(cells, options, poiRng);

        // Generate resources
        const resources = this.generateResources(cells, pointsOfInterest, options, resourceRng);

        // Generate buildings
        const { buildings, buildingMetadata } = this.generateBuildings(cells, resources, options, buildingRng);

        // Create the region
        return {
            id: this.generateRegionId(options, random),
            name: this.generateRegionName(options, random),
            description: `A procedurally generated region of size ${width}x${height}.`,
            width,
            height,
            cells,
            pointsOfInterest,
            resources,
            buildings,
            buildingMetadata,
            metadata: {
                seed: random.getSeedConfig().seed,
                generatorType: this.generatorType,
                parameters: {
                    width,
                    height,
                    terrain: options.terrain || {},
                    pointsOfInterest: options.pointsOfInterest || {},
                    resources: options.resources || {},
                    buildings: options.buildings || {}
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

        // Extract terrain options or use defaults
        const terrainOptions = options.terrain || {};
        const waterThreshold = terrainOptions.waterThreshold || 0.05;
        const mountainThreshold = terrainOptions.mountainThreshold || 0.7;
        const forestThreshold = terrainOptions.forestThreshold || 0.4;
        const desertThreshold = terrainOptions.desertThreshold || 0.1;
        const urbanChance = terrainOptions.urbanChance || 0.1;

        // Track which terrain types we've found
        const found = {
            water: false,
            mountain: false,
            forest: false,
            desert: false,
            urban: false,
            plains: false
        };

        // Create a noise map for terrain generation with elevation and moisture values
        const elevationRng = random.createChild('elevation');
        const moistureRng = random.createChild('moisture');

        // Generate cells
        for (let y = 0; y < height; y++) {
            for (let x = 0; x < width; x++) {
                // Generate elevation values with derived RNGs to ensure determinism
                const elevationRngForCell = elevationRng.createChild(`x${x}y${y}`);
                const elevation = elevationRngForCell.random();

                // Generate moisture values
                const moistureRngForCell = moistureRng.createChild(`x${x}y${y}`);
                const moisture = moistureRngForCell.random();

                // Determine terrain type based on elevation and moisture
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

                // Create the cell
                cells.push({
                    x,
                    y,
                    terrain,
                    elevation,
                    moisture
                });
            }
        }

        // Ensure we have at least one of each terrain type
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

        // Create a new RNG for this process
        const assignRng = random.createChild('terrain-assign');

        // Create a list of cells we can modify (away from edges)
        const candidateCells = cells.filter(cell =>
            cell.x > 1 && cell.y > 1 &&
            cell.x < cells[0].x - 1 && cell.y < cells[0].y - 1
        );

        // Ensure we have at least one of each terrain type
        for (const terrainType of terrainTypes) {
            if (!found[terrainType]) {
                // Pick a random candidate cell
                const cellIndex = assignRng.randomInt(0, candidateCells.length - 1);
                const cell = candidateCells[cellIndex];

                // Find the matching cell in our cells array
                const targetCell = cells.find(c => c.x === cell.x && c.y === cell.y);
                if (targetCell) {
                    targetCell.terrain = terrainType;
                }

                // Remove the cell from candidates
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

        // Define POI templates
        const poiTemplates = [
            { id: 'ruins', weight: 0.7, minDistance: 3 },
            { id: 'cave', weight: 0.5, minDistance: 4 },
            { id: 'settlement', weight: 0.3, minDistance: 5 },
            { id: 'shrine', weight: 0.8, minDistance: 2 },
            { id: 'dungeon', weight: 0.2, minDistance: 6 }
        ];

        // Create child RNGs for different steps
        const attemptRng = random.createChild('poi-attempts');
        const templateRng = random.createChild('poi-templates');
        const positionRng = random.createChild('poi-positions');

        // Generate POIs
        while (poiCount < maxPOIs && attempt < maxAttempts) {
            attempt++;

            // Create a child RNG for this attempt to ensure determinism
            const currentAttemptRng = attemptRng.createChild(`attempt-${attempt}`);

            // Choose a template using weighted selection
            const templateWeights = poiTemplates.map(t => t.weight);
            const template = templateRng.randomWeightedElement(poiTemplates, templateWeights);

            // Choose a random position
            const x = positionRng.randomInt(0, options.width - 1);
            const y = positionRng.randomInt(0, options.height - 1);

            // Find the cell at this position
            const cell = cells.find(c => c.x === x && c.y === y);
            if (!cell || !allowedTerrains.includes(cell.terrain)) {
                continue;
            }

            // Check minimum distance from other POIs
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

            // Add the POI
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

        // Define resource templates
        const resourceTemplates = [
            { id: 'wood', weight: 0.8, terrains: ['forest'] },
            { id: 'stone', weight: 0.7, terrains: ['mountain'] },
            { id: 'herbs', weight: 0.6, terrains: ['forest', 'plains'] },
            { id: 'ore', weight: 0.4, terrains: ['mountain'] },
            { id: 'fish', weight: 0.5, terrains: ['water'] },
            { id: 'gems', weight: 0.2, terrains: ['mountain', 'cave'] },
            { id: 'fruit', weight: 0.6, terrains: ['forest', 'plains'] }
        ];

        // Create child RNGs for different steps
        const attemptRng = random.createChild('resource-attempts');
        const templateRng = random.createChild('resource-templates');
        const positionRng = random.createChild('resource-positions');
        const amountRng = random.createChild('resource-amounts');

        // Generate resources
        while (resourceCount < maxResources && attempt < maxAttempts) {
            attempt++;

            // Create a child RNG for this attempt to ensure determinism
            const currentAttemptRng = attemptRng.createChild(`attempt-${attempt}`);

            // Choose a template using weighted selection
            const templateWeights = resourceTemplates.map(t => t.weight);
            const template = templateRng.randomWeightedElement(resourceTemplates, templateWeights);

            // Choose a random position
            const x = positionRng.randomInt(0, options.width - 1);
            const y = positionRng.randomInt(0, options.height - 1);

            // Find the cell at this position
            const cell = cells.find(c => c.x === x && c.y === y);
            if (!cell || !template.terrains.includes(cell.terrain)) {
                continue;
            }

            // Generate the amount of resource
            const amount = amountRng.random() * 0.5 + 0.5; // 0.5 to 1.0

            // Add the resource
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

    /**
     * Generate buildings for the region
     * @param cells Array of region cells
     * @param resources Array of resources
     * @param options Generation options
     * @param random Random number generator
     * @returns Object with buildings array and buildingMetadata
     */
    private generateBuildings(
        cells: RegionCell[],
        resources: Resource[],
        options: RegionGeneratorOptions,
        random: IRandomGenerator
    ): { buildings: Building[]; buildingMetadata: any } {
        const buildingOptions = options.buildings || {};
        const maxBuildings = buildingOptions.maxBuildings || 50;
        const allowedTypes = buildingOptions.allowedTypes || ['default'];
        const ruleEngine = new DefaultPlacementRuleEngine();
        const placementRules: PlacementRule[] = (buildingOptions.placementRules as any) || [
            { allowedTerrains: ['plains', 'forest', 'urban', 'mountain'] }
        ];
        const materialStyles: BuildingMaterialStyle[] = buildingOptions.materialStyles || [
            { material: 'wood', style: 'default' },
            { material: 'stone', style: 'mountain', biome: 'mountain' },
            { material: 'clay', style: 'desert', biome: 'desert' }
        ];
        const customizationHooks = buildingOptions.customizationHooks || {};

        const buildings: Building[] = [];
        const usedCells = new Set<string>();
        let attempts = 0;
        const maxAttempts = maxBuildings * 20;

        // Helper: select material/style
        function selectMaterialStyle(cell: RegionCell): BuildingMaterialStyle {
            // Prefer biome/terrain match
            for (const ms of materialStyles) {
                if (ms.biome && cell.terrain === ms.biome) return ms;
            }
            // Fallback to first
            return materialStyles[0];
        }

        // Helper: get cell key
        function cellKey(x: number, y: number) { return `${x},${y}`; }

        // Main building placement loop
        while (buildings.length < maxBuildings && attempts < maxAttempts) {
            attempts++;
            // Pick a random cell
            const idx = random.randomInt(0, cells.length - 1);
            const cell = cells[idx];
            const key = cellKey(cell.x, cell.y);
            if (usedCells.has(key)) continue;
            // Avoid water, steep slopes, and edge cases
            if (cell.terrain === 'water' || (cell.elevation !== undefined && cell.elevation < 0.05)) continue;
            // Placement rules (new engine)
            const context: PlacementRuleContext = { cells, buildings, resources };
            const ruleResult: PlacementRuleResult = ruleEngine.evaluate(cell, context, placementRules);
            if (!ruleResult.valid) {
                continue;
            }
            // --- Customization API: pre-generation hooks ---
            let buildingParams: Partial<Building> = {
                id: `building-${buildings.length}`,
                templateId: allowedTypes[0],
                x: cell.x,
                y: cell.y,
                elevation: cell.elevation,
                rotation: random.randomInt(0, 3) * 90,
                biome: cell.terrain,
                terrainType: cell.terrain
            };
            for (const hook of BuildingCustomizationAPIInstance.getHooks()) {
                const result = hook('pre', buildingParams, context);
                if (result) {
                    buildingParams = { ...buildingParams, ...result };
                }
            }
            // Terrain adaptation: check slope (neighboring elevation difference)
            const neighbors = cells.filter(c => Math.abs(c.x - cell.x) <= 1 && Math.abs(c.y - cell.y) <= 1 && !(c.x === cell.x && c.y === cell.y));
            let maxSlope = 0;
            let avgSlope = 0;
            let slopeCount = 0;
            for (const n of neighbors) {
                if (n.elevation !== undefined && cell.elevation !== undefined) {
                    const slope = Math.abs(cell.elevation - n.elevation);
                    if (slope > maxSlope) maxSlope = slope;
                    avgSlope += slope;
                    slopeCount++;
                }
            }
            avgSlope = slopeCount > 0 ? avgSlope / slopeCount : 0;
            if (maxSlope > 0.2) continue; // Too steep for building
            // Foundation adaptation
            let foundationType = 'standard';
            let foundationDepth = 1;
            let materialStrength = 1;
            if (maxSlope > 0.1) {
                foundationType = 'stilted';
                foundationDepth = 3;
                materialStrength = 0.8;
            } else if (cell.terrain === 'mountain') {
                foundationType = 'anchored';
                foundationDepth = 2;
                materialStrength = 1.2;
            }
            // Entrance adaptation: flag if any neighbor has significant elevation difference
            let requiresEntranceStair = false;
            for (const n of neighbors) {
                if (n.elevation !== undefined && cell.elevation !== undefined) {
                    if (Math.abs(cell.elevation - n.elevation) > 0.1) {
                        requiresEntranceStair = true;
                        break;
                    }
                }
            }
            // Material/style selection (now using StyleMaterialSystem)
            const environment = {
                temperature: cell.moisture !== undefined ? 1 - cell.moisture : 0.5, // Example: inverse of moisture
                humidity: cell.moisture !== undefined ? cell.moisture : 0.5,
                altitude: cell.elevation !== undefined ? cell.elevation : 0.5
            };
            const matStyleResult = selectMaterialAndStyle(cell, resources, environment);
            // Customization config
            let customization = {};
            // --- Customization API: post-generation hooks ---
            let building: Building = {
                ...buildingParams,
                foundationType,
                material: matStyleResult.material,
                style: matStyleResult.style,
                integrity: 1,
                customization,
                foundationDepth,
                materialStrength,
                slope: avgSlope,
                requiresEntranceStair,
                textureVariant: matStyleResult.textureVariant,
                modelVariant: matStyleResult.modelVariant
            } as any;
            for (const hook of BuildingCustomizationAPIInstance.getHooks()) {
                const result = hook('post', building, context);
                if (result) {
                    building = { ...building, ...result };
                }
            }
            buildings.push(building);
            usedCells.add(key);
        }

        // Chunked generation and LOD metadata (stub for future optimization)
        const buildingMetadata = {
            placementRules,
            materialStyles,
            chunking: {
                chunkSize: 16,
                totalChunks: Math.ceil(Math.sqrt(buildings.length) / 16)
            },
            lod: {
                levels: [0, 1, 2],
                strategy: 'distance-based'
            }
        };

        return { buildings, buildingMetadata };
    }
} 