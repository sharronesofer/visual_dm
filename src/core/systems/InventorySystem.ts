/**
 * InventorySystem.ts
 * 
 * Implements a comprehensive inventory management system for tracking items,
 * stacking, weight calculations, categories, and limitations.
 */

import { BaseSystemManager, SystemConfig, SystemEvent } from './BaseSystemManager';
import { Repository } from './DatabaseLayer';
import {
    BaseEntity,
    Item,
    ItemType,
    ItemRarity,
    Inventory,
    InventorySlot,
    EconomicValue,
    Currency,
    CurrencyType,
    createBaseEntity
} from './DataModels';

// Additional interfaces needed for the inventory system
export interface InventoryCreateParams {
    ownerId: string;
    maxWeight?: number;
    maxSlots?: number;
}

export interface ItemCreateParams {
    name: string;
    description: string;
    type: ItemType;
    rarity: ItemRarity;
    weight: number;
    value: EconomicValue;
    stackable: boolean;
    maxStackSize?: number;
    quantity?: number;
    properties?: Record<string, any>;
    requiredLevel?: number;
    iconId?: string;
    tags?: string[];
}

export interface AddItemResult {
    success: boolean;
    message: string;
    inventory: Inventory | null;
    item: Item | null;
    slot: InventorySlot | null;
}

export interface RemoveItemResult {
    success: boolean;
    message: string;
    inventory: Inventory | null;
    removedItem: Item | null;
    quantity: number;
}

export interface InventoryQueryParams {
    ownerId?: string;
    itemType?: ItemType;
    itemRarity?: ItemRarity;
    itemTags?: string[];
    weightLimit?: { min?: number; max?: number };
    hasRoom?: boolean;
}

/**
 * InventorySystem manages all inventory-related operations
 */
export class InventorySystem extends BaseSystemManager {
    private inventoryRepository: Repository<Inventory>;
    private itemRepository: Repository<Item>;
    private refundQueue: { [ownerId: string]: { [material: string]: number } } = {};

    constructor(config: SystemConfig) {
        super({
            ...config,
            name: config.name || 'InventorySystem'
        });
    }

    /**
     * Initialize inventory repositories
     */
    protected async initializeRepositories(): Promise<void> {
        // Create repositories with indexed fields for performance
        this.inventoryRepository = this.createRepository<Inventory>(
            'inventories',
            ['ownerId']
        );

        this.itemRepository = this.createRepository<Item>(
            'items',
            ['type', 'rarity', 'name', 'stackable']
        );
    }

    /**
     * Initialize system-specific functionality
     */
    protected async initializeSystem(): Promise<void> {
        // Register event handlers
        this.on('item:created', this.handleItemCreated.bind(this));
        this.on('item:removed', this.handleItemRemoved.bind(this));
        this.on('inventory:created', this.handleInventoryCreated.bind(this));
    }

    /**
     * System shutdown
     */
    protected async shutdownSystem(): Promise<void> {
        // Perform any cleanup if needed
        this.logInfo('Shutting down InventorySystem');
    }

    /**
     * Create a new inventory for an entity
     */
    public async createInventory(params: InventoryCreateParams): Promise<Inventory> {
        this.logInfo(`Creating inventory for owner: ${params.ownerId}`);

        // Check if an inventory already exists for this owner
        const existingInventories = await this.inventoryRepository.findBy('ownerId', params.ownerId);
        if (existingInventories.length > 0) {
            this.logWarn(`Inventory already exists for owner ${params.ownerId}, returning existing`);
            return existingInventories[0];
        }

        // Create a new inventory entity
        const inventory = await this.inventoryRepository.create({
            ownerId: params.ownerId,
            slots: [],
            maxWeight: params.maxWeight || 100, // Default weight limit
            maxSlots: params.maxSlots || 20,    // Default slot limit
            currentWeight: 0
        });

        // Initialize empty slots
        const slots: InventorySlot[] = [];
        for (let i = 0; i < inventory.maxSlots; i++) {
            slots.push({
                id: `${inventory.id}_slot_${i}`,
                itemId: null,
                quantity: 0
            });
        }

        // Update the inventory with initialized slots
        const updatedInventory = await this.inventoryRepository.update(inventory.id, { slots });

        // Emit event for inventory creation
        await this.emitEvent({
            type: 'inventory:created',
            source: this.name,
            timestamp: Date.now(),
            data: { inventory: updatedInventory }
        });

        return updatedInventory || inventory;
    }

