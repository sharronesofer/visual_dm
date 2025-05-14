/**
 * NavigationSystem.ts
 * 
 * Implements pathfinding and character movement functionality.
 * Handles how entities navigate through the game world.
 */

import { BaseSystemManager, SystemConfig, SystemEvent, systemRegistry } from './BaseSystemManager';
import { Repository } from './DatabaseLayer';
import {
    BaseEntity,
    createBaseEntity,
    updateEntityTimestamp,
    MovementType,
    TerrainType,
    MovementCapabilities
} from './DataModels';
import { WorldSystem, MapTile, PathOptions } from './WorldSystem';

// Additional interfaces for the navigation system
export interface EntityPosition extends BaseEntity {
    entityId: string;
    mapId: string;
    position: { x: number, y: number };
    direction: number; // Degrees (0-359)
    elevation: number;
    movementState: MovementState;
    lastUpdated: number;
}

export enum MovementState {
    IDLE = 'idle',
    MOVING = 'moving',
    FOLLOWING = 'following',
    PATROLLING = 'patrolling',
    TELEPORTING = 'teleporting',
    DISABLED = 'disabled'
}

export interface PathNode {
    x: number;
    y: number;
    g: number; // Cost from start
    h: number; // Heuristic (estimated cost to goal)
    f: number; // Total cost (g + h)
    parent?: PathNode;
    movementCost: number;
}

export interface PathResult {
    success: boolean;
    path: { x: number, y: number }[];
    totalCost: number;
    message?: string;
}

export interface MovementResult {
    success: boolean;
    newPosition?: { x: number, y: number };
    distanceMoved: number;
    terrainsCrossed: TerrainType[];
    staminaUsed: number;
    message?: string;
}

export interface PatrolRoute extends BaseEntity {
    entityId: string;
    waypoints: { x: number, y: number }[];
    currentWaypointIndex: number;
    looping: boolean;
    startTime: number;
    pauseDuration: number; // Milliseconds to pause at each waypoint
}

/**
 * NavigationSystem manages entity movement and pathfinding
 */
export class NavigationSystem extends BaseSystemManager {
    private entityPositionRepository: Repository<EntityPosition>;
    private patrolRouteRepository: Repository<PatrolRoute>;
    private worldSystem: WorldSystem | null = null;

    constructor(config: SystemConfig) {
        super({
            ...config,
            name: config.name || 'NavigationSystem',
            dependencies: [
                { name: 'WorldSystem', required: true }
            ]
        });
    }

    /**
     * Initialize navigation repositories
     */
    protected async initializeRepositories(): Promise<void> {
        this.entityPositionRepository = this.createRepository<EntityPosition>(
            'entity_positions',
            ['entityId', 'mapId', 'position.x', 'position.y', 'movementState']
        );

        this.patrolRouteRepository = this.createRepository<PatrolRoute>(
            'patrol_routes',
            ['entityId', 'looping']
        );
    }

    /**
     * Initialize system-specific functionality
     */
    protected async initializeSystem(): Promise<void> {
        // Get reference to the world system
        this.worldSystem = systemRegistry.getSystem<WorldSystem>('WorldSystem');

        if (!this.worldSystem) {
            throw new Error('WorldSystem dependency not found');
        }

        // Set up event handlers
        this.on('entity:moved', this.handleEntityMoved.bind(this));
        this.on('patrol:started', this.handlePatrolStarted.bind(this));
        this.on('patrol:completed', this.handlePatrolCompleted.bind(this));
        this.on('entity:teleported', this.handleEntityTeleported.bind(this));
    }

    /**
     * System shutdown
     */
    protected async shutdownSystem(): Promise<void> {
        this.logInfo('Shutting down NavigationSystem');
    }

