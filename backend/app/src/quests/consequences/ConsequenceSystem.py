from typing import Any, Dict, List, Union


/**
 * Types of consequences that can occur
 */
ConsequenceType = Union[, 'faction_reputation', 'world_state', 'npc_relationship', 'environment', 'quest_availability', 'economy', 'custom']
/**
 * Severity levels for consequences
 */
ConsequenceSeverity = Union['minor', 'moderate', 'major', 'critical']
/**
 * Represents a consequence trigger condition
 */
class ConsequenceTrigger:
    type: Union['immediate', 'delayed', 'conditional']
    delay?: float
    condition?: (state: WorldState) => bool
/**
 * Represents a single consequence
 */
class Consequence:
    id: str
    type: ConsequenceType
    severity: ConsequenceSeverity
    description: str
    trigger: \'ConsequenceTrigger\'
    effects: Dict[str, Any]
}
WorldStateChangeType = Union[, 'QUEST_COMPLETION', 'QUEST_FAILURE', 'QUEST_CANCELLED', 'FACTION_TENSION_CHANGE', 'TENSION_DECREASE', 'DIPLOMATIC_OPPORTUNITY', 'RESOURCE_CHANGE', 'TERRITORY_CHANGE']
class WorldStateChange:
    type: WorldStateChangeType
    description: str
    value: float
    affectedFactions: List[FactionType]
    location: Union[str, None]
    customData?: \'WorldStateChangeCustomData\'
class WorldStateChangeCustomData:
    type: Union['QUEST_COMPLETION', 'QUEST_FAILURE', 'QUEST_CANCELLATION', 'TENSION_DECAY', 'TENSION_STATE_CHANGE', 'DIPLOMATIC_EVENT']
    questId?: str
    winningFaction?: FactionType
    factions?: List[FactionType]
    timestamp: float
    oldState?: Union['HIGH_TENSION', 'LOW_TENSION']
    newState?: Union['HIGH_TENSION', 'LOW_TENSION']
    eventType?: Union['OPPORTUNITY', 'CONFLICT']
/**
 * Manages the tracking and application of quest consequences
 */
class ConsequenceSystem {
  private itemHandler: ItemConsequenceHandler
  constructor(private worldStateHandler: WorldStateHandler) {
    this.itemHandler = new ItemConsequenceHandler()
  }
  /**
   * Process a consequence
   */
  async processConsequence(
    playerId: str,
    consequence: QuestConsequence
  ): Promise<void> {
    switch (consequence.type) {
      case 'ITEM_REWARD':
        await this.itemHandler.handleItemReward(playerId, consequence, this.worldStateHandler.getWorldState())
        break
      case 'ITEM_REMOVE':
        await this.itemHandler.handleItemRemoval(playerId, consequence, this.worldStateHandler.getWorldState())
        break
      case 'WORLD_STATE':
        await this.worldStateHandler.handleWorldStateChange(consequence, this.worldStateHandler.getWorldState())
        break
      default:
        throw new Error(`Unknown consequence type: ${consequence.type}`)
    }
  }
  /**
   * Process multiple consequences
   */
  async processConsequences(
    playerId: str,
    consequences: List[QuestConsequence]
  ): Promise<void> {
    for (const consequence of consequences) {
      await this.processConsequence(playerId, consequence)
    }
  }
  /**
   * Update world state (check expired effects, etc.)
   */
  update(): void {
    this.worldStateHandler.update(this.worldStateHandler.getWorldState())
  }
  /**
   * Get the current world state
   */
  getWorldState(): WorldState {
    return this.worldStateHandler.getWorldState()
  }
  /**
   * Get a player's inventory
   */
  getPlayerInventory(playerId: str): PlayerInventory {
    return this.itemHandler.getPlayerInventory(playerId)
  }
  /**
   * Get state changes for a specific location
   */
  getLocationChanges(location: str): WorldStateChange[] {
    return this.worldStateHandler.getLocationChanges(location)
  }
  /**
   * Apply a consequence to the world state
   */
  applyConsequence(consequence: WorldStateChange): void {
    this.worldStateHandler.applyWorldStateChange(consequence)
  }
  /**
   * Apply a list of consequences to the world state
   */
  applyConsequences(consequences: List[WorldStateChange]): void {
    consequences.forEach(consequence => {
      this.worldStateHandler.applyChange(consequence)
    })
  }
  /**
   * Get all state changes
   */
  getAllStateChanges(): WorldStateChange[] {
    return this.worldStateHandler.getAllStateChanges()
  }
  /**
   * Handle item consequences
   */
  handleItemConsequences(inventory: Any, consequences: List[any]): void {
    this.itemHandler.handleConsequences(inventory, consequences)
  }
} 