    /**
     * Create a new item
     */
    public async createItem(params: ItemCreateParams): Promise<Item> {
        this.logInfo(`Creating item: ${params.name} (${params.type})`);

        const item = await this.itemRepository.create({
            name: params.name,
            description: params.description,
            type: params.type,
            rarity: params.rarity,
            weight: params.weight,
            value: params.value,
            stackable: params.stackable,
            maxStackSize: params.maxStackSize || (params.stackable ? 99 : 1),
            quantity: params.quantity || 1,
            properties: params.properties || {},
            requiredLevel: params.requiredLevel,
            iconId: params.iconId,
            tags: params.tags || []
        });

        // Emit event for item creation
        await this.emitEvent({
            type: 'item:created',
            source: this.name,
            timestamp: Date.now(),
            data: { item }
        });

        return item;
    }

    /**
     * Add an item to an inventory
     */
    public async addItemToInventory(
        inventoryId: string,
        itemId: string,
        quantity: number = 1
    ): Promise<AddItemResult> {
        this.logInfo(`Adding item ${itemId} (qty: ${quantity}) to inventory ${inventoryId}`);

        // Validate inputs
        if (quantity <= 0) {
            return {
                success: false,
                message: `Invalid quantity: ${quantity}`,
                inventory: null,
                item: null,
                slot: null
            };
        }

        // Get inventory and item
        const inventory = await this.inventoryRepository.findById(inventoryId);
        const item = await this.itemRepository.findById(itemId);

        if (!inventory) {
            return {
                success: false,
                message: `Inventory not found: ${inventoryId}`,
                inventory: null,
                item: null,
                slot: null
            };
        }

        if (!item) {
            return {
                success: false,
                message: `Item not found: ${itemId}`,
                inventory: null,
                item: null,
                slot: null
            };
        }

        // Calculate weight impact
        const weightImpact = item.weight * quantity;
        if (inventory.currentWeight + weightImpact > inventory.maxWeight) {
            return {
                success: false,
                message: `Adding this item would exceed inventory weight limit`,
                inventory,
                item,
                slot: null
            };
        }

        // Check if item is stackable and exists in inventory
        if (item.stackable) {
            // Find a slot with the same item type and available stack space
            for (const slot of inventory.slots) {
                if (slot.itemId === itemId && slot.quantity < item.maxStackSize) {
                    // Can stack with existing item
                    const availableSpace = item.maxStackSize - slot.quantity;
                    const addQuantity = Math.min(quantity, availableSpace);

                    // Update the slot
                    slot.quantity += addQuantity;

                    // Update the inventory weight
                    inventory.currentWeight += item.weight * addQuantity;

                    // If we still have items left to add and there was not enough space in this stack
                    if (addQuantity < quantity) {
                        // Try to add the remaining items recursively to a new slot
                        const remainingQuantity = quantity - addQuantity;
                        const partialResult = await this.addItemToInventory(
                            inventoryId,
                            itemId,
                            remainingQuantity
                        );

                        if (!partialResult.success) {
                            // If we couldn't add all items, revert the ones we just added
                            slot.quantity -= addQuantity;
                            inventory.currentWeight -= item.weight * addQuantity;
                            return {
                                success: false,
                                message: `Could only add ${addQuantity} items. Remaining failed: ${partialResult.message}`,
                                inventory,
                                item,
                                slot
                            };
                        }
                    }

                    // Update the inventory
                    const updatedInventory = await this.inventoryRepository.update(
                        inventory.id,
                        {
                            slots: inventory.slots,
                            currentWeight: inventory.currentWeight
                        }
                    );

                    return {
                        success: true,
                        message: `Added ${addQuantity} ${item.name} to existing stack`,
                        inventory: updatedInventory || inventory,
                        item,
                        slot
                    };
                }
            }
        }

        // If the item is not stackable or no existing stack was found, find an empty slot
        const emptySlotIndex = inventory.slots.findIndex(slot => slot.itemId === null);
        if (emptySlotIndex === -1) {
            return {
                success: false,
                message: `No available inventory slots`,
                inventory,
                item,
                slot: null
            };
        }

        // Prepare quantity for the new slot
        const slotQuantity = item.stackable ? Math.min(quantity, item.maxStackSize) : 1;

        // Update the slot
        const slot = inventory.slots[emptySlotIndex];
        slot.itemId = item.id;
        slot.quantity = slotQuantity;

        // Update inventory weight
        inventory.currentWeight += item.weight * slotQuantity;

        // If this is a stackable item and we couldn't fit all in one slot
        if (item.stackable && slotQuantity < quantity) {
            // Try to add the remaining items recursively
            const remainingQuantity = quantity - slotQuantity;
            const partialResult = await this.addItemToInventory(
                inventoryId,
                itemId,
                remainingQuantity
            );

            if (!partialResult.success) {
                // If we couldn't add all items, revert the ones we just added
                slot.itemId = null;
                slot.quantity = 0;
                inventory.currentWeight -= item.weight * slotQuantity;
                return {
                    success: false,
                    message: `Could only add ${slotQuantity} items. Remaining failed: ${partialResult.message}`,
                    inventory,
                    item,
                    slot
                };
            }
        }

        // Update the inventory
        const updatedInventory = await this.inventoryRepository.update(
            inventory.id,
            {
                slots: inventory.slots,
                currentWeight: inventory.currentWeight
            }
        );

        return {
            success: true,
            message: `Added ${slotQuantity} ${item.name} to inventory`,
            inventory: updatedInventory || inventory,
            item,
            slot
        };
    }

