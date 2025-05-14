import { WorldState } from './WorldStateHandler';

export interface PlayerInventory {
  items: Map<string, number>;
  equipment: Map<string, any>;
}

export class ItemConsequenceHandler {
  private playerInventories: Map<string, PlayerInventory> = new Map();

  constructor() {}

  /**
   * Handle item reward consequence
   */
  async handleItemReward(playerId: string, consequence: any, worldState: WorldState): Promise<void> {
    const inventory = this.getPlayerInventory(playerId);
    const { itemId, amount } = consequence.value;
    this.addItem(inventory, itemId, amount);
  }

  /**
   * Handle item removal consequence
   */
  async handleItemRemoval(playerId: string, consequence: any, worldState: WorldState): Promise<void> {
    const inventory = this.getPlayerInventory(playerId);
    const { itemId, amount } = consequence.value;
    this.removeItem(inventory, itemId, amount);
  }

  /**
   * Get player's inventory, creating it if it doesn't exist
   */
  getPlayerInventory(playerId: string): PlayerInventory {
    if (!this.playerInventories.has(playerId)) {
      this.playerInventories.set(playerId, {
        items: new Map(),
        equipment: new Map()
      });
    }
    return this.playerInventories.get(playerId)!;
  }

  /**
   * Handle item consequences
   */
  handleConsequences(inventory: PlayerInventory, consequences: any[]): void {
    consequences.forEach(consequence => {
      switch (consequence.type) {
        case 'ADD_ITEM':
          this.addItem(inventory, consequence.itemId, consequence.amount);
          break;
        case 'REMOVE_ITEM':
          this.removeItem(inventory, consequence.itemId, consequence.amount);
          break;
        case 'EQUIP_ITEM':
          this.equipItem(inventory, consequence.itemId, consequence.slot);
          break;
        case 'UNEQUIP_ITEM':
          this.unequipItem(inventory, consequence.slot);
          break;
      }
    });
  }

  private addItem(inventory: PlayerInventory, itemId: string, amount: number): void {
    const currentAmount = inventory.items.get(itemId) || 0;
    inventory.items.set(itemId, currentAmount + amount);
  }

  private removeItem(inventory: PlayerInventory, itemId: string, amount: number): void {
    const currentAmount = inventory.items.get(itemId) || 0;
    const newAmount = Math.max(0, currentAmount - amount);
    inventory.items.set(itemId, newAmount);
  }

  private equipItem(inventory: PlayerInventory, itemId: string, slot: string): void {
    // Unequip any existing item in the slot
    this.unequipItem(inventory, slot);
    
    // Equip the new item
    inventory.equipment.set(slot, itemId);
    
    // Remove one instance from inventory
    this.removeItem(inventory, itemId, 1);
  }

  private unequipItem(inventory: PlayerInventory, slot: string): void {
    const equippedItem = inventory.equipment.get(slot);
    if (equippedItem) {
      // Add the item back to inventory
      this.addItem(inventory, equippedItem, 1);
      
      // Clear the equipment slot
      inventory.equipment.delete(slot);
    }
  }
} 