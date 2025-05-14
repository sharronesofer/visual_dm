/**
 * Economy System Test
 * 
 * This script tests the functionality of the Economy System.
 * Run with: npx ts-node src/core/systems/test/economy-system-test.ts
 */

import { EconomySystem } from '../EconomySystem';
import { InventorySystem } from '../InventorySystem';
import {
    CurrencyType,
    EconomicValue,
    ItemRarity,
    ItemType
} from '../DataModels';
import { systemRegistry } from '../BaseSystemManager';

async function runEconomySystemTest() {
    console.log('\n----- Starting Economy System Test -----\n');

    // Create and initialize systems
    const economySystem = new EconomySystem({
        name: 'EconomySystem',
        debug: true,
        autoInitialize: true
    });

    const inventorySystem = new InventorySystem({
        name: 'InventorySystem',
        debug: true,
        autoInitialize: true
    });

    // Register the systems
    systemRegistry.registerSystem(economySystem);
    systemRegistry.registerSystem(inventorySystem);

    // Wait for initialization
    await new Promise(resolve => setTimeout(resolve, 100));

    // Create a region with price data
    const northRegion = await economySystem.setRegionalPrices({
        regionId: 'north',
        name: 'Northern Kingdom',
        basePriceModifier: 1.2, // More expensive region
        itemTypeModifiers: {
            [ItemType.WEAPON]: 1.1,
            [ItemType.ARMOR]: 0.9,
            [ItemType.CONSUMABLE]: 1.5
        },
        supplyDemandModifiers: {
            'iron': 0.8, // Common
            'silk': 1.3, // Rare
        },
        seasonalModifiers: {
            'winter': {
                'default': 1.2,
                [ItemType.CONSUMABLE]: 1.5
            },
            'summer': {
                'default': 0.9,
                'clothing': 1.2
            }
        }
    });

    console.log('Created region with price data:', northRegion.name);

    // Create a merchant
    const blacksmith = await economySystem.createMerchant({
        name: 'Grimhammer Forge',
        regionId: 'north',
        specialization: 'blacksmith',
        buyPriceModifier: 0.4, // Pays less when buying from player
        sellPriceModifier: 1.6, // Charges more when selling to player
        inventoryIds: [],
        restockInterval: 86400000, // 24 hours
        lastRestockTime: Date.now(),
        reputation: 60,
        currencies: [
            { type: CurrencyType.GOLD, amount: 200 },
            { type: CurrencyType.SILVER, amount: 1500 },
            { type: CurrencyType.COPPER, amount: 8000 }
        ]
    });

    console.log('Created merchant:', blacksmith.name);

    // Create inventory for the merchant
    const merchantInventory = await inventorySystem.createInventory({
        ownerId: blacksmith.id,
        maxWeight: 500,
        maxSlots: 50
    });

    console.log('Created merchant inventory');

    // Update merchant inventory IDs
    // We need to modify this since merchantRepository is private
    // Instead of directy access, we'll create an updated merchant
    await economySystem.createMerchant({
        ...blacksmith,
        inventoryIds: [merchantInventory.id]
    });

    // Create a player inventory
    const playerInventory = await inventorySystem.createInventory({
        ownerId: 'player1',
        maxWeight: 100,
        maxSlots: 20
    });

    console.log('Created player inventory');

    // Create some items
    const sword = await inventorySystem.createItem({
        name: 'Steel Longsword',
        description: 'A sturdy steel longsword',
        type: ItemType.WEAPON,
        rarity: ItemRarity.UNCOMMON,
        weight: 3.5,
        value: {
            currencies: [
                { type: CurrencyType.GOLD, amount: 12 },
                { type: CurrencyType.SILVER, amount: 50 }
            ],
            valueModifier: 1.0
        },
        stackable: false
    });

    const potion = await inventorySystem.createItem({
        name: 'Health Potion',
        description: 'Restores 50 health',
        type: ItemType.CONSUMABLE,
        rarity: ItemRarity.COMMON,
        weight: 0.2,
        value: {
            currencies: [
                { type: CurrencyType.SILVER, amount: 25 }
            ],
            valueModifier: 1.0
        },
        stackable: true,
        maxStackSize: 10
    });

    const ore = await inventorySystem.createItem({
        name: 'Iron Ore',
        description: 'Raw iron ore',
        type: ItemType.MATERIAL,
        rarity: ItemRarity.COMMON,
        weight: 2.0,
        value: {
            currencies: [
                { type: CurrencyType.SILVER, amount: 15 }
            ],
            valueModifier: 1.0
        },
        stackable: true,
        maxStackSize: 20,
        tags: ['iron', 'ore', 'metal']
    });

    console.log('Created items:', sword.name, potion.name, ore.name);

    // Add items to inventories
    await inventorySystem.addItemToInventory(merchantInventory.id, sword.id, 1);
    await inventorySystem.addItemToInventory(merchantInventory.id, potion.id, 5);
    await inventorySystem.addItemToInventory(playerInventory.id, ore.id, 10);

    console.log('Added items to inventories');

    // Test price calculation
    const standardPrice = await economySystem.calculatePrice({
        baseValue: sword.value
    });

    const regionPrice = await economySystem.calculatePrice({
        baseValue: sword.value,
        regionId: 'north'
    });

    const merchantBuyPrice = await economySystem.calculatePrice({
        baseValue: ore.value,
        regionId: 'north',
        merchantId: blacksmith.id,
        playerReputation: 75,
        isBuying: true
    });

    const merchantSellPrice = await economySystem.calculatePrice({
        baseValue: sword.value,
        regionId: 'north',
        merchantId: blacksmith.id,
        playerReputation: 75,
        isBuying: false
    });

    console.log('Standard price:', economySystem.formatCurrencies(standardPrice.currencies));
    console.log('Regional price:', economySystem.formatCurrencies(regionPrice.currencies));
    console.log('Merchant buy price:', economySystem.formatCurrencies(merchantBuyPrice.currencies));
    console.log('Merchant sell price:', economySystem.formatCurrencies(merchantSellPrice.currencies));

    // Test currency breakdowns
    const gold = { type: CurrencyType.GOLD, amount: 3 };
    const brokenDown = economySystem.breakdownCurrency(gold);
    console.log('Breaking down 3 gold:', economySystem.formatCurrencies(brokenDown));

    // Test currency combination
    const combined = economySystem.combineCurrencies([
        { type: CurrencyType.GOLD, amount: 2 },
        { type: CurrencyType.SILVER, amount: 150 },
        { type: CurrencyType.COPPER, amount: 75 },
        { type: CurrencyType.GOLD, amount: 1 }
    ]);
    console.log('Combined currencies:', economySystem.formatCurrencies(combined));

    // Calculate inventory values
    const merchantInventoryValue = await inventorySystem.calculateInventoryValue(merchantInventory.id);
    const playerInventoryValue = await inventorySystem.calculateInventoryValue(playerInventory.id);

    console.log('Merchant inventory value:', economySystem.formatCurrencies(merchantInventoryValue.currencies));
    console.log('Player inventory value:', economySystem.formatCurrencies(playerInventoryValue.currencies));

    console.log('\n----- Economy System Test Complete -----\n');
}

// Run the test
runEconomySystemTest().catch(error => {
    console.error('Test failed with error:', error);
}); 