    /**
     * Remove an item from an inventory
     */
    public async removeItemFromInventory(
        inventoryId: string,
        itemId: string,
        quantity: number = 1
    ): Promise<RemoveItemResult> {
        this.logInfo(`Removing item ${itemId} (qty: ${quantity}) from inventory ${inventoryId}`);

        // Validate inputs
        if (quantity <= 0) {
            return {
                success: false,
                message: `Invalid quantity: ${quantity}`,
                inventory: null,
                removedItem: null,
                quantity: 0
            };
        }

        // Get inventory and item
        const inventory = await this.inventoryRepository.findById(inventoryId);
        const item = await this.itemRepository.findById(itemId);

        if (!inventory) {
            return {
                success: false,
                message: `Inventory not found: ${inventoryId}`,
                inventory: null,
                removedItem: null,
                quantity: 0
            };
        }

        if (!item) {
            return {
                success: false,
                message: `Item not found: ${itemId}`,
                inventory: null,
                removedItem: null,
                quantity: 0
            };
        }

        // Find all slots with this item
        const slotsWithItem = inventory.slots.filter(slot => slot.itemId === itemId);
        if (slotsWithItem.length === 0) {
            return {
                success: false,
                message: `Item not found in inventory`,
                inventory,
                removedItem: null,
                quantity: 0
            };
        }

        // Calculate total available quantity
        const totalAvailable = slotsWithItem.reduce((sum, slot) => sum + slot.quantity, 0);
        if (totalAvailable < quantity) {
            return {
                success: false,
                message: `Not enough items in inventory. Requested: ${quantity}, Available: ${totalAvailable}`,
                inventory,
                removedItem: item,
                quantity: 0
            };
        }

        // Keep track of remaining quantity to remove
        let remainingToRemove = quantity;
        let totalRemoved = 0;

        // Start removing from slots, beginning with partially filled stacks
        const sortedSlots = [...slotsWithItem].sort((a, b) => a.quantity - b.quantity);

        for (const slot of sortedSlots) {
            if (remainingToRemove <= 0) break;

            const slotIndex = inventory.slots.findIndex(s => s.id === slot.id);
            if (slotIndex === -1) continue;

            const removeFromSlot = Math.min(slot.quantity, remainingToRemove);

            // Update inventory weight
            inventory.currentWeight -= item.weight * removeFromSlot;

            // Update slot
            if (removeFromSlot === slot.quantity) {
                // Remove entire slot
                inventory.slots[slotIndex].itemId = null;
                inventory.slots[slotIndex].quantity = 0;
            } else {
                // Remove partial
                inventory.slots[slotIndex].quantity -= removeFromSlot;
            }

            remainingToRemove -= removeFromSlot;
            totalRemoved += removeFromSlot;
        }

        // Update the inventory
        const updatedInventory = await this.inventoryRepository.update(
            inventory.id,
            {
                slots: inventory.slots,
                currentWeight: inventory.currentWeight
            }
        );

        // Emit event for item removal
        await this.emitEvent({
            type: 'item:removed',
            source: this.name,
            timestamp: Date.now(),
            data: {
                inventoryId,
                itemId,
                quantity: totalRemoved
            }
        });

        return {
            success: true,
            message: `Removed ${totalRemoved} ${item.name} from inventory`,
            inventory: updatedInventory || inventory,
            removedItem: item,
            quantity: totalRemoved
        };
    }

