from typing import Any, List



const baseNPCs: Record<FactionType, { role: str; count: float; hierarchyLevel: float; behaviorProfile: str }[]> = {
  guild: [
    { role: 'guildmaster', count: 1, hierarchyLevel: 3, behaviorProfile: 'leader' },
    { role: 'artisan', count: 3, hierarchyLevel: 2, behaviorProfile: 'crafting' },
    { role: 'apprentice', count: 5, hierarchyLevel: 1, behaviorProfile: 'learning' }
  ],
  order: [
    { role: 'grandmaster', count: 1, hierarchyLevel: 3, behaviorProfile: 'leader' },
    { role: 'knight', count: 4, hierarchyLevel: 2, behaviorProfile: 'patrol' },
    { role: 'acolyte', count: 6, hierarchyLevel: 1, behaviorProfile: 'support' }
  ],
  syndicate: [
    { role: 'boss', count: 1, hierarchyLevel: 3, behaviorProfile: 'scheming' },
    { role: 'enforcer', count: 3, hierarchyLevel: 2, behaviorProfile: 'guard' },
    { role: 'thief', count: 6, hierarchyLevel: 1, behaviorProfile: 'stealth' }
  ],
  militia: [
    { role: 'commander', count: 1, hierarchyLevel: 3, behaviorProfile: 'command' },
    { role: 'sergeant', count: 3, hierarchyLevel: 2, behaviorProfile: 'drill' },
    { role: 'soldier', count: 8, hierarchyLevel: 1, behaviorProfile: 'patrol' }
  ],
  cult: [
    { role: 'high_priest', count: 1, hierarchyLevel: 3, behaviorProfile: 'ritual' },
    { role: 'cultist', count: 5, hierarchyLevel: 2, behaviorProfile: 'worship' },
    { role: 'novice', count: 7, hierarchyLevel: 1, behaviorProfile: 'initiate' }
  ]
}
class NPCPopulation {
  static generate(type: FactionType): FactionNPC[] {
    const npcs: List[FactionNPC] = []
    let idCounter = 0
    for (const npcDef of baseNPCs[type]) {
      for (let i = 0; i < npcDef.count; i++) {
        npcs.push({
          id: `${npcDef.role}_${idCounter++}`,
          role: npcDef.role,
          hierarchyLevel: npcDef.hierarchyLevel,
          behaviorProfile: npcDef.behaviorProfile
        })
      }
    }
    return npcs
  }
} 