    /**
     * Create or update an entity's position
     */
    public async setEntityPosition(
        entityId: string,
        mapId: string,
        position: { x: number, y: number },
        direction: number = 0,
        movementState: MovementState = MovementState.IDLE
    ): Promise<EntityPosition> {
        this.logInfo(`Setting position for entity ${entityId} to (${position.x}, ${position.y})`);

        // Check if entity position already exists
        const existingPositions = await this.entityPositionRepository.findBy('entityId', entityId);

        if (existingPositions.length > 0) {
            // Update existing position
            const updated = await this.entityPositionRepository.update(
                existingPositions[0].id,
                {
                    mapId,
                    position,
                    direction,
                    movementState,
                    lastUpdated: Date.now()
                }
            );

            if (updated) {
                await this.emitMovementEvent(updated);
                return updated;
            }

            return existingPositions[0];
        } else {
            // Create new position
            const tile = await this.worldSystem?.getTileAt(position.x, position.y);

            const entityPosition: EntityPosition = {
                ...createBaseEntity(),
                entityId,
                mapId,
                position,
                direction,
                elevation: tile?.elevation || 0,
                movementState,
                lastUpdated: Date.now()
            };

            const created = await this.entityPositionRepository.create(entityPosition);
            await this.emitMovementEvent(created);
            return created;
        }
    }

    /**
     * Get an entity's current position
     */
    public async getEntityPosition(entityId: string): Promise<EntityPosition | null> {
        const positions = await this.entityPositionRepository.findBy('entityId', entityId);
        return positions.length > 0 ? positions[0] : null;
    }

    /**
     * Move an entity in a specific direction
     */
    public async moveEntity(
        entityId: string,
        direction: number,
        distance: number,
        movementType: MovementType = MovementType.WALK,
        movementCapabilities?: MovementCapabilities
    ): Promise<MovementResult> {
        const entityPosition = await this.getEntityPosition(entityId);

        if (!entityPosition) {
            return {
                success: false,
                distanceMoved: 0,
                terrainsCrossed: [],
                staminaUsed: 0,
                message: 'Entity position not found'
            };
        }

        // Calculate destination based on direction and distance
        const radians = direction * Math.PI / 180;
        const targetX = Math.round(entityPosition.position.x + Math.cos(radians) * distance);
        const targetY = Math.round(entityPosition.position.y + Math.sin(radians) * distance);

        // Find path to target
        const pathResult = await this.findPath(
            entityPosition.position.x,
            entityPosition.position.y,
            targetX,
            targetY,
            {
                avoidTerrainTypes: [TerrainType.WATER, TerrainType.MOUNTAIN]
            }
        );

        if (!pathResult.success || pathResult.path.length <= 1) {
            return {
                success: false,
                distanceMoved: 0,
                terrainsCrossed: [],
                staminaUsed: 0,
                message: 'No valid path found'
            };
        }

        // Calculate movement based on capabilities
        const terrainsCrossed: TerrainType[] = [];
        let staminaUsed = 0;
        let actualDistance = 0;

        // If movementCapabilities provided, check stamina
        if (movementCapabilities) {
            const staminaCost = movementCapabilities.staminaCosts[movementType] || 1;
            const maxDistance = Math.floor(movementCapabilities.currentStamina / staminaCost);

            if (maxDistance < 1) {
                return {
                    success: false,
                    distanceMoved: 0,
                    terrainsCrossed: [],
                    staminaUsed: 0,
                    message: 'Insufficient stamina'
                };
            }

            // Limit path based on available stamina
            if (pathResult.path.length > maxDistance + 1) {
                pathResult.path = pathResult.path.slice(0, maxDistance + 1);
            }

            staminaUsed = (pathResult.path.length - 1) * staminaCost;
        }

        // Move along the path and collect terrains crossed
        for (let i = 1; i < pathResult.path.length; i++) {
            const node = pathResult.path[i];
            const tile = await this.worldSystem?.getTileAt(node.x, node.y);

            if (tile) {
                terrainsCrossed.push(tile.terrain);

                // Mark tile as explored
                await this.worldSystem?.exploreTile(node.x, node.y, entityId);
            }

            actualDistance++;
        }

        // Set new position to the final point in the path
        const finalPoint = pathResult.path[pathResult.path.length - 1];

        const updatedPosition = await this.setEntityPosition(
            entityId,
            entityPosition.mapId,
            { x: finalPoint.x, y: finalPoint.y },
            direction,
            MovementState.MOVING
        );

        return {
            success: true,
            newPosition: updatedPosition.position,
            distanceMoved: actualDistance,
            terrainsCrossed,
            staminaUsed
        };
    }

