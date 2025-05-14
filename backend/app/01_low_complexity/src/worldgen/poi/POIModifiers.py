from typing import Any, List



const modifiers: List[POIModifier] = [
  {
    id: 'bandit_attack',
    description: 'Recently attacked by bandits. Loot is reduced, hostile NPCs present.',
    lootModifier: loot => loot.filter(item => item !== 'coins'),
    npcModifier: npcs => [...npcs, 'bandit']
  },
  {
    id: 'festival',
    description: 'A festival is underway. More food and friendly NPCs.',
    lootModifier: loot => [...loot, 'festival_food'],
    npcModifier: npcs => [...npcs, 'performer', 'villager']
  },
  {
    id: 'quest_item',
    description: 'Contains a quest-relevant item.',
    lootModifier: loot => [...loot, 'quest_item'],
    questHook: 'find_the_relic'
  }
]
class POIModifiers {
  static getAll(): POIModifier[] {
    return modifiers
  }
} 