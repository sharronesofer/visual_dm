/**
 * WorldSystem.ts
 * 
 * Implements world generation, map management, and points of interest.
 * This system is responsible for creating and managing the game world structure.
 */

import { BaseSystemManager, SystemConfig, SystemEvent } from './BaseSystemManager';
import { Repository } from './DatabaseLayer';
import {
    BaseEntity,
    createBaseEntity,
    updateEntityTimestamp,
    POI,
    POIType,
    POISize,
    POIStatus,
    TerrainType
} from './DataModels';
import { BuildingSystem } from '../../systems/BuildingSystem';
import { SocialSubtype } from '../../poi/types/POITypes';
import { MarketSystem } from '../../systems/economy/MarketSystem';
// import { EventBus } from '../core/events/EventBus';
// import { SceneEventType, ISceneEvent } from '../core/events/SceneEventTypes';

// Additional interfaces for the world system
export interface MapRegion extends BaseEntity {
    name: string;
    description: string;
    terrain: TerrainType;
    difficulty: number; // 1-100 scale
    position: { x: number, y: number };
    size: { width: number, height: number };
    parentRegionId?: string;
    mapId: string;
    tags: string[];
    climate?: string;
    resources?: string[];
    controllingFaction?: string;
    discoveredBy?: string[];
}

export interface GameMap extends BaseEntity {
    name: string;
    description: string;
    width: number;
    height: number;
    seed: string;
    defaultTerrain: TerrainType;
    tags: string[];
    roughness?: number;
    regionDensity?: number;
    poiDensity?: number;
    generationCompleted: boolean;
}

export interface MapTile extends BaseEntity {
    mapId: string;
    x: number;
    y: number;
    terrain: TerrainType;
    elevation: number;
    passable: boolean;
    explored: boolean;
    exploredBy: string[];
    regionId?: string;
    poiId?: string;
    movementCost: number;
    tags: string[];
}

export interface PathOptions {
    avoidTerrainTypes?: TerrainType[];
    preferredTerrainTypes?: TerrainType[];
    maxMovementCost?: number;
    ignoreExploration?: boolean;
}

export interface WorldGenerationOptions {
    name: string;
    width: number;
    height: number;
    seed: string;
    roughness?: number;
    defaultTerrain?: TerrainType;
    regionDensity?: number;
    poiDensity?: number;
}

/**
 * WorldSystem handles world generation, map management, and point of interest functionality
 */
export class WorldSystem extends BaseSystemManager {
    // Repositories
    public mapRepository: Repository<GameMap>;
    public regionRepository: Repository<MapRegion>;
    public tileRepository: Repository<MapTile>;
    public poiRepository: Repository<POI>;

    private buildingSystem?: BuildingSystem;

    constructor(config: SystemConfig, buildingSystem?: BuildingSystem) {
        super({
            ...config,
            name: config.name || 'WorldSystem',
            dependencies: []
        });
        this.buildingSystem = buildingSystem;
    }

    /**
     * Initialize repositories for world data
     */
    protected async initializeRepositories(): Promise<void> {
        this.mapRepository = this.createRepository<GameMap>(
            'maps',
            ['name', 'width', 'height', 'generationCompleted']
        );

        this.regionRepository = this.createRepository<MapRegion>(
            'regions',
            ['name', 'terrain', 'mapId', 'position.x', 'position.y', 'parentRegionId']
        );

        this.tileRepository = this.createRepository<MapTile>(
            'tiles',
            ['mapId', 'x', 'y', 'terrain', 'regionId', 'poiId', 'passable', 'explored']
        );

        this.poiRepository = this.createRepository<POI>(
            'pois',
            ['name', 'type', 'status', 'regionId', 'position.x', 'position.y']
        );
    }

    /**
     * Initialize system-specific functionality
     */
    protected async initializeSystem(): Promise<void> {
        // Set up event handlers
        this.on('poi:discovered', this.handlePOIDiscovered.bind(this));
        this.on('poi:visited', this.handlePOIVisited.bind(this));
        this.on('region:discovered', this.handleRegionDiscovered.bind(this));
        this.on('tile:explored', this.handleTileExplored.bind(this));
    }

    /**
     * System shutdown
     */
    protected async shutdownSystem(): Promise<void> {
        this.logInfo('Shutting down WorldSystem');
    }