    /**
     * Find a path between two points using A* algorithm
     */
    public async findPath(
        startX: number,
        startY: number,
        goalX: number,
        goalY: number,
        options: PathOptions = {}
    ): Promise<PathResult> {
        this.logInfo(`Finding path from (${startX}, ${startY}) to (${goalX}, ${goalY})`);

        if (!this.worldSystem) {
            return {
                success: false,
                path: [],
                totalCost: 0,
                message: 'World system not available'
            };
        }

        // A* pathfinding algorithm
        const openSet: PathNode[] = [];
        const closedSet: Map<string, PathNode> = new Map();

        // Create start node
        const startNode: PathNode = {
            x: startX,
            y: startY,
            g: 0,
            h: this.heuristic(startX, startY, goalX, goalY),
            f: 0,
            movementCost: 0
        };

        startNode.f = startNode.g + startNode.h;
        openSet.push(startNode);

        while (openSet.length > 0) {
            // Sort by f-value and get the lowest one
            openSet.sort((a, b) => a.f - b.f);
            const current = openSet.shift()!;

            // Check if we reached the goal
            if (current.x === goalX && current.y === goalY) {
                // Reconstruct path
                const path: { x: number, y: number }[] = [];
                let node: PathNode | undefined = current;

                while (node) {
                    path.unshift({ x: node.x, y: node.y });
                    node = node.parent;
                }

                return {
                    success: true,
                    path,
                    totalCost: current.g
                };
            }

            // Add to closed set
            closedSet.set(`${current.x},${current.y}`, current);

            // Check each neighbor
            const neighbors = await this.getNeighbors(current, options);

            for (const neighbor of neighbors) {
                // Skip if in closed set
                if (closedSet.has(`${neighbor.x},${neighbor.y}`)) continue;

                // Calculate tentative g score
                const tentativeG = current.g + neighbor.movementCost;

                // Find if neighbor is in open set
                const openNeighbor = openSet.find(n => n.x === neighbor.x && n.y === neighbor.y);

                if (!openNeighbor) {
                    // New node, add to open set
                    neighbor.g = tentativeG;
                    neighbor.h = this.heuristic(neighbor.x, neighbor.y, goalX, goalY);
                    neighbor.f = neighbor.g + neighbor.h;
                    neighbor.parent = current;
                    openSet.push(neighbor);
                } else if (tentativeG < openNeighbor.g) {
                    // Better path found
                    openNeighbor.g = tentativeG;
                    openNeighbor.f = openNeighbor.g + openNeighbor.h;
                    openNeighbor.parent = current;
                }
            }
        }

        // No path found
        return {
            success: false,
            path: [],
            totalCost: 0,
            message: 'No path found'
        };
    }

    /**
     * Calculate heuristic (estimated distance) between points
     */
    private heuristic(x1: number, y1: number, x2: number, y2: number): number {
        // Manhattan distance
        return Math.abs(x1 - x2) + Math.abs(y1 - y2);
    }