    /**
     * Get all items in an inventory
     */
    public async getInventoryItems(inventoryId: string): Promise<{ items: Item[], slots: InventorySlot[] }> {
        this.logInfo(`Getting items for inventory ${inventoryId}`);

        const inventory = await this.inventoryRepository.findById(inventoryId);
        if (!inventory) {
            throw new Error(`Inventory not found: ${inventoryId}`);
        }

        // Get all unique item IDs in the inventory
        const itemIds = inventory.slots
            .filter(slot => slot.itemId !== null)
            .map(slot => slot.itemId as string);

        // Remove duplicates
        const uniqueItemIds = [...new Set(itemIds)];

        // Get all items data
        const items = await this.itemRepository.findByIds(uniqueItemIds);

        return {
            items,
            slots: inventory.slots
        };
    }

    /**
     * Query inventories based on various parameters
     */
    public async queryInventories(params: InventoryQueryParams): Promise<Inventory[]> {
        this.logInfo('Querying inventories with params:', params);

        let inventories = await this.inventoryRepository.findAll();

        // Filter by owner ID if provided
        if (params.ownerId) {
            inventories = inventories.filter(inv => inv.ownerId === params.ownerId);
        }

        // Filter by weight limit if provided
        if (params.weightLimit) {
            const weightLimit = params.weightLimit;

            // Check min weight if defined
            if (weightLimit.min !== undefined) {
                inventories = inventories.filter(inv => inv.currentWeight >= weightLimit.min!);
            }

            // Check max weight if defined
            if (weightLimit.max !== undefined) {
                inventories = inventories.filter(inv => inv.currentWeight <= weightLimit.max!);
            }
        }

        // Filter by whether the inventory has room
        if (params.hasRoom !== undefined) {
            inventories = inventories.filter(inv => {
                const hasEmptySlot = inv.slots.some(slot => slot.itemId === null);
                const hasWeightRoom = inv.currentWeight < inv.maxWeight;
                return params.hasRoom ? (hasEmptySlot && hasWeightRoom) : (!hasEmptySlot || !hasWeightRoom);
            });
        }

        // For item type, rarity, and tags filtering, we need to check the actual items
        if (params.itemType || params.itemRarity || params.itemTags) {
            const filteredInventories: Inventory[] = [];

            for (const inventory of inventories) {
                const { items } = await this.getInventoryItems(inventory.id);

                // Apply the filters
                let validItems = items;

                if (params.itemType) {
                    validItems = validItems.filter(item => item.type === params.itemType);
                }

                if (params.itemRarity) {
                    validItems = validItems.filter(item => item.rarity === params.itemRarity);
                }

                if (params.itemTags && params.itemTags.length > 0) {
                    validItems = validItems.filter(item =>
                        params.itemTags!.some(tag => item.tags.includes(tag))
                    );
                }

                // If inventory has any matching items, include it
                if (validItems.length > 0) {
                    filteredInventories.push(inventory);
                }
            }

            return filteredInventories;
        }

        return inventories;
    }

    /**
     * Check if an inventory has a specific item
     */
    public async hasItem(inventoryId: string, itemId: string, quantity: number = 1): Promise<boolean> {
        const inventory = await this.inventoryRepository.findById(inventoryId);
        if (!inventory) return false;

        // Count total quantity of the item across all slots
        const totalQuantity = inventory.slots
            .filter(slot => slot.itemId === itemId)
            .reduce((sum, slot) => sum + slot.quantity, 0);

        return totalQuantity >= quantity;
    }