    /**
     * Generate a new game world
     */
    public async generateWorld(options: WorldGenerationOptions): Promise<GameMap> {
        this.logInfo(`Generating new world: ${options.name} (${options.width}x${options.height})`);

        // Create the map entity
        const gameMap: GameMap = {
            ...createBaseEntity(),
            name: options.name,
            description: `Game world: ${options.name}`,
            width: options.width,
            height: options.height,
            seed: options.seed,
            defaultTerrain: options.defaultTerrain || TerrainType.PLAIN,
            tags: ['world', 'game_map'],
            roughness: options.roughness || 0.5,
            regionDensity: options.regionDensity || 0.05,
            poiDensity: options.poiDensity || 0.02,
            generationCompleted: false
        };

        const createdMap = await this.mapRepository.create(gameMap);

        // Generate world content in the background
        this.generateWorldContent(createdMap).catch(error => {
            this.logError(`Failed to generate world content: ${error.message}`);
        });

        return createdMap;
    }

    /**
     * Generate world content (regions, tiles, POIs)
     * This runs asynchronously after map creation
     */
    private async generateWorldContent(map: GameMap): Promise<void> {
        try {
            this.logInfo(`Starting world content generation for ${map.name}`);

            // Step 1: Generate base terrain and elevation
            await this.generateBaseTerrain(map);

            // Step 2: Generate regions
            await this.generateRegions(map);

            // Step 3: Generate POIs
            await this.generatePOIs(map);

            // Mark generation as complete
            await this.mapRepository.update(map.id, { generationCompleted: true });

            this.logInfo(`World generation completed for ${map.name}`);

            // Emit event for world generation complete
            await this.emitEvent({
                type: 'world:generated',
                source: this.name,
                timestamp: Date.now(),
                data: { map }
            });
        } catch (error) {
            this.logError(`World generation failed: ${error.message}`);
            // Mark generation as failed but still completed
            await this.mapRepository.update(map.id, {
                generationCompleted: true,
                tags: [...map.tags, 'generation_error']
            });
        }
    }

    /**
     * Generate base terrain and elevation for the map
     */
    private async generateBaseTerrain(map: GameMap): Promise<void> {
        this.logInfo(`Generating base terrain for ${map.name}`);

        // Use simple Diamond-Square algorithm to generate elevation
        // This is a simplified version for demonstration purposes
        const size = Math.pow(2, Math.ceil(Math.log2(Math.max(map.width, map.height)))) + 1;
        const elevation: number[][] = Array(size).fill(0).map(() => Array(size).fill(0));

        // Set initial corner values
        elevation[0][0] = Math.random();
        elevation[0][size - 1] = Math.random();
        elevation[size - 1][0] = Math.random();
        elevation[size - 1][size - 1] = Math.random();

        // Diamond-Square algorithm
        let step = size - 1;
        let roughness = map.roughness || 0.5;

        while (step > 1) {
            const halfStep = Math.floor(step / 2);

            // Diamond step
            for (let y = 0; y < size - 1; y += step) {
                for (let x = 0; x < size - 1; x += step) {
                    const centerX = x + halfStep;
                    const centerY = y + halfStep;

                    elevation[centerY][centerX] = (
                        elevation[y][x] +
                        elevation[y][x + step] +
                        elevation[y + step][x] +
                        elevation[y + step][x + step]
                    ) / 4 + (Math.random() * 2 - 1) * roughness;
                }
            }

            // Square step
            for (let y = 0; y < size; y += halfStep) {
                for (let x = (y + halfStep) % step; x < size; x += step) {
                    let count = 0;
                    let sum = 0;

                    // Check the four adjacent values if they exist
                    if (y >= halfStep) { sum += elevation[y - halfStep][x]; count++; }
                    if (y + halfStep < size) { sum += elevation[y + halfStep][x]; count++; }
                    if (x >= halfStep) { sum += elevation[y][x - halfStep]; count++; }
                    if (x + halfStep < size) { sum += elevation[y][x + halfStep]; count++; }

                    elevation[y][x] = sum / count + (Math.random() * 2 - 1) * roughness;
                }
            }

            // Decrease roughness and step size
            step = halfStep;
            roughness *= 0.5;
        }

        // Create tiles based on elevation
        const batch: MapTile[] = [];
        const batchSize = 100;

        for (let y = 0; y < map.height; y++) {
            for (let x = 0; x < map.width; x++) {
                const scaledElevation = Math.min(Math.max(elevation[y][x], 0), 1);
                let terrain = map.defaultTerrain;
                let passable = true;
                let movementCost = 1;

                // Determine terrain type based on elevation
                if (scaledElevation < 0.2) {
                    terrain = TerrainType.WATER;
                    passable = false;
                    movementCost = 5;
                } else if (scaledElevation < 0.4) {
                    terrain = TerrainType.PLAIN;
                    movementCost = 1;
                } else if (scaledElevation < 0.6) {
                    terrain = TerrainType.FOREST;
                    movementCost = 1.5;
                } else if (scaledElevation < 0.8) {
                    terrain = TerrainType.PLAIN;
                    movementCost = 1;
                } else {
                    terrain = TerrainType.MOUNTAIN;
                    passable = scaledElevation < 0.9;
                    movementCost = 3;
                }

                // Create the tile entity
                const tile: MapTile = {
                    ...createBaseEntity(),
                    mapId: map.id,
                    x,
                    y,
                    terrain,
                    elevation: scaledElevation,
                    passable,
                    explored: false,
                    exploredBy: [],
                    movementCost,
                    tags: [terrain.toLowerCase()]
                };

                batch.push(tile);

                // Create tiles in batches to avoid memory issues
                if (batch.length >= batchSize) {
                    await Promise.all(batch.map(t => this.tileRepository.create(t)));
                    batch.length = 0;
                }
            }
        }

        // Create any remaining tiles
        if (batch.length > 0) {
            await Promise.all(batch.map(t => this.tileRepository.create(t)));
        }

        this.logInfo(`Generated ${map.width * map.height} tiles for ${map.name}`);
    }

