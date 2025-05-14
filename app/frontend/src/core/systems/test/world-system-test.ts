/**
 * World System Test
 * 
 * This script tests the functionality of the World System.
 * Run with: npx ts-node src/core/systems/test/world-system-test.ts
 */

import { WorldSystem } from '../WorldSystem';
import { POIStatus, TerrainType } from '../DataModels';
import { systemRegistry } from '../BaseSystemManager';

async function runWorldSystemTest() {
    console.log('\n----- Starting World System Test -----\n');

    // Create and initialize world system
    const worldSystem = new WorldSystem({
        name: 'WorldSystem',
        debug: true,
        autoInitialize: true
    });

    // Register the system
    systemRegistry.registerSystem(worldSystem);

    // Wait for initialization
    await new Promise(resolve => setTimeout(resolve, 100));

    // Generate a small test world
    const testWorld = await worldSystem.generateWorld({
        name: 'Test World',
        width: 50,
        height: 50,
        seed: 'test-seed-123',
        roughness: 0.5,
        defaultTerrain: TerrainType.PLAIN,
        regionDensity: 0.2,
        poiDensity: 0.1
    });

    console.log(`Generated world: ${testWorld.name} (${testWorld.width}x${testWorld.height})`);

    // Wait for generation to complete
    console.log('Waiting for world generation to complete...');
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Get regions for the world
    const regions = await worldSystem.getRegionsForMap(testWorld.id);
    console.log(`Generated ${regions.length} regions`);

    // Check a few tiles in different regions
    if (regions.length > 0) {
        const region = regions[0];
        console.log(`Examining region: ${region.name} (${region.terrain})`);

        // Get tiles at the center of the region
        const centerX = region.position.x + Math.floor(region.size.width / 2);
        const centerY = region.position.y + Math.floor(region.size.height / 2);

        const centerTile = await worldSystem.getTileAt(centerX, centerY);
        console.log(`Center tile at (${centerX}, ${centerY}): `,
            centerTile ? `Terrain: ${centerTile.terrain}, Passable: ${centerTile.passable}` : 'Not found');

        // Get nearby tiles
        const nearbyTiles = await worldSystem.getTilesInArea(centerX, centerY, 3);
        console.log(`Found ${nearbyTiles.length} tiles within radius 3 of center`);

        // Explore a tile
        if (centerTile) {
            await worldSystem.exploreTile(centerX, centerY, 'test-player');
            const updatedTile = await worldSystem.getTileAt(centerX, centerY);
            console.log(`Explored center tile: ${updatedTile?.explored}`);
        }

        // Get POIs in the region
        const pois = await worldSystem.getPOIsInRegion(region.id);
        console.log(`Region has ${pois.length} POIs`);

        // Discover a POI if any exist
        if (pois.length > 0) {
            const poi = pois[0];
            console.log(`POI before discovery: ${poi.name}, Status: ${poi.status}`);

            await worldSystem.discoverPOI(poi.id, 'test-player');

            const updatedPoi = await worldSystem.getPOI(poi.id);
            console.log(`POI after discovery: ${updatedPoi?.name}, Status: ${updatedPoi?.status}`);

            // Visit the POI
            await worldSystem.visitPOI(poi.id, 'test-player');

            const visitedPoi = await worldSystem.getPOI(poi.id);
            console.log(`POI after visit: ${visitedPoi?.name}, Status: ${visitedPoi?.status}`);
        }
    }

    console.log('\n----- World System Test Complete -----\n');
}

// Run the test
runWorldSystemTest().catch(error => {
    console.error('Test failed with error:', error);
}); 