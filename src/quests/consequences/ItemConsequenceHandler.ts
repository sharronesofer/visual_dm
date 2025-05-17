import { WorldState } from './WorldStateHandler';
import { ItemService } from '../../core/services/ItemService';
import { Item } from '../../core/models/Item';
import { ItemType } from '../../core/interfaces/types/loot';

// Define a proper type for the player inventory
export interface PlayerInventory {
  inventorySlotIds: string[];
}

export class ItemConsequenceHandler {
  private playerIds: Set<string> = new Set();
  private itemService: ItemService;

  constructor(itemService: ItemService) {
    this.itemService = itemService;
  }

  /**
   * Handle item reward consequence
   */
  async handleItemReward(playerId: string, consequence: any, worldState: WorldState): Promise<void> {
    this.registerPlayer(playerId);

    // Extract consequence details
    const { itemId, itemType, amount = 1, rarity } = consequence.value;

    // Generate an item based on the consequence
    let item: Item | null = null;

    if (itemId) {
      // Try to get specific item by ID
      const foundItem = this.itemService.getItem(itemId);
      if (foundItem) {
        item = foundItem;
      }
    } else if (itemType) {
      // Generate a random item of the specified type
      if (rarity && rarity.toLowerCase().includes('magic')) {
        // Generate magical item
        item = this.itemService.generateMagicalItem(itemType as ItemType);
      } else {
        // Generate regular item
        item = this.itemService.generateRandomItem(itemType as ItemType);
      }
    } else {
      // Generate completely random item
      item = this.itemService.generateRandomItem();
    }

    // Add the item to player inventory
    if (item) {
      this.itemService.addItemToInventory(item, amount);
    }
  }

  /**
   * Handle item removal consequence
   */
  async handleItemRemoval(playerId: string, consequence: any, worldState: WorldState): Promise<void> {
    this.registerPlayer(playerId);

    // Extract consequence details
    const { itemId, amount = 1 } = consequence.value;

    // Get inventory slots that contain this item
    const inventory = this.itemService.getPlayerInventory();
    const slots = inventory.getAllSlots().filter(slot => slot.item.id === itemId);

    // Remove items from slots
    let remainingToRemove = amount;

    for (const slot of slots) {
      if (remainingToRemove <= 0) break;

      const amountFromThisSlot = Math.min(slot.quantity, remainingToRemove);
      if (this.itemService.removeItemFromInventory(slot.id, amountFromThisSlot)) {
        remainingToRemove -= amountFromThisSlot;
      }
    }
  }

  /**
   * Register a player to be tracked
   */
  registerPlayer(playerId: string): void {
    this.playerIds.add(playerId);
  }

  /**
   * Handle item consequences
   */
  handleConsequences(playerId: string, consequences: any[]): void {
    this.registerPlayer(playerId);

    consequences.forEach(consequence => {
      switch (consequence.type) {
        case 'ADD_ITEM':
          this.handleItemReward(playerId, { value: consequence }, {} as WorldState);
          break;

        case 'REMOVE_ITEM':
          this.handleItemRemoval(playerId, { value: consequence }, {} as WorldState);
          break;

        case 'EQUIP_ITEM':
          this.equipItem(playerId, consequence.itemId, consequence.slot);
          break;

        case 'UNEQUIP_ITEM':
          this.unequipItem(playerId, consequence.slot);
          break;
      }
    });
  }

  /**
   * Equip an item to a specific slot
   */
  private equipItem(playerId: string, itemId: string, slot: string): void {
    const inventory = this.itemService.getPlayerInventory();
    const slots = inventory.getAllSlots().filter(s => s.item.id === itemId);

    if (slots.length > 0) {
      this.itemService.equipItem(slots[0].id);
    }
  }

  /**
   * Unequip an item from a specific slot
   */
  private unequipItem(playerId: string, slot: string): void {
    const inventory = this.itemService.getPlayerInventory();
    const equippedSlots = inventory.getEquippedSlots();

    // Find the slot matching the requested slot to unequip
    // This is a simplification; in a real implementation, you would map slot names correctly
    const slotToUnequip = equippedSlots[0]; // Just unequip the first equipped item for simplicity

    if (slotToUnequip) {
      this.itemService.unequipItem(slotToUnequip.id);
    }
  }
} 