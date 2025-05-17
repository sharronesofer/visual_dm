import { v4 as uuidv4 } from 'uuid';
import { Item } from '../models/Item';
import { ItemType } from '../interfaces/types/loot';

export interface InventorySlot {
    id: string;
    item: Item;
    isEquipped: boolean;
    quantity: number;
    stackLimit: number; // Maximum number of this item that can be stacked in one slot
    slotPosition?: number; // Optional positioning within the inventory UI
}

export interface InventorySummary {
    totalItems: number;
    totalValue: number;
    totalWeight: number;
    categories: Record<string, number>; // Count by item type
    equippedItems: string[]; // Names of equipped items
}

export interface InventoryCapacity {
    maxWeight: number;
    maxSlots: number;
}

export class InventoryService {
    private slots: Map<string, InventorySlot> = new Map();
    private capacity: InventoryCapacity = {
        maxWeight: 100, // Default maximum weight
        maxSlots: 20,   // Default slot count
    };

    constructor(capacity?: Partial<InventoryCapacity>) {
        if (capacity) {
            this.capacity = { ...this.capacity, ...capacity };
        }
    }

    /**
     * Add an item to the inventory
     */
    addItem(item: Item, quantity: number = 1): string | null {
        // Don't add items with zero or negative quantities
        if (quantity <= 0) {
            return null;
        }

        // Check if adding this item would exceed weight capacity
        const potentialWeight = this.getCurrentWeight() + (item.weight * quantity);
        if (potentialWeight > this.capacity.maxWeight) {
            return null; // Cannot add due to weight constraints
        }

        // Check if the item is stackable and if we have existing stacks
        const stackable = this.isItemStackable(item);
        if (stackable) {
            // Try to find an existing slot with the same item type that isn't full
            const existingSlot = this.findStackableSlot(item);

            if (existingSlot) {
                // Calculate how many items can be added to this stack
                const availableSpace = existingSlot.stackLimit - existingSlot.quantity;
                const amountToAdd = Math.min(quantity, availableSpace);

                // Add to existing stack
                existingSlot.quantity += amountToAdd;

                // If there are remaining items, create a new slot (recursive call)
                const remaining = quantity - amountToAdd;
                if (remaining > 0) {
                    return this.addItem(item, remaining);
                }

                return existingSlot.id;
            }
        }

        // We need a new slot - check if we have space
        if (this.slots.size >= this.capacity.maxSlots) {
            return null; // No more slot space
        }

        // Create a new inventory slot
        const defaultStackLimit = stackable ? 99 : 1;
        const slotId = uuidv4();
        const newSlot: InventorySlot = {
            id: slotId,
            item,
            isEquipped: false,
            quantity,
            stackLimit: defaultStackLimit,
            slotPosition: this.getNextAvailablePosition()
        };

        this.slots.set(slotId, newSlot);
        return slotId;
    }

    /**
     * Remove an item from the inventory
     */
    removeItem(slotId: string, quantity: number = 1): boolean {
        const slot = this.slots.get(slotId);
        if (!slot) {
            return false;
        }

        if (quantity >= slot.quantity) {
            // Remove the entire slot
            if (slot.isEquipped) {
                // Unequip before removing
                this.unequipItem(slotId);
            }
            this.slots.delete(slotId);
        } else {
            // Reduce quantity
            slot.quantity -= quantity;
        }

        return true;
    }

    /**
     * Equip an item
     */
    equipItem(slotId: string): boolean {
        const slot = this.slots.get(slotId);
        if (!slot || slot.quantity <= 0) {
            return false;
        }

        // Check if any similar type item is already equipped
        this.unequipItemsByType(slot.item.type);

        // Mark as equipped
        slot.isEquipped = true;
        return true;
    }

    /**
     * Unequip an item
     */
    unequipItem(slotId: string): boolean {
        const slot = this.slots.get(slotId);
        if (!slot) {
            return false;
        }

        slot.isEquipped = false;
        return true;
    }

    /**
     * Unequip all items of a specific type
     */
    private unequipItemsByType(type: ItemType): void {
        this.slots.forEach(slot => {
            if (slot.isEquipped && slot.item.type === type) {
                slot.isEquipped = false;
            }
        });
    }

    /**
     * Check if the inventory contains a specific item by ID
     */
    hasItem(itemId: string, minQuantity: number = 1): boolean {
        let totalQuantity = 0;

        // Check all slots for the item
        for (const slot of this.slots.values()) {
            if (slot.item.id === itemId) {
                totalQuantity += slot.quantity;
                if (totalQuantity >= minQuantity) {
                    return true;
                }
            }
        }

        return false;
    }