    /**
     * Generate regions for the map
     */
    private async generateRegions(map: GameMap): Promise<void> {
        this.logInfo(`Generating regions for ${map.name}`);

        // Calculate number of regions based on density and map size
        const regionDensity = map.regionDensity || 0.05;
        const mapArea = map.width * map.height;
        const numRegions = Math.max(1, Math.floor(mapArea * regionDensity / 10000));

        this.logInfo(`Generating ${numRegions} regions`);

        // Create regions
        for (let i = 0; i < numRegions; i++) {
            // Determine region size
            const width = 10 + Math.floor(Math.random() * 20);
            const height = 10 + Math.floor(Math.random() * 20);

            // Determine region position
            const x = Math.floor(Math.random() * (map.width - width));
            const y = Math.floor(Math.random() * (map.height - height));

            // Get a sample of tiles to determine dominant terrain
            const sampleSize = Math.min(50, width * height);
            const sampleTiles: MapTile[] = [];

            for (let j = 0; j < sampleSize; j++) {
                const sampleX = x + Math.floor(Math.random() * width);
                const sampleY = y + Math.floor(Math.random() * height);

                const tiles = await this.tileRepository.query(
                    t => t.mapId === map.id && t.x === sampleX && t.y === sampleY
                );

                if (tiles.length > 0) {
                    sampleTiles.push(tiles[0]);
                }
            }

            // Count terrain types
            const terrainCounts: Record<string, number> = {};
            sampleTiles.forEach(tile => {
                terrainCounts[tile.terrain] = (terrainCounts[tile.terrain] || 0) + 1;
            });

            // Determine dominant terrain
            let dominantTerrain = map.defaultTerrain;
            let maxCount = 0;

            Object.entries(terrainCounts).forEach(([terrain, count]) => {
                if (count > maxCount) {
                    dominantTerrain = terrain as TerrainType;
                    maxCount = count;
                }
            });

            // Generate region name
            const regionNames = [
                'Valley', 'Hills', 'Plateau', 'Plains', 'Forest', 'Woods',
                'Grove', 'Marsh', 'Swamp', 'Highlands', 'Mountains', 'Lake'
            ];

            const regionAdjectives = [
                'Verdant', 'Misty', 'Shadowy', 'Sunlit', 'Ancient', 'Lost',
                'Forgotten', 'Eastern', 'Western', 'Northern', 'Southern', 'Hidden'
            ];

            const regionPrefix = regionAdjectives[Math.floor(Math.random() * regionAdjectives.length)];
            const regionSuffix = regionNames[Math.floor(Math.random() * regionNames.length)];
            const regionName = `${regionPrefix} ${regionSuffix}`;

            // Create the region entity
            const region: MapRegion = {
                ...createBaseEntity(),
                name: regionName,
                description: `A ${regionPrefix.toLowerCase()} ${regionSuffix.toLowerCase()} region with ${dominantTerrain.toLowerCase()} terrain.`,
                terrain: dominantTerrain,
                difficulty: 10 + Math.floor(Math.random() * 50),
                position: { x, y },
                size: { width, height },
                mapId: map.id,
                tags: [dominantTerrain.toLowerCase(), 'region'],
                climate: this.getClimateForTerrain(dominantTerrain),
                resources: this.getResourcesForTerrain(dominantTerrain)
            };

            const createdRegion = await this.regionRepository.create(region);

            // Update tiles in the region
            const regionTiles = await this.tileRepository.query(
                t => t.mapId === map.id &&
                    t.x >= x && t.x < (x + width) &&
                    t.y >= y && t.y < (y + height)
            );

            for (const tile of regionTiles) {
                await this.tileRepository.update(tile.id, { regionId: createdRegion.id });
            }
        }
    }

