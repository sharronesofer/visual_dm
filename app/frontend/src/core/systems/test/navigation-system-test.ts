/**
 * Navigation System Test
 * 
 * This script tests the functionality of the Navigation System.
 * Run with: npx ts-node src/core/systems/test/navigation-system-test.ts
 */

import { NavigationSystem, MovementState } from '../NavigationSystem';
import { WorldSystem } from '../WorldSystem';
import { MovementType, TerrainType } from '../DataModels';
import { systemRegistry } from '../BaseSystemManager';

async function runNavigationSystemTest() {
    console.log('\n----- Starting Navigation System Test -----\n');

    // Create and initialize world system (required for navigation)
    const worldSystem = new WorldSystem({
        name: 'WorldSystem',
        debug: true,
        autoInitialize: true
    });

    // Register the world system
    systemRegistry.registerSystem(worldSystem);

    // Wait for initialization
    await new Promise(resolve => setTimeout(resolve, 100));

    // Create and initialize navigation system
    const navigationSystem = new NavigationSystem({
        name: 'NavigationSystem',
        debug: true,
        autoInitialize: true
    });

    // Register the navigation system
    systemRegistry.registerSystem(navigationSystem);

    // Wait for initialization
    await new Promise(resolve => setTimeout(resolve, 100));

    // Generate a small test world
    const testWorld = await worldSystem.generateWorld({
        name: 'Navigation Test World',
        width: 50,
        height: 50,
        seed: 'nav-test-seed-123',
        defaultTerrain: TerrainType.PLAIN
    });

    console.log(`Generated world: ${testWorld.name} (${testWorld.width}x${testWorld.height})`);

    // Wait for generation to complete
    console.log('Waiting for world generation to complete...');
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Get regions for the world
    const regions = await worldSystem.getRegionsForMap(testWorld.id);
    console.log(`Generated ${regions.length} regions`);

    if (regions.length > 0) {
        const region = regions[0];
        console.log(`Using region: ${region.name} for navigation tests`);

        // Place an entity in the world
        const startX = region.position.x + 5;
        const startY = region.position.y + 5;

        const entityPosition = await navigationSystem.setEntityPosition(
            'test-entity',
            testWorld.id,
            { x: startX, y: startY },
            0, // Direction
            MovementState.IDLE
        );

        console.log(`Placed entity at position: (${entityPosition.position.x}, ${entityPosition.position.y})`);

        // Define a destination within the region
        const destX = region.position.x + region.size.width - 5;
        const destY = region.position.y + region.size.height - 5;

        console.log(`Destination set to: (${destX}, ${destY})`);

        // Find a path to the destination
        const pathResult = await navigationSystem.findPath(
            startX,
            startY,
            destX,
            destY,
            {
                avoidTerrainTypes: [TerrainType.WATER, TerrainType.MOUNTAIN],
                ignoreExploration: true
            }
        );

        if (pathResult.success) {
            console.log(`Path found with ${pathResult.path.length} steps and total cost: ${pathResult.totalCost}`);
            console.log(`First few steps: ${JSON.stringify(pathResult.path.slice(0, 5))}`);
            console.log(`Last few steps: ${JSON.stringify(pathResult.path.slice(-5))}`);
        } else {
            console.log(`Path finding failed: ${pathResult.message}`);
        }

        // Move the entity along the path
        if (pathResult.success && pathResult.path.length > 1) {
            // Calculate direction to the first waypoint
            const firstWaypoint = pathResult.path[1];
            const dx = firstWaypoint.x - startX;
            const dy = firstWaypoint.y - startY;
            const direction = Math.atan2(dy, dx) * 180 / Math.PI;

            // Define movement capabilities
            const movementCapabilities = {
                types: [MovementType.WALK, MovementType.RUN],
                speeds: {
                    [MovementType.WALK]: 1,
                    [MovementType.RUN]: 2,
                    [MovementType.SWIM]: 0.5,
                    [MovementType.FLY]: 0,
                    [MovementType.TELEPORT]: 0,
                    [MovementType.CLIMB]: 0.5
                },
                terrainPenalties: {
                    [TerrainType.PLAIN]: 1,
                    [TerrainType.FOREST]: 1.5,
                    [TerrainType.MOUNTAIN]: 3,
                    [TerrainType.WATER]: 4,
                    [TerrainType.SWAMP]: 2,
                    [TerrainType.DESERT]: 1.5,
                    [TerrainType.SNOW]: 2,
                    [TerrainType.URBAN]: 1
                },
                maxStamina: 100,
                currentStamina: 100,
                staminaRegenRate: 5,
                staminaCosts: {
                    [MovementType.WALK]: 1,
                    [MovementType.RUN]: 3,
                    [MovementType.SWIM]: 5,
                    [MovementType.FLY]: 2,
                    [MovementType.TELEPORT]: 20,
                    [MovementType.CLIMB]: 7
                }
            };

            // Move entity up to 10 spaces
            const moveResult = await navigationSystem.moveEntity(
                'test-entity',
                direction,
                10,
                MovementType.WALK,
                movementCapabilities
            );

            if (moveResult.success) {
                console.log(`Entity moved ${moveResult.distanceMoved} spaces to ${JSON.stringify(moveResult.newPosition)}`);
                console.log(`Terrain types crossed: ${moveResult.terrainsCrossed.join(', ')}`);
                console.log(`Stamina used: ${moveResult.staminaUsed}`);

                // Get updated position
                const updatedPosition = await navigationSystem.getEntityPosition('test-entity');
                console.log(`Updated entity position: ${JSON.stringify(updatedPosition?.position)}`);
            } else {
                console.log(`Movement failed: ${moveResult.message}`);
            }
        }

        // Create a patrol route
        const waypoints = [
            { x: startX, y: startY },
            { x: startX + 10, y: startY },
            { x: startX + 10, y: startY + 10 },
            { x: startX, y: startY + 10 }
        ];

        const patrolRoute = await navigationSystem.createPatrolRoute(
            'test-entity',
            waypoints,
            true, // looping
            2000 // pause duration
        );

        console.log(`Created patrol route with ${patrolRoute.waypoints.length} waypoints`);

        // Update patrol waypoint
        const updatedRoute = await navigationSystem.updatePatrolWaypoint('test-entity', 1);
        console.log(`Updated patrol route to waypoint index: ${updatedRoute?.currentWaypointIndex}`);

        // Find entities at location
        const nearbyEntities = await navigationSystem.getEntitiesAtLocation(
            entityPosition.position.x,
            entityPosition.position.y,
            5 // radius
        );

        console.log(`Found ${nearbyEntities.length} entities near position`);

        // Test teleportation
        const teleportResult = await navigationSystem.teleportEntity(
            'test-entity',
            testWorld.id,
            { x: destX, y: destY }
        );

        console.log(`Teleported entity to: ${JSON.stringify(teleportResult?.position)}`);
    }

    console.log('\n----- Navigation System Test Complete -----\n');
}

// Run the test
runNavigationSystemTest().catch(error => {
    console.error('Test failed with error:', error);
}); 