    /**
     * Count total quantity of an item type in inventory
     */
    countItemsByType(type: ItemType): number {
        let count = 0;
        this.slots.forEach(slot => {
            if (slot.item.type === type) {
                count += slot.quantity;
            }
        });
        return count;
    }

    /**
     * Get current inventory weight
     */
    getCurrentWeight(): number {
        let totalWeight = 0;
        this.slots.forEach(slot => {
            totalWeight += slot.item.weight * slot.quantity;
        });
        return totalWeight;
    }

    /**
     * Get summary of inventory contents
     */
    getSummary(): InventorySummary {
        let totalItems = 0;
        let totalValue = 0;
        let totalWeight = 0;
        const categories: Record<string, number> = {};
        const equippedItems: string[] = [];

        this.slots.forEach(slot => {
            const itemType = slot.item.type.toString();

            // Update totals
            totalItems += slot.quantity;
            totalValue += slot.item.value * slot.quantity;
            totalWeight += slot.item.weight * slot.quantity;

            // Update category count
            categories[itemType] = (categories[itemType] || 0) + slot.quantity;

            // Track equipped items
            if (slot.isEquipped) {
                equippedItems.push(slot.item.name);
            }
        });

        return {
            totalItems,
            totalValue,
            totalWeight,
            categories,
            equippedItems
        };
    }

    /**
     * Get all inventory slots
     */
    getAllSlots(): InventorySlot[] {
        return Array.from(this.slots.values());
    }

    /**
     * Get slots with equipped items
     */
    getEquippedSlots(): InventorySlot[] {
        return Array.from(this.slots.values()).filter(slot => slot.isEquipped);
    }

    /**
     * Sort inventory by specified criteria
     */
    sortInventory(criteria: 'value' | 'weight' | 'name' | 'type' | 'quantity'): void {
        const slots = this.getAllSlots();

        slots.sort((a, b) => {
            switch (criteria) {
                case 'value':
                    return b.item.value - a.item.value;
                case 'weight':
                    return b.item.weight - a.item.weight;
                case 'name':
                    return a.item.name.localeCompare(b.item.name);
                case 'type':
                    return a.item.type.toString().localeCompare(b.item.type.toString());
                case 'quantity':
                    return b.quantity - a.quantity;
                default:
                    return 0;
            }
        });

        // Update slot positions based on sorted order
        slots.forEach((slot, index) => {
            const storedSlot = this.slots.get(slot.id);
            if (storedSlot) {
                storedSlot.slotPosition = index;
            }
        });
    }

    /**
     * Determine if an item can be stacked
     */
    private isItemStackable(item: Item): boolean {
        // Generally, consumables and materials can be stacked
        return [
            ItemType.POTION,
            ItemType.MATERIAL,
            ItemType.TREASURE,
            ItemType.MISC
        ].includes(item.type);
    }

    /**
     * Find a slot that can stack more of this item
     */
    private findStackableSlot(item: Item): InventorySlot | undefined {
        for (const slot of this.slots.values()) {
            // Check if same item type and not full
            if (slot.item.id === item.id && slot.quantity < slot.stackLimit) {
                return slot;
            }
        }
        return undefined;
    }

    /**
     * Get the next available position for a new item
     */
    private getNextAvailablePosition(): number {
        const positions = new Set(
            Array.from(this.slots.values())
                .map(slot => slot.slotPosition)
                .filter(pos => pos !== undefined) as number[]
        );

        // Find the first unused position
        for (let i = 0; i < this.capacity.maxSlots; i++) {
            if (!positions.has(i)) {
                return i;
            }
        }

        // Fallback to end of inventory
        return this.slots.size;
    }

    /**
     * Increase inventory capacity
     */
    upgradeCapacity(additionalWeight: number = 0, additionalSlots: number = 0): void {
        this.capacity.maxWeight += additionalWeight;
        this.capacity.maxSlots += additionalSlots;
    }

    /**
     * Clear the entire inventory
     */
    clearInventory(): void {
        this.slots.clear();
    }

    /**
     * Transfer an item between inventories
     */
    static transferItem(
        sourceInventory: InventoryService,
        targetInventory: InventoryService,
        sourceSlotId: string,
        quantity: number = 1
    ): boolean {
        // Get the source slot
        const sourceSlot = sourceInventory.slots.get(sourceSlotId);
        if (!sourceSlot || sourceSlot.quantity < quantity) {
            return false;
        }

        // Try to add to target inventory first
        const addedSlotId = targetInventory.addItem(sourceSlot.item, quantity);
        if (!addedSlotId) {
            return false; // Target inventory couldn't accept the item
        }

        // Remove from source inventory
        sourceInventory.removeItem(sourceSlotId, quantity);
        return true;
    }
} 