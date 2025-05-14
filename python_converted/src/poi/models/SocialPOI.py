from typing import Any, Dict, Union


{ SocialSubtype }
class NPC:
    id: str
    name: str
    role: Union['merchant', 'quest_giver', 'trainer', 'guard', 'leader', 'citizen']
    properties: Dict[str, Any]
    inventory?: string[]
    [key: string]: unknown
  }
}
class Quest:
    id: str
    title: str
    type: Union['fetch', 'escort', 'defend', 'investigate', 'diplomatic']
    properties: Dict[str, Any]
}
class Faction:
    id: str
    name: str
    properties: Dict[str, Any]
}
/**
 * Specialized POI class for social interaction locations
 */
class SocialPOI extends BasePOI {
  private npcData: Map<string, NPC>
  private questData: Map<string, Quest>
  private factions: Map<string, Faction>
  private economyLevel: float
  private populationDensity: float
  constructor(
    id: str,
    name: str,
    subtype: SocialSubtype,
    coordinates: Coordinates,
    thematicElements: ThematicElements
  ) {
    super(id, name, POIType.SOCIAL, subtype, coordinates, thematicElements)
    this.npcData = new Map<string, NPC>()
    this.questData = new Map<string, Quest>()
    this.factions = new Map<string, Faction>()
    this.economyLevel = this.calculateInitialEconomyLevel()
    this.populationDensity = this.calculateInitialPopulation()
    this.boundingBox = { width: 2, height: 2, depth: 2 } 
    this.canExpand = true
    this.expansionRules = [
      {
        direction: 'north',
        conditions: ['!blocked', 'population_pressure'],
        probability: 0.4
      },
      {
        direction: 'south',
        conditions: ['!blocked', 'population_pressure'],
        probability: 0.4
      },
      {
        direction: 'east',
        conditions: ['!blocked', 'population_pressure'],
        probability: 0.4
      },
      {
        direction: 'west',
        conditions: ['!blocked', 'population_pressure'],
        probability: 0.4
      }
    ]
    this.initializeBySubtype(subtype)
  }
  addNPC(npc: NPC): void {
    this.npcData.set(npc.id, npc)
    this.npcs.push(npc.id)
    this.features.push({
      id: npc.id,
      type: `npc_${npc.role}`,
      properties: npc.properties
    })
    this.trackChange('modification', `Added ${npc.role} NPC: ${npc.name}`)
  }
  removeNPC(npcId: str): bool {
    const removed = this.npcData.delete(npcId)
    if (removed) {
      this.npcs = this.npcs.filter(id => id !== npcId)
      this.features = this.features.filter(f => f.id !== npcId)
      this.trackChange('modification', `Removed NPC: ${npcId}`)
    }
    return removed
  }
  getNPC(npcId: str): \'NPC\' | undefined {
    return this.npcData.get(npcId)
  }
  updateNPCSchedule(npcId: str, timeOfDay: str, activity: str): bool {
    const npc = this.npcData.get(npcId)
    if (npc) {
      if (!npc.properties.schedule) {
        npc.properties.schedule = {}
      }
      npc.properties.schedule[timeOfDay] = activity
      this.trackChange('modification', `Updated schedule for NPC: ${npcId}`)
      return true
    }
    return false
  }
  addQuest(quest: Quest): void {
    this.questData.set(quest.id, quest)
    this.quests.push(quest.id)
    this.features.push({
      id: quest.id,
      type: `quest_${quest.type}`,
      properties: quest.properties
    })
    this.trackChange('modification', `Added ${quest.type} quest: ${quest.title}`)
  }
  removeQuest(questId: str): bool {
    const removed = this.questData.delete(questId)
    if (removed) {
      this.quests = this.quests.filter(id => id !== questId)
      this.features = this.features.filter(f => f.id !== questId)
      this.trackChange('modification', `Removed quest: ${questId}`)
    }
    return removed
  }
  getQuest(questId: str): \'Quest\' | undefined {
    return this.questData.get(questId)
  }
  completeQuest(questId: str): bool {
    const quest = this.questData.get(questId)
    if (quest && !quest.properties.isComplete) {
      quest.properties.isComplete = true
      this.trackChange('modification', `Completed quest: ${questId}`)
      if (quest.properties.rewards?.reputation) {
        this.adjustFactionReputation(
          Object.keys(this.factions)[0], 
          quest.properties.rewards.reputation
        )
      }
      return true
    }
    return false
  }
  addFaction(faction: Faction): void {
    this.factions.set(faction.id, faction)
    this.features.push({
      id: faction.id,
      type: 'faction',
      properties: faction.properties
    })
    this.trackChange('modification', `Added faction: ${faction.name}`)
  }
  removeFaction(factionId: str): bool {
    const removed = this.factions.delete(factionId)
    if (removed) {
      this.features = this.features.filter(f => f.id !== factionId)
      this.trackChange('modification', `Removed faction: ${factionId}`)
    }
    return removed
  }
  getFaction(factionId: str): \'Faction\' | undefined {
    return this.factions.get(factionId)
  }
  adjustFactionReputation(factionId: str, change: float): bool {
    const faction = this.factions.get(factionId)
    if (faction) {
      faction.properties.playerReputation = Math.max(
        -100,
        Math.min(100, faction.properties.playerReputation + change)
      )
      this.trackChange('modification', `Adjusted faction reputation: ${factionId}`)
      return true
    }
    return false
  }
  getEconomyLevel(): float {
    return this.economyLevel
  }
  getPopulationDensity(): float {
    return this.populationDensity
  }
  serialize(): Record<string, unknown> {
    return {
      ...super.serialize(),
      npcData: Array.from(this.npcData.entries()),
      questData: Array.from(this.questData.entries()),
      factions: Array.from(this.factions.entries()),
      economyLevel: this.economyLevel,
      populationDensity: this.populationDensity
    }
  }
  deserialize(data: Record<string, unknown>): void {
    super.deserialize(data)
    if (Array.isArray(data.npcData)) {
      this.npcData = new Map(data.npcData)
    }
    if (Array.isArray(data.questData)) {
      this.questData = new Map(data.questData)
    }
    if (Array.isArray(data.factions)) {
      this.factions = new Map(data.factions)
    }
    if (typeof data.economyLevel === 'number') {
      this.economyLevel = data.economyLevel
    }
    if (typeof data.populationDensity === 'number') {
      this.populationDensity = data.populationDensity
    }
  }
  validateThematicCoherence(): bool {
    return super.validateThematicCoherence() && this.validateSocialTheme()
  }
  private validateSocialTheme(): bool {
    return (
      this.validateNPCDistribution() &&
      this.validateQuestAvailability() &&
      this.validateFactionInfluence()
    )
  }
  private validateNPCDistribution(): bool {
    const npcRoles = new Set(Array.from(this.npcData.values()).map(npc => npc.role))
    switch (this.subtype as SocialSubtype) {
      case SocialSubtype.MARKET:
        return npcRoles.has('merchant')
      case SocialSubtype.GUILD:
        return npcRoles.has('trainer') || npcRoles.has('leader')
      case SocialSubtype.CASTLE:
        return npcRoles.has('guard') && npcRoles.has('leader')
      default:
        return true
    }
  }
  private validateQuestAvailability(): bool {
    for (const quest of this.questData.values()) {
      if (quest.properties.difficulty < 1 || quest.properties.difficulty > 10) {
        return false
      }
    }
    return true
  }
  private validateFactionInfluence(): bool {
    for (const faction of this.factions.values()) {
      if (faction.properties.dominance < 0 || faction.properties.dominance > 10) {
        return false
      }
    }
    return this.factions.size > 0
  }
  private calculateInitialEconomyLevel(): float {
    let baseEconomy = 5 
    switch (this.subtype as SocialSubtype) {
      case SocialSubtype.MARKET:
      case SocialSubtype.GUILD:
        baseEconomy += 2
        break
      case SocialSubtype.CASTLE:
        baseEconomy += 3
        break
      case SocialSubtype.VILLAGE:
        baseEconomy -= 1
        break
      default:
        break
    }
    return Math.min(10, Math.max(1, baseEconomy))
  }
  private calculateInitialPopulation(): float {
    let basePopulation = this.economyLevel
    switch (this.subtype as SocialSubtype) {
      case SocialSubtype.VILLAGE:
        basePopulation += 2
        break
      case SocialSubtype.MARKET:
        basePopulation += 4
        break
      case SocialSubtype.CASTLE:
        basePopulation += 5
        break
      default:
        break
    }
    return Math.min(10, basePopulation)
  }
  private initializeBySubtype(subtype: SocialSubtype): void {
    switch (subtype) {
      case SocialSubtype.VILLAGE:
        this.boundingBox = { width: 3, height: 1, depth: 3 } 
        break
      case SocialSubtype.MARKET:
        this.boundingBox = { width: 2, height: 1, depth: 2 } 
        this.thematicElements.dangerLevel = Math.min(2, this.thematicElements.dangerLevel)
        break
      case SocialSubtype.GUILD:
        this.boundingBox = { width: 2, height: 2, depth: 2 } 
        break
      case SocialSubtype.CASTLE:
        this.boundingBox = { width: 4, height: 4, depth: 4 } 
        this.thematicElements.dangerLevel = Math.max(4, this.thematicElements.dangerLevel)
        break
      default:
        break
    }
  }
} 