    /**
     * Generate POIs (Points of Interest) for the map
     */
    private async generatePOIs(map: GameMap): Promise<void> {
        this.logInfo(`Generating POIs for ${map.name}`);

        // Get all regions
        const regions = await this.regionRepository.query(r => r.mapId === map.id);

        for (const region of regions) {
            // Calculate number of POIs based on density and region size
            const poiDensity = map.poiDensity || 0.02;
            const regionArea = region.size.width * region.size.height;
            const numPOIs = Math.max(1, Math.floor(regionArea * poiDensity / 100));

            this.logInfo(`Generating ${numPOIs} POIs for region ${region.name}`);

            for (let i = 0; i < numPOIs; i++) {
                // Determine POI position within region
                const x = region.position.x + Math.floor(Math.random() * region.size.width);
                const y = region.position.y + Math.floor(Math.random() * region.size.height);

                // Check if the tile is passable
                const tiles = await this.tileRepository.query(
                    t => t.mapId === map.id && t.x === x && t.y === y
                );

                if (tiles.length === 0 || !tiles[0].passable) {
                    // Skip non-passable tiles
                    continue;
                }

                // Determine POI type based on terrain
                const tile = tiles[0];
                const poiType = this.getPOITypeForTerrain(tile.terrain);

                // Generate POI name
                const poiName = this.generatePOIName(poiType, region.terrain);

                // Create the POI entity
                const poi: POI = {
                    ...createBaseEntity(),
                    name: poiName,
                    description: `A ${poiType.toLowerCase()} in the ${region.name}.`,
                    type: poiType,
                    size: this.getPOISizeForType(poiType),
                    status: POIStatus.UNDISCOVERED,
                    region: region.name,
                    position: { x, y },
                    tags: [poiType.toLowerCase(), region.terrain.toLowerCase()],
                    difficulty: region.difficulty || 10,
                    inhabitants: [],
                    loot: [],
                    associatedQuestIds: [],
                    entrances: []
                };

                const createdPOI = await this.poiRepository.create(poi);

                // Update the tile with the POI ID
                await this.tileRepository.update(tile.id, { poiId: createdPOI.id });
            }
        }
    }

    /**
     * Get climate type based on terrain
     */
    private getClimateForTerrain(terrain: TerrainType): string {
        switch (terrain) {
            case TerrainType.DESERT:
                return 'arid';
            case TerrainType.FOREST:
                return 'temperate';
            case TerrainType.MOUNTAIN:
                return 'alpine';
            case TerrainType.PLAIN:
                return 'temperate';
            case TerrainType.SNOW:
                return 'arctic';
            case TerrainType.SWAMP:
                return 'humid';
            case TerrainType.URBAN:
                return 'temperate';
            case TerrainType.WATER:
                return 'maritime';
            default:
                return 'temperate';
        }
    }

