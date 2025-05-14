from typing import Any, Dict, List


class WorldState:
    resources: Dict[str, float>
    territories: Dict[str, str[]>
    influence: Dict[str, float>
    custom: Dict[str, Any>
    customStates: Dict[str, Any>
    environmentalConditions: Dict[str, Any]
  economyFactors: Dict[str, Any]
  }
  availableQuests: Set<string>
  activeEffects: List[any]
  territoryControl: Record<string, string>
  factionInfluence: Record<string, number>
  factionTensions: Record<string, number>
}
/**
 * Handles world state changes and their application to locations
 */
class WorldStateHandler {
  private stateChanges: Map<string, WorldStateChange> = new Map()
  private locationChanges: Map<string, WorldStateChange[]> = new Map()
  private worldState: \'WorldState\'
  constructor(initialState: WorldState) {
    this.worldState = initialState
  }
  /**
   * Apply a world state change
   */
  applyWorldStateChange(change: WorldStateChange): void {
    const { type, description, value, affectedFactions, location, customData } = change
    const key = `${type}_${affectedFactions.join('_')}_${Date.now()}`
    this.stateChanges.set(key, change)
    if (location) {
      const locationKey = location.toLowerCase()
      const changes = this.locationChanges.get(locationKey) || []
      changes.push(change)
      this.locationChanges.set(locationKey, changes)
    }
    switch (type) {
      case 'RESOURCE':
        this.handleResourceChange(change)
        break
      case 'TERRITORY':
        this.handleTerritoryChange(change)
        break
      case 'INFLUENCE':
        this.handleInfluenceChange(change)
        break
      case 'FACTION_TENSION_CHANGE':
        this.handleTensionChange(change)
        break
      case 'CUSTOM':
        this.handleCustomChange(change)
        break
      case 'QUEST_FAILURE':
        this.applyQuestFailure(change)
        break
      default:
        console.warn(`Unhandled world state change type: ${type}`)
    }
  }
  /**
   * Get the current world state
   */
  getWorldState(): \'WorldState\' {
    return this.worldState
  }
  /**
   * Get all state changes
   */
  getAllStateChanges(): WorldStateChange[] {
    return Array.from(this.stateChanges.values())
  }
  /**
   * Get state changes for a specific location
   */
  getLocationChanges(location: str): WorldStateChange[] {
    const locationKey = location.toLowerCase()
    return this.locationChanges.get(locationKey) || []
  }
  /**
   * Get the current territory control state
   */
  getTerritoryControl(): Record<string, string> {
    return this.worldState.territoryControl
  }
  /**
   * Get the availability of a resource
   */
  getResourceAvailability(resourceId: str): float {
    return this.worldState.resources.get(resourceId) || 0
  }
  /**
   * Get current environmental conditions
   */
  getEnvironmentalConditions(): Record<string, any> {
    return this.worldState.environmentalConditions
  }
  private handleResourceChange(change: WorldStateChange): void {
    const resourceId = change.customData?.resourceId
    if (!resourceId) return
    const currentValue = this.worldState.resources.get(resourceId) || 0
    this.worldState.resources.set(resourceId, currentValue + change.value)
  }
  private handleTerritoryChange(change: WorldStateChange): void {
    const territory = change.customData?.territory
    const faction = change.customData?.faction as FactionType
    if (!territory || !faction) return
    const currentTerritories = this.worldState.territories.get(faction) || []
    if (change.value > 0) {
      if (!currentTerritories.includes(territory)) {
        currentTerritories.push(territory)
      }
    } else {
      const index = currentTerritories.indexOf(territory)
      if (index > -1) {
        currentTerritories.splice(index, 1)
      }
    }
    this.worldState.territories.set(faction, currentTerritories)
    this.worldState.territoryControl[territory] = faction
  }
  private handleInfluenceChange(change: WorldStateChange): void {
    const faction = change.customData?.faction as FactionType
    if (!faction) return
    const currentValue = this.worldState.influence.get(faction) || 0
    this.worldState.influence.set(faction, currentValue + change.value)
    this.worldState.factionInfluence[faction] = 
      (this.worldState.factionInfluence[faction] || 0) + change.value
  }
  private handleTensionChange(change: WorldStateChange): void {
    const factions = change.affectedFactions as FactionType[]
    if (factions.length !== 2) return
    const tensionKey = `${factions[0]}_${factions[1]}`
    const currentTension = this.worldState.factionTensions[tensionKey] || 0
    this.worldState.factionTensions[tensionKey] = currentTension + change.value
  }
  private handleCustomChange(change: WorldStateChange): void {
    const key = change.customData?.key
    const value = change.customData?.value
    if (!key) return
    this.worldState.custom.set(key, value)
  }
  private applyQuestFailure(change: WorldStateChange): void {
    if (!change.customData?.questId) return
    const questFailures = this.worldState.custom.get('questFailures') || []
    questFailures.push({
      questId: change.customData.questId,
      timestamp: Date.now(),
      affectedFactions: change.affectedFactions,
      reason: change.description
    })
    this.worldState.custom.set('questFailures', questFailures)
    if (change.value !== 0) {
      change.affectedFactions.forEach(faction => {
        const currentInfluence = this.worldState.influence.get(faction) || 0
        this.worldState.influence.set(faction, currentInfluence + change.value)
      })
    }
  }
  /**
   * Handle world state change from a consequence
   */
  async handleWorldStateChange(consequence: Any, state: WorldState): Promise<void> {
    const { target, value } = consequence
    switch (target) {
      case 'environment':
        state.environmentalConditions.environment = value
        break
      case 'economy':
        Object.assign(state.economyFactors, value)
        break
      case 'quest_availability':
        if (value.add) {
          value.add.forEach((questId: str) => state.availableQuests.add(questId))
        }
        if (value.remove) {
          value.remove.forEach((questId: str) => state.availableQuests.delete(questId))
        }
        break
      case 'active_effects':
        state.activeEffects.push(value)
        break
    }
  }
  /**
   * Update world state (check expired effects, etc.)
   */
  update(state: WorldState): void {
    const now = Date.now()
    state.activeEffects = state.activeEffects.filter(effect => {
      if (!effect.duration) return true
      return (effect.startTime + effect.duration) > now
    })
    for (const [location, changes] of this.locationChanges.entries()) {
      this.locationChanges.set(
        location,
        changes.filter(change => {
          if (!change.customData?.duration) return true
          return (change.customData.timestamp + change.customData.duration) > now
        })
      )
    }
  }
} 