    /**
     * Get valid neighboring tiles
     */
    private async getNeighbors(node: PathNode, options: PathOptions): Promise<PathNode[]> {
        if (!this.worldSystem) return [];

        const neighbors: PathNode[] = [];
        const dirs = [
            { dx: 0, dy: -1 }, // North
            { dx: 1, dy: -1 }, // Northeast
            { dx: 1, dy: 0 },  // East
            { dx: 1, dy: 1 },  // Southeast
            { dx: 0, dy: 1 },  // South
            { dx: -1, dy: 1 }, // Southwest
            { dx: -1, dy: 0 }, // West
            { dx: -1, dy: -1 } // Northwest
        ];

        for (const dir of dirs) {
            const x = node.x + dir.dx;
            const y = node.y + dir.dy;

            const tile = await this.worldSystem.getTileAt(x, y);

            if (!tile) continue;

            // Check if tile is passable
            if (!tile.passable) continue;

            // Check if terrain should be avoided
            if (options.avoidTerrainTypes && options.avoidTerrainTypes.includes(tile.terrain)) {
                continue;
            }

            // Check if movement cost is too high
            if (options.maxMovementCost && tile.movementCost > options.maxMovementCost) {
                continue;
            }

            // Check if unexplored tiles should be ignored
            if (!options.ignoreExploration && !tile.explored) {
                continue;
            }

            // Apply movement cost modifiers
            let movementCost = tile.movementCost;

            // Prefer certain terrain types if specified
            if (options.preferredTerrainTypes && options.preferredTerrainTypes.includes(tile.terrain)) {
                movementCost *= 0.8; // 20% discount for preferred terrain
            }

            // Diagonal movement costs more
            if (dir.dx !== 0 && dir.dy !== 0) {
                movementCost *= 1.4; // Approximately sqrt(2)
            }

            neighbors.push({
                x,
                y,
                g: 0, // Will be calculated in main algorithm
                h: 0, // Will be calculated in main algorithm
                f: 0, // Will be calculated in main algorithm
                movementCost
            });
        }

        return neighbors;
    }

    /**
     * Create a patrol route for an entity
     */
    public async createPatrolRoute(
        entityId: string,
        waypoints: { x: number, y: number }[],
        looping: boolean = true,
        pauseDuration: number = 5000
    ): Promise<PatrolRoute> {
        this.logInfo(`Creating patrol route for entity ${entityId} with ${waypoints.length} waypoints`);

        // Check if entity already has a patrol route
        const existingRoutes = await this.patrolRouteRepository.findBy('entityId', entityId);

        if (existingRoutes.length > 0) {
            // Update existing route
            const updated = await this.patrolRouteRepository.update(
                existingRoutes[0].id,
                {
                    waypoints,
                    looping,
                    currentWaypointIndex: 0,
                    startTime: Date.now(),
                    pauseDuration
                }
            );

            if (updated) {
                await this.emitEvent({
                    type: 'patrol:started',
                    source: this.name,
                    timestamp: Date.now(),
                    data: { route: updated }
                });

                return updated;
            }

            return existingRoutes[0];
        } else {
            // Create new route
            const patrolRoute: PatrolRoute = {
                ...createBaseEntity(),
                entityId,
                waypoints,
                currentWaypointIndex: 0,
                looping,
                startTime: Date.now(),
                pauseDuration
            };

            const created = await this.patrolRouteRepository.create(patrolRoute);

            await this.emitEvent({
                type: 'patrol:started',
                source: this.name,
                timestamp: Date.now(),
                data: { route: created }
            });

            return created;
        }
    }

    /**
     * Get patrol route for an entity
     */
    public async getPatrolRoute(entityId: string): Promise<PatrolRoute | null> {
        const routes = await this.patrolRouteRepository.findBy('entityId', entityId);
        return routes.length > 0 ? routes[0] : null;
    }

    /**
     * Update patrol route's current waypoint
     */
    public async updatePatrolWaypoint(
        entityId: string,
        newIndex: number
    ): Promise<PatrolRoute | null> {
        const route = await this.getPatrolRoute(entityId);
        if (!route) return null;

        // Validate index
        if (newIndex < 0 || newIndex >= route.waypoints.length) {
            this.logWarn(`Invalid waypoint index ${newIndex} for entity ${entityId}`);
            return route;
        }

        // Update waypoint index
        return this.patrolRouteRepository.update(route.id, {
            currentWaypointIndex: newIndex
        });
    }

