/**
 * Integrated Systems Test
 * 
 * This script tests the integration of all backend systems working together.
 * Run with: npx ts-node src/core/systems/test/integrated-systems-test.ts
 */

import { systemRegistry, initializeBackendSystems } from '../index';
import { MemorySystem } from '../MemorySystem';
import { RelationshipSystem } from '../RelationshipSystem';
import { InventorySystem } from '../InventorySystem';
import { EconomySystem } from '../EconomySystem';
import { WorldSystem } from '../WorldSystem';
import { NavigationSystem, MovementState } from '../NavigationSystem';
import {
    MemoryType,
    RelationshipType,
    ItemType,
    ItemRarity,
    CurrencyType,
    TerrainType,
    POIType,
    POISize,
    POIStatus,
    MovementType
} from '../DataModels';

async function runIntegratedSystemsTest() {
    console.log('\n----- Starting Integrated Systems Test -----\n');

    // Initialize all systems
    await initializeBackendSystems(true);

    // Wait for all systems to initialize
    await new Promise(resolve => setTimeout(resolve, 500));

    // Get references to all systems
    const memorySystem = systemRegistry.getSystem<MemorySystem>('MemorySystem');
    const relationshipSystem = systemRegistry.getSystem<RelationshipSystem>('RelationshipSystem');
    const inventorySystem = systemRegistry.getSystem<InventorySystem>('InventorySystem');
    const economySystem = systemRegistry.getSystem<EconomySystem>('EconomySystem');
    const worldSystem = systemRegistry.getSystem<WorldSystem>('WorldSystem');
    const navigationSystem = systemRegistry.getSystem<NavigationSystem>('NavigationSystem');

    if (!memorySystem || !relationshipSystem || !inventorySystem ||
        !economySystem || !worldSystem || !navigationSystem) {
        throw new Error('One or more systems failed to initialize');
    }

    console.log('All systems initialized successfully');

    try {
        // Step 1: Create a world and region
        const gameWorld = await worldSystem.generateWorld({
            name: 'Integrated Test World',
            width: 100,
            height: 100,
            seed: 'integrated-test-seed',
            defaultTerrain: TerrainType.PLAIN
        });

        console.log(`Created world: ${gameWorld.name}`);

        // Wait for world generation to complete
        await new Promise(resolve => setTimeout(resolve, 1000));

        const regions = await worldSystem.getRegionsForMap(gameWorld.id);
        console.log(`Generated ${regions.length} regions`);

        if (regions.length === 0) {
            throw new Error('No regions generated');
        }

        const mainRegion = regions[0];
        console.log(`Using region: ${mainRegion.name} (${mainRegion.terrain})`);

        // Step 2: Create NPCs
        const merchant = {
            id: 'npc-merchant',
            name: 'Aldric the Merchant'
        };

        const guardCaptain = {
            id: 'npc-guard',
            name: 'Captain Eliza'
        };

        const player = {
            id: 'player-1',
            name: 'Hero'
        };

        // Step 3: Create relationships between NPCs
        const merchantGuardRelationship = await relationshipSystem.createRelationship(
            merchant.id,
            guardCaptain.id,
            RelationshipType.PROFESSIONAL
        );

        console.log(`Created relationship between ${merchant.name} and ${guardCaptain.name}`);

        // Step 4: Add a memory for the merchant
        const merchantMemory = await memorySystem.createMemory({
            type: MemoryType.INTERACTION,
            ownerEntityId: merchant.id,
            involvedEntityIds: [guardCaptain.id],
            description: `${guardCaptain.name} helped protect my caravan from bandits`,
            details: {
                location: 'Northern Road',
                outcome: 'positive'
            },
            emotionalImpact: 80,
            decayRate: 5,
            importance: 70,
            tags: ['protection', 'gratitude']
        });

        console.log(`Created memory for ${merchant.name}: ${merchantMemory.description}`);

        // Step 5: Place NPCs in the world
        const merchantX = mainRegion.position.x + 10;
        const merchantY = mainRegion.position.y + 10;

        await navigationSystem.setEntityPosition(
            merchant.id,
            gameWorld.id,
            { x: merchantX, y: merchantY },
            0,
            MovementState.IDLE
        );

        const guardX = merchantX + 5;
        const guardY = merchantY;

        await navigationSystem.setEntityPosition(
            guardCaptain.id,
            gameWorld.id,
            { x: guardX, y: guardY },
            270, // Facing west, towards merchant
            MovementState.IDLE
        );

        const playerX = merchantX - 10;
        const playerY = merchantY - 5;

        await navigationSystem.setEntityPosition(
            player.id,
            gameWorld.id,
            { x: playerX, y: playerY },
            45, // Facing northeast
            MovementState.IDLE
        );

        console.log(`Placed NPCs and player in the world`);

        // Step 6: Create a patrol route for the guard
        const guardPatrol = await navigationSystem.createPatrolRoute(
            guardCaptain.id,
            [
                { x: guardX, y: guardY },
                { x: guardX + 10, y: guardY },
                { x: guardX + 10, y: guardY + 10 },
                { x: guardX, y: guardY + 10 }
            ],
            true, // looping
            3000  // pause duration
        );

        console.log(`Created patrol route for ${guardCaptain.name}`);

        // Step 7: Create inventories for all characters
        const merchantInventory = await inventorySystem.createInventory({
            ownerId: merchant.id,
            maxWeight: 200,
            maxSlots: 30
        });

        const guardInventory = await inventorySystem.createInventory({
            ownerId: guardCaptain.id,
            maxWeight: 100,
            maxSlots: 20
        });

        const playerInventory = await inventorySystem.createInventory({
            ownerId: player.id,
            maxWeight: 150,
            maxSlots: 25
        });

        console.log(`Created inventories for all characters`);

        // Step 8: Create items and add to inventories
        const sword = await inventorySystem.createItem({
            name: 'Steel Sword',
            description: 'A well-crafted steel sword',
            type: ItemType.WEAPON,
            rarity: ItemRarity.UNCOMMON,
            weight: 3,
            value: {
                currencies: [{ type: CurrencyType.GOLD, amount: 15 }],
                valueModifier: 1.0
            },
            stackable: false,
            maxStackSize: 1,
            tags: ['weapon', 'steel', 'sword']
        });

        const healthPotion = await inventorySystem.createItem({
            name: 'Health Potion',
            description: 'Restores 50 health points',
            type: ItemType.CONSUMABLE,
            rarity: ItemRarity.COMMON,
            weight: 0.5,
            value: {
                currencies: [{ type: CurrencyType.SILVER, amount: 25 }],
                valueModifier: 1.0
            },
            stackable: true,
            maxStackSize: 10,
            tags: ['potion', 'healing']
        });

        const treasureMap = await inventorySystem.createItem({
            name: 'Treasure Map',
            description: 'A map showing the location of hidden treasure',
            type: ItemType.QUEST,
            rarity: ItemRarity.RARE,
            weight: 0.1,
            value: {
                currencies: [{ type: CurrencyType.GOLD, amount: 5 }],
                valueModifier: 1.0
            },
            stackable: false,
            maxStackSize: 1,
            tags: ['map', 'treasure', 'quest']
        });

        // Add items to inventories
        await inventorySystem.addItemToInventory(merchantInventory.id, healthPotion.id, 5);
        await inventorySystem.addItemToInventory(guardInventory.id, sword.id, 1);
        await inventorySystem.addItemToInventory(playerInventory.id, treasureMap.id, 1);

        console.log(`Created and distributed items`);

        // Step A9: Set up economy data
        await economySystem.setRegionalPrices({
            regionId: mainRegion.id,
            name: mainRegion.name,
            basePriceModifier: 1.0,
            itemTypeModifiers: {
                [ItemType.WEAPON]: 1.1,
                [ItemType.CONSUMABLE]: 0.9
            },
            supplyDemandModifiers: {},
            seasonalModifiers: {}
        });

        const merchantData = await economySystem.createMerchant({
            name: merchant.name,
            regionId: mainRegion.id,
            specialization: 'general',
            buyPriceModifier: 0.5,
            sellPriceModifier: 1.5,
            inventoryIds: [merchantInventory.id],
            restockInterval: 86400000, // 24 hours
            lastRestockTime: Date.now(),
            reputation: 60,
            currencies: [
                { type: CurrencyType.GOLD, amount: 50 },
                { type: CurrencyType.SILVER, amount: 500 },
                { type: CurrencyType.COPPER, amount: 1000 }
            ]
        });

        console.log(`Set up economy data for the region and merchant`);

        // Step 10: Create POI for merchant shop
        const shopPOI = await worldSystem.getPOIsInRegion(mainRegion.id)
            .then(pois => pois.find(poi =>
                poi.position.x === merchantX &&
                poi.position.y === merchantY
            ));

        if (shopPOI) {
            // Update existing POI
            await worldSystem.poiRepository.update(shopPOI.id, {
                name: "Aldric's Trading Post",
                description: "A well-stocked trading post run by Aldric",
                type: POIType.SETTLEMENT,
                size: POISize.SMALL,
                status: POIStatus.VISIBLE,
                inhabitants: [merchant.id, guardCaptain.id],
                tags: ['shop', 'trading_post']
            });
            console.log(`Updated POI for merchant shop`);
        } else {
            // Create new POI
            // Note: We don't directly create a POI here as we would need access to the private repository
            console.log(`No POI found at merchant location to update`);
        }

        // Step 11: Simulate player movement to merchant
        console.log(`Simulating player movement to merchant...`);

        const pathToMerchant = await navigationSystem.findPath(
            playerX, playerY,
            merchantX, merchantY,
            { ignoreExploration: true }
        );

        if (pathToMerchant.success) {
            console.log(`Found path to merchant with ${pathToMerchant.path.length} steps`);

            // Calculate movement to merchant (just move part way)
            const moveSteps = Math.min(5, pathToMerchant.path.length - 1);
            if (moveSteps > 0) {
                const targetPoint = pathToMerchant.path[moveSteps];
                const dx = targetPoint.x - playerX;
                const dy = targetPoint.y - playerY;
                const direction = Math.atan2(dy, dx) * 180 / Math.PI;

                // Move the player
                const moveResult = await navigationSystem.moveEntity(
                    player.id,
                    direction,
                    moveSteps,
                    MovementType.WALK
                );

                if (moveResult.success) {
                    console.log(`Player moved ${moveResult.distanceMoved} steps toward merchant`);
                }
            }
        }

        // Step 12: Create memory of player meeting merchant
        const playerMemory = await memorySystem.createMemory({
            type: MemoryType.INTERACTION,
            ownerEntityId: player.id,
            involvedEntityIds: [merchant.id],
            description: `Met ${merchant.name} at his trading post`,
            details: {
                location: "Aldric's Trading Post",
                items_seen: ['Health Potion']
            },
            emotionalImpact: 30,
            decayRate: 10,
            importance: 40,
            tags: ['merchant', 'shop', 'trading']
        });

        console.log(`Created memory for player meeting merchant`);

        // Step 13: Create relationship between player and merchant
        const playerMerchantRelationship = await relationshipSystem.createRelationship(
            player.id,
            merchant.id,
            RelationshipType.ACQUAINTANCE
        );

        console.log(`Created relationship between player and merchant`);

        // Step 14: Simulate buying a health potion
        // First get current player currencies or add some if none
        let playerCurrency = await inventorySystem.getInventoryCurrencies(playerInventory.id);

        if (playerCurrency.length === 0) {
            // Add some currency for the player
            await inventorySystem.addCurrencyToInventory(
                playerInventory.id,
                { type: CurrencyType.GOLD, amount: 5 },
                { type: CurrencyType.SILVER, amount: 50 }
            );

            playerCurrency = await inventorySystem.getInventoryCurrencies(playerInventory.id);
        }

        console.log(`Player has currency: ${economySystem.formatCurrencies(playerCurrency)}`);

        // Simulate purchasing a health potion
        const healthPotionPrice = await economySystem.calculatePrice({
            baseValue: healthPotion.value,
            regionId: mainRegion.id,
            merchantId: merchantData.id,
            playerReputation: 50,
            isBuying: false // Player is buying from merchant
        });

        console.log(`Health potion price: ${economySystem.formatCurrencies(healthPotionPrice.currencies)}`);

        // Transfer the item (simplified version of what would happen in a trade)
        const transferResult = await inventorySystem.transferItem(
            merchantInventory.id,
            playerInventory.id,
            healthPotion.id,
            1
        );

        if (transferResult) {
            console.log(`Player purchased a health potion from the merchant`);

            // Add a memory of the transaction
            await memorySystem.createMemory({
                type: MemoryType.TRADE,
                ownerEntityId: merchant.id,
                involvedEntityIds: [player.id],
                description: `Sold a health potion to ${player.name}`,
                details: {
                    item: healthPotion.name,
                    price: healthPotionPrice.currencies
                },
                emotionalImpact: 10,
                decayRate: 20,
                importance: 20,
                tags: ['sale', 'potion']
            });
        }

        // Step 15: Print final state summary
        console.log('\n----- System State Summary -----');

        // World summary
        const allPOIs = await worldSystem.getPOIsInRegion(mainRegion.id);
        console.log(`World contains ${regions.length} regions and ${allPOIs.length} POIs`);

        // Character positions
        const merchantPos = await navigationSystem.getEntityPosition(merchant.id);
        const guardPos = await navigationSystem.getEntityPosition(guardCaptain.id);
        const playerPos = await navigationSystem.getEntityPosition(player.id);

        console.log(`Character positions:`);
        console.log(`- ${merchant.name}: (${merchantPos?.position.x}, ${merchantPos?.position.y})`);
        console.log(`- ${guardCaptain.name}: (${guardPos?.position.x}, ${guardPos?.position.y})`);
        console.log(`- ${player.name}: (${playerPos?.position.x}, ${playerPos?.position.y})`);

        // Inventory summary
        const merchantItems = await inventorySystem.getInventoryItems(merchantInventory.id);
        const playerItems = await inventorySystem.getInventoryItems(playerInventory.id);

        console.log(`Merchant inventory: ${merchantItems.length} items`);
        console.log(`Player inventory: ${playerItems.length} items`);

        // Memory summary
        const merchantMemories = await memorySystem.getMemoriesForEntity(merchant.id);
        const playerMemories = await memorySystem.getMemoriesForEntity(player.id);

        console.log(`Merchant has ${merchantMemories.length} memories`);
        console.log(`Player has ${playerMemories.length} memories`);

        // Relationship summary
        const merchantRelationships = await relationshipSystem.getRelationshipsForEntity(merchant.id);
        console.log(`Merchant has ${merchantRelationships.length} relationships`);

        console.log('\n----- Integrated Systems Test Complete -----\n');
    } catch (error) {
        console.error('Test failed with error:', error);
    }
}

// Run the test
runIntegratedSystemsTest().catch(error => {
    console.error('Test failed with error:', error);
}); 