    /**
     * Get resources based on terrain
     */
    private getResourcesForTerrain(terrain: TerrainType): string[] {
        switch (terrain) {
            case TerrainType.DESERT:
                return ['sand', 'cacti', 'minerals'];
            case TerrainType.FOREST:
                return ['wood', 'herbs', 'game'];
            case TerrainType.MOUNTAIN:
                return ['ore', 'stone', 'gems'];
            case TerrainType.PLAIN:
                return ['crops', 'grass', 'livestock'];
            case TerrainType.SNOW:
                return ['ice', 'fur', 'crystals'];
            case TerrainType.SWAMP:
                return ['reeds', 'mushrooms', 'herbs'];
            case TerrainType.URBAN:
                return ['trade', 'crafts', 'labor'];
            case TerrainType.WATER:
                return ['fish', 'shells', 'water'];
            default:
                return ['misc', 'unknown'];
        }
    }

    /**
     * Get POI type based on terrain
     */
    private getPOITypeForTerrain(terrain: TerrainType): POIType {
        const poiTypes = [
            POIType.SETTLEMENT,
            POIType.DUNGEON,
            POIType.LANDMARK,
            POIType.RESOURCE,
            POIType.ENCOUNTER,
            POIType.QUEST,
            POIType.SECRET
        ];

        // Weight the selection based on terrain
        let weights: number[] = [25, 20, 30, 15, 10, 5, 5]; // Default weights

        switch (terrain) {
            case TerrainType.DESERT:
                weights = [15, 35, 25, 15, 10, 5, 5];
                break;
            case TerrainType.FOREST:
                weights = [20, 15, 35, 20, 10, 5, 5];
                break;
            case TerrainType.MOUNTAIN:
                weights = [10, 25, 30, 30, 5, 5, 5];
                break;
            case TerrainType.PLAIN:
                weights = [35, 15, 30, 10, 10, 5, 5];
                break;
            case TerrainType.WATER:
                weights = [15, 10, 45, 5, 25, 5, 5];
                break;
            case TerrainType.URBAN:
                weights = [70, 5, 15, 5, 5, 5, 5];
                break;
        }

        // Select based on weighted probability
        const totalWeight = weights.reduce((a, b) => a + b, 0);
        let random = Math.random() * totalWeight;

        for (let i = 0; i < weights.length; i++) {
            if (random < weights[i]) {
                return poiTypes[i];
            }
            random -= weights[i];
        }

        return POIType.LANDMARK;
    }

    /**
     * Get POI size based on POI type
     */
    private getPOISizeForType(poiType: POIType): POISize {
        switch (poiType) {
            case POIType.SETTLEMENT:
                const settlementSizes = [POISize.TINY, POISize.SMALL, POISize.MEDIUM, POISize.LARGE];
                const settlementWeights = [20, 40, 30, 10];
                return this.weightedRandom(settlementSizes, settlementWeights);

            case POIType.DUNGEON:
                const dungeonSizes = [POISize.TINY, POISize.SMALL, POISize.MEDIUM, POISize.LARGE];
                const dungeonWeights = [25, 35, 30, 10];
                return this.weightedRandom(dungeonSizes, dungeonWeights);

            case POIType.LANDMARK:
                const landmarkSizes = [POISize.TINY, POISize.SMALL, POISize.MEDIUM];
                const landmarkWeights = [30, 40, 30];
                return this.weightedRandom(landmarkSizes, landmarkWeights);

            default:
                return POISize.SMALL;
        }
    }

    /**
     * Select a random element based on weights
     */
    private weightedRandom<T>(items: T[], weights: number[]): T {
        const totalWeight = weights.reduce((a, b) => a + b, 0);
        let random = Math.random() * totalWeight;

        for (let i = 0; i < weights.length; i++) {
            if (random < weights[i]) {
                return items[i];
            }
            random -= weights[i];
        }

        return items[0];
    }