    /**
     * Get entities at a specific location
     */
    public async getEntitiesAtLocation(
        x: number,
        y: number,
        radius: number = 0
    ): Promise<string[]> {
        if (radius === 0) {
            // Exact position match
            const positions = await this.entityPositionRepository.query(
                pos => pos.position.x === x && pos.position.y === y
            );

            return positions.map(pos => pos.entityId);
        } else {
            // Within radius
            const positions = await this.entityPositionRepository.query(pos => {
                const dx = pos.position.x - x;
                const dy = pos.position.y - y;
                const distanceSquared = dx * dx + dy * dy;
                return distanceSquared <= radius * radius;
            });

            return positions.map(pos => pos.entityId);
        }
    }

    /**
     * Teleport an entity to a new location
     */
    public async teleportEntity(
        entityId: string,
        mapId: string,
        position: { x: number, y: number }
    ): Promise<EntityPosition | null> {
        this.logInfo(`Teleporting entity ${entityId} to (${position.x}, ${position.y})`);

        const entityPosition = await this.getEntityPosition(entityId);

        if (!entityPosition) {
            // Create new position
            return this.setEntityPosition(
                entityId,
                mapId,
                position,
                0,
                MovementState.TELEPORTING
            );
        } else {
            // Update existing position
            const updated = await this.entityPositionRepository.update(
                entityPosition.id,
                {
                    mapId,
                    position,
                    movementState: MovementState.TELEPORTING,
                    lastUpdated: Date.now()
                }
            );

            if (updated) {
                await this.emitEvent({
                    type: 'entity:teleported',
                    source: this.name,
                    timestamp: Date.now(),
                    data: {
                        entityId,
                        from: entityPosition,
                        to: updated
                    }
                });

                // Set the entity back to idle state after teleport
                setTimeout(async () => {
                    await this.entityPositionRepository.update(
                        updated.id,
                        { movementState: MovementState.IDLE }
                    );
                }, 100);

                return updated;
            }

            return entityPosition;
        }
    }

    /**
     * Calculate distance between two positions
     */
    public calculateDistance(
        pos1: { x: number, y: number },
        pos2: { x: number, y: number },
        diagonalMovement: boolean = true
    ): number {
        if (diagonalMovement) {
            // Euclidean distance
            const dx = pos2.x - pos1.x;
            const dy = pos2.y - pos1.y;
            return Math.sqrt(dx * dx + dy * dy);
        } else {
            // Manhattan distance
            return Math.abs(pos2.x - pos1.x) + Math.abs(pos2.y - pos1.y);
        }
    }

    /**
     * Emit movement event
     */
    private async emitMovementEvent(position: EntityPosition): Promise<void> {
        await this.emitEvent({
            type: 'entity:moved',
            source: this.name,
            timestamp: Date.now(),
            data: { position }
        });
    }

    // Event handlers
    private async handleEntityMoved(event: SystemEvent): Promise<void> {
        const { position } = event.data;
        this.logDebug(`Handler: Entity ${position.entityId} moved to (${position.position.x}, ${position.position.y})`);
    }

    private async handlePatrolStarted(event: SystemEvent): Promise<void> {
        const { route } = event.data;
        this.logDebug(`Handler: Patrol started for entity ${route.entityId} with ${route.waypoints.length} waypoints`);
    }

    private async handlePatrolCompleted(event: SystemEvent): Promise<void> {
        const { route } = event.data;
        this.logDebug(`Handler: Patrol completed for entity ${route.entityId}`);
    }

    private async handleEntityTeleported(event: SystemEvent): Promise<void> {
        const { entityId, from, to } = event.data;
        this.logDebug(`Handler: Entity ${entityId} teleported from (${from.position.x}, ${from.position.y}) to (${to.position.x}, ${to.position.y})`);
    }
} 