    /**
     * Transfer items between inventories
     */
    public async transferItems(
        fromInventoryId: string,
        toInventoryId: string,
        itemId: string,
        quantity: number
    ): Promise<boolean> {
        this.logInfo(`Transferring ${quantity} of item ${itemId} from ${fromInventoryId} to ${toInventoryId}`);

        // Check if source inventory has enough of the item
        const hasEnough = await this.hasItem(fromInventoryId, itemId, quantity);
        if (!hasEnough) {
            this.logWarn(`Source inventory ${fromInventoryId} does not have enough of item ${itemId}`);
            return false;
        }

        // Try to remove from source inventory
        const removeResult = await this.removeItemFromInventory(fromInventoryId, itemId, quantity);
        if (!removeResult.success) {
            this.logError(`Failed to remove item from source inventory: ${removeResult.message}`);
            return false;
        }

        // Try to add to destination inventory
        const addResult = await this.addItemToInventory(toInventoryId, itemId, quantity);
        if (!addResult.success) {
            // If failed to add, return the items to source inventory
            this.logError(`Failed to add item to destination inventory: ${addResult.message}`);
            const returnResult = await this.addItemToInventory(
                fromInventoryId,
                itemId,
                removeResult.quantity
            );

            if (!returnResult.success) {
                this.logError(`Failed to return items to source inventory: ${returnResult.message}`);
            }

            return false;
        }

        return true;
    }

    /**
     * Calculate the total value of an inventory
     */
    public async calculateInventoryValue(inventoryId: string): Promise<EconomicValue> {
        this.logInfo(`Calculating value for inventory ${inventoryId}`);

        const { items, slots } = await this.getInventoryItems(inventoryId);

        // Create a map of item ID to item for easy lookup
        const itemMap = new Map<string, Item>();
        items.forEach(item => itemMap.set(item.id, item));

        // Initialize result
        const result: EconomicValue = {
            currencies: [
                { type: CurrencyType.GOLD, amount: 0 },
                { type: CurrencyType.SILVER, amount: 0 },
                { type: CurrencyType.COPPER, amount: 0 }
            ],
            valueModifier: 1.0
        };

        // Calculate total value
        for (const slot of slots) {
            if (!slot.itemId || slot.quantity <= 0) continue;

            const item = itemMap.get(slot.itemId);
            if (!item) continue;

            // Get item value and multiply by quantity
            const itemValue = item.value;

            // Add each currency type
            itemValue.currencies.forEach(currency => {
                const totalAmount = currency.amount * slot.quantity;

                // Find matching currency in result or add if not exists
                const resultCurrency = result.currencies.find(c => c.type === currency.type);
                if (resultCurrency) {
                    resultCurrency.amount += totalAmount;
                } else {
                    result.currencies.push({ type: currency.type, amount: totalAmount });
                }
            });
        }

        return result;
    }

    /**
     * Event handler for item created
     */
    private async handleItemCreated(event: SystemEvent): Promise<void> {
        const { item } = event.data;
        this.logDebug(`Handler: Item created - ${item.name}`);
        // Additional logic can be added here
    }

    /**
     * Event handler for item removed
     */
    private async handleItemRemoved(event: SystemEvent): Promise<void> {
        const { inventoryId, itemId, quantity } = event.data;
        this.logDebug(`Handler: Item removed - ${quantity} of ${itemId} from ${inventoryId}`);
        // Additional logic can be added here
    }

    /**
     * Event handler for inventory created
     */
    private async handleInventoryCreated(event: SystemEvent): Promise<void> {
        const { inventory } = event.data;
        this.logDebug(`Handler: Inventory created for ${inventory.ownerId}`);
        // Additional logic can be added here
    }

    /**
     * Queue refunded materials for later collection if inventory is full
     */
    public queueRefundedMaterials(ownerId: string, materials: { [material: string]: number }) {
        if (!this.refundQueue[ownerId]) {
            this.refundQueue[ownerId] = {};
        }
        for (const [mat, qty] of Object.entries(materials)) {
            this.refundQueue[ownerId][mat] = (this.refundQueue[ownerId][mat] || 0) + qty;
        }
        this.logInfo(`Queued refunded materials for owner ${ownerId}:`, materials);
    }

    public getQueuedRefunds(ownerId: string): { [material: string]: number } {
        return this.refundQueue[ownerId] || {};
    }
} 