    /**
     * Generate a name for a POI based on type and terrain
     */
    private generatePOIName(poiType: POIType, terrain: TerrainType): string {
        // First names for different POI types
        const poiPrefixes: Record<POIType, string[]> = {
            [POIType.SETTLEMENT]: [
                'Greenfield', 'Riverdale', 'Oakridge', 'Stonehaven', 'Pinecrest',
                'Meadowbrook', 'Eastwatch', 'Westport', 'Northkeep', 'Southford'
            ],
            [POIType.DUNGEON]: [
                'Darkdeep', 'Shadowfell', 'Gloomhaven', 'Dreadpeak', 'Grimhold',
                'Doomvault', 'Netherdepth', 'Blackcrypt', 'Fellcavern', 'Direlair'
            ],
            [POIType.LANDMARK]: [
                'Whispering', 'Towering', 'Glimmering', 'Watchful', 'Eternal',
                'Silent', 'Majestic', 'Sacred', 'Ancient', 'Solitary'
            ],
            [POIType.RESOURCE]: [],
            [POIType.ENCOUNTER]: [],
            [POIType.QUEST]: [],
            [POIType.SECRET]: []
        };

        // Second parts based on POI type
        const poiSuffixes: Record<POIType, string[]> = {
            [POIType.SETTLEMENT]: [
                'Village', 'Town', 'Hamlet', 'Outpost', 'Camp',
                'Fort', 'Keep', 'Refuge', 'Haven', 'Landing'
            ],
            [POIType.DUNGEON]: [
                'Dungeon', 'Cave', 'Mine', 'Cavern', 'Labyrinth',
                'Tomb', 'Crypt', 'Lair', 'Den', 'Abyss'
            ],
            [POIType.LANDMARK]: [
                'Peak', 'Grove', 'Stone', 'Tree', 'Spire',
                'Monolith', 'Arch', 'Falls', 'Pillar', 'Vista'
            ],
            [POIType.RESOURCE]: [],
            [POIType.ENCOUNTER]: [],
            [POIType.QUEST]: [],
            [POIType.SECRET]: []
        };

        // Terrain-based modifiers
        const terrainModifiers: Record<TerrainType, string[]> = {
            [TerrainType.PLAIN]: ['Golden', 'Verdant', 'Grassy', 'Rolling', 'Open'],
            [TerrainType.FOREST]: ['Wooded', 'Mossy', 'Leafy', 'Shadowy', 'Green'],
            [TerrainType.MOUNTAIN]: ['Rocky', 'Craggy', 'Stone', 'Cliff', 'High'],
            [TerrainType.WATER]: ['Misty', 'Watery', 'Damp', 'Flooded', 'Blue'],
            [TerrainType.DESERT]: ['Sandy', 'Dusty', 'Dry', 'Barren', 'Red'],
            [TerrainType.SWAMP]: ['Murky', 'Boggy', 'Muddy', 'Fetid', 'Dark'],
            [TerrainType.SNOW]: ['Frozen', 'Icy', 'Frosty', 'White', 'Cold'],
            [TerrainType.URBAN]: ['Bustling', 'Crowded', 'Paved', 'Walled', 'Busy']
        };

        // Randomly select name components
        const prefix = poiPrefixes[poiType][Math.floor(Math.random() * poiPrefixes[poiType].length)];
        const suffix = poiSuffixes[poiType][Math.floor(Math.random() * poiSuffixes[poiType].length)];

        // Use terrain modifier with 30% chance
        if (Math.random() < 0.3 && terrainModifiers[terrain]) {
            const modifier = terrainModifiers[terrain][Math.floor(Math.random() * terrainModifiers[terrain].length)];
            return `${prefix} ${modifier} ${suffix}`;
        }

        return `${prefix} ${suffix}`;
    }

    /**
     * Get map by ID
     */
    public async getWorldMap(mapId: string): Promise<GameMap | null> {
        return this.mapRepository.findById(mapId);
    }

    /**
     * Get all world maps
     */
    public async getAllWorldMaps(): Promise<GameMap[]> {
        return this.mapRepository.findAll();
    }

    /**
     * Get all regions for a map
     */
    public async getRegionsForMap(mapId: string): Promise<MapRegion[]> {
        return this.regionRepository.findBy('mapId', mapId);
    }

    /**
     * Get tile at a specific position
     */
    public async getTileAt(x: number, y: number, mapId?: string): Promise<MapTile | null> {
        if (!mapId) {
            // If no mapId specified, get the first map
            const maps = await this.mapRepository.findAll();
            if (maps.length === 0) return null;
            mapId = maps[0].id;
        }

        const tiles = await this.tileRepository.query(
            t => t.mapId === mapId && t.x === x && t.y === y
        );

        return tiles.length > 0 ? tiles[0] : null;
    }

