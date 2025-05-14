from typing import Any, Dict, List


class PlayerInventory:
    items: Dict[str, float>
    equipment: Dict[str, Any>
class ItemConsequenceHandler {
  private playerInventories: Map<string, PlayerInventory> = new Map()
  constructor() {}
  /**
   * Handle item reward consequence
   */
  async handleItemReward(playerId: str, consequence: Any, worldState: WorldState): Promise<void> {
    const inventory = this.getPlayerInventory(playerId)
    const { itemId, amount } = consequence.value
    this.addItem(inventory, itemId, amount)
  }
  /**
   * Handle item removal consequence
   */
  async handleItemRemoval(playerId: str, consequence: Any, worldState: WorldState): Promise<void> {
    const inventory = this.getPlayerInventory(playerId)
    const { itemId, amount } = consequence.value
    this.removeItem(inventory, itemId, amount)
  }
  /**
   * Get player's inventory, creating it if it doesn't exist
   */
  getPlayerInventory(playerId: str): \'PlayerInventory\' {
    if (!this.playerInventories.has(playerId)) {
      this.playerInventories.set(playerId, {
        items: new Map(),
        equipment: new Map()
      })
    }
    return this.playerInventories.get(playerId)!
  }
  /**
   * Handle item consequences
   */
  handleConsequences(inventory: \'PlayerInventory\', consequences: List[any]): void {
    consequences.forEach(consequence => {
      switch (consequence.type) {
        case 'ADD_ITEM':
          this.addItem(inventory, consequence.itemId, consequence.amount)
          break
        case 'REMOVE_ITEM':
          this.removeItem(inventory, consequence.itemId, consequence.amount)
          break
        case 'EQUIP_ITEM':
          this.equipItem(inventory, consequence.itemId, consequence.slot)
          break
        case 'UNEQUIP_ITEM':
          this.unequipItem(inventory, consequence.slot)
          break
      }
    })
  }
  private addItem(inventory: \'PlayerInventory\', itemId: str, amount: float): void {
    const currentAmount = inventory.items.get(itemId) || 0
    inventory.items.set(itemId, currentAmount + amount)
  }
  private removeItem(inventory: \'PlayerInventory\', itemId: str, amount: float): void {
    const currentAmount = inventory.items.get(itemId) || 0
    const newAmount = Math.max(0, currentAmount - amount)
    inventory.items.set(itemId, newAmount)
  }
  private equipItem(inventory: \'PlayerInventory\', itemId: str, slot: str): void {
    this.unequipItem(inventory, slot)
    inventory.equipment.set(slot, itemId)
    this.removeItem(inventory, itemId, 1)
  }
  private unequipItem(inventory: \'PlayerInventory\', slot: str): void {
    const equippedItem = inventory.equipment.get(slot)
    if (equippedItem) {
      this.addItem(inventory, equippedItem, 1)
      inventory.equipment.delete(slot)
    }
  }
} 