    /**
     * Get POI by ID
     */
    public async getPOI(poiId: string): Promise<POI | null> {
        return this.poiRepository.findById(poiId);
    }

    /**
     * Mark a tile as explored
     */
    public async exploreTile(x: number, y: number, entityId: string, mapId?: string): Promise<MapTile | null> {
        const tile = await this.getTileAt(x, y, mapId);
        if (!tile) return null;

        if (!tile.explored || !tile.exploredBy.includes(entityId)) {
            // Update tile as explored
            const updatedTile = await this.tileRepository.update(
                tile.id,
                {
                    explored: true,
                    exploredBy: [...tile.exploredBy, entityId]
                }
            );

            if (updatedTile) {
                // Emit tile explored event
                await this.emitEvent({
                    type: 'tile:explored',
                    source: this.name,
                    timestamp: Date.now(),
                    data: {
                        tile: updatedTile,
                        entityId
                    }
                });

                // If tile has a POI and the POI is hidden, make it visible
                if (updatedTile.poiId) {
                    const poi = await this.poiRepository.findById(updatedTile.poiId);
                    if (poi && poi.status === POIStatus.UNDISCOVERED) {
                        await this.discoverPOI(poi.id, entityId);
                    }
                }
            }

            return updatedTile;
        }

        return tile;
    }

    /**
     * Discover a POI
     */
    public async discoverPOI(poiId: string, entityId: string): Promise<POI | null> {
        const poi = await this.poiRepository.findById(poiId);
        if (!poi) return null;

        // Update status to visible (not yet visited)
        await this.poiRepository.update(poiId, { status: POIStatus.VISIBLE });

        // Emit POI discovered event
        await this.emitEvent({
            type: 'poi:discovered',
            source: this.name,
            timestamp: Date.now(),
            data: {
                poi,
                entityId
            }
        });

        // If the POI is a market, notify the MarketSystem
        if (poi.type === POIType.SOCIAL && poi.subtype === SocialSubtype.MARKET) {
            // TODO: Replace with correct MarketSystem instance if needed
            MarketSystem.getInstance().notifyMarketDiscovered(poi.id);
        }

        return poi;
    }

    /**
     * Visit a POI
     */
    public async visitPOI(poiId: string, entityId: string): Promise<POI | null> {
        const poi = await this.poiRepository.findById(poiId);
        if (!poi) return null;

        // Update status to visited
        await this.poiRepository.update(poiId, { status: POIStatus.VISITED });

        // Emit POI visited event
        await this.emitEvent({
            type: 'poi:visited',
            source: this.name,
            timestamp: Date.now(),
            data: {
                poi,
                entityId
            }
        });

        return poi;
    }

    /**
     * Get tiles in an area
     */
    public async getTilesInArea(
        centerX: number,
        centerY: number,
        radius: number,
        mapId?: string
    ): Promise<MapTile[]> {
        if (!mapId) {
            // If no mapId specified, get the first map
            const maps = await this.mapRepository.findAll();
            if (maps.length === 0) return [];
            mapId = maps[0].id;
        }

        // First get tiles in the bounding square for efficiency
        const tiles = await this.getTilesInRect(
            centerX - radius,
            centerY - radius,
            centerX + radius,
            centerY + radius,
            mapId
        );

        // Then filter to only include tiles within the radius
        return tiles.filter(tile => {
            const dx = tile.x - centerX;
            const dy = tile.y - centerY;
            const distanceSquared = dx * dx + dy * dy;
            return distanceSquared <= radius * radius;
        });
    }

    /**
     * Create a seeded random number generator
     */
    private createSeededRandom(seed: string): () => number {
        // Simple implementation of a seeded random number generator
        // In a production system, you'd use a more robust algorithm
        let s = 0;
        for (let i = 0; i < seed.length; i++) {
            s += seed.charCodeAt(i);
        }

        return function () {
            s = Math.sin(s) * 10000;
            return s - Math.floor(s);
        };
    }

    // Event handlers
    private async handleMapGenerated(event: SystemEvent): Promise<void> {
        const { map } = event.data;
        this.logDebug(`Handler: Map generated - ${map.name}`);
    }

    private async handleRegionDiscovered(event: SystemEvent): Promise<void> {
        const { region, entityId } = event.data;
        this.logDebug(`Handler: Region discovered - ${region.name} by ${entityId}`);
    }

    private async handlePOIDiscovered(event: SystemEvent): Promise<void> {
        const { poi, entityId } = event.data;
        this.logDebug(`Handler: POI discovered - ${poi.name} by ${entityId}`);
    }

    private async handlePOIVisited(event: SystemEvent): Promise<void> {
        const { poi, entityId } = event.data;
        this.logDebug(`Handler: POI visited - ${poi.name} by ${entityId}`);
    }

    private async handleTileExplored(event: SystemEvent): Promise<void> {
        const { position, entityId } = event.data;
        this.logDebug(`Handler: Tile explored at (${position.x}, ${position.y}) by ${entityId}`);
    }

    /**
     * Get information about a map
     */
    public async getMap(mapId: string): Promise<GameMap | null> {
        return this.mapRepository.findById(mapId);
    }

    /**
     * Get all maps
     */
    public async getAllMaps(): Promise<GameMap[]> {
        return this.mapRepository.findAll();
    }

    /**
     * Get tiles in a rectangular area
     */
    public async getTilesInRect(
        x1: number,
        y1: number,
        x2: number,
        y2: number,
        mapId?: string
    ): Promise<MapTile[]> {
        if (!mapId) {
            // If no mapId specified, get the first map
            const maps = await this.mapRepository.findAll();
            if (maps.length === 0) return [];
            mapId = maps[0].id;
        }

        return this.tileRepository.query(
            t => t.mapId === mapId &&
                t.x >= Math.min(x1, x2) && t.x <= Math.max(x1, x2) &&
                t.y >= Math.min(y1, y2) && t.y <= Math.max(y1, y2)
        );
    }

    /**
     * Get all POIs in a region
     */
    public async getPOIsInRegion(regionId: string): Promise<POI[]> {
        return this.poiRepository.findBy('region', regionId);
    }

    /**
     * Get all POIs of a specific type
     */
    public async getPOIsByType(type: POIType): Promise<POI[]> {
        return this.poiRepository.findBy('type', type);
    }

    /**
     * Get POIs at a specific location
     */
    public async getPOIsAtLocation(
        x: number,
        y: number,
        mapId?: string
    ): Promise<POI[]> {
        const tile = await this.getTileAt(x, y, mapId);
        if (!tile || !tile.poiId) return [];

        const poi = await this.poiRepository.findById(tile.poiId);
        return poi ? [poi] : [];
    }

    /**
     * Get POIs in an area
     */
    public async getPOIsInArea(
        centerX: number,
        centerY: number,
        radius: number,
        mapId?: string
    ): Promise<POI[]> {
        const tiles = await this.getTilesInArea(centerX, centerY, radius, mapId);
        const poiIds = new Set<string>();

        // Collect unique POI IDs
        tiles.forEach(tile => {
            if (tile.poiId) poiIds.add(tile.poiId);
        });

        if (poiIds.size === 0) return [];

        // Get all POIs
        const pois: POI[] = [];
        for (const poiId of poiIds) {
            const poi = await this.poiRepository.findById(poiId);
            if (poi) pois.push(poi);
        }

        return pois;
    }

    /**
     * Get tiles in a region
     */
    public async getTilesInRegion(regionId: string): Promise<MapTile[]> {
        return this.tileRepository.findBy('regionId', regionId);
    }

    /**
     * Get the region at specific coordinates
     */
    public async getRegionAt(
        x: number,
        y: number,
        mapId?: string
    ): Promise<MapRegion | null> {
        const tile = await this.getTileAt(x, y, mapId);
        if (!tile || !tile.regionId) return null;

        return this.regionRepository.findById(tile.regionId);
    }

    /**
     * Process a world tick, including building deterioration
     */
    public async processWorldTick(): Promise<void> {
        // ... existing world tick logic ...
        if (this.buildingSystem) {
            this.buildingSystem.processHourlyDeterioration(1); // Default amount, can be parameterized
        }
        // ... rest of tick logic ...
    }
} 