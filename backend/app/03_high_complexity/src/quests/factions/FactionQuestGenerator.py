from typing import Any, Dict, List



class FactionQuestGenerator {
  private baseTemplates: Map<string, QuestTemplate> = new Map()
  private config: FactionQuestGeneratorConfig
  constructor(
    private factionSystem: FactionQuestSystem,
    private consequenceSystem: ConsequenceSystem,
    config: Partial<FactionQuestGeneratorConfig> = {}
  ) {
    this.config = this.initializeConfig(config)
  }
  /**
   * Generate a faction-specific quest template
   */
  generateFactionQuest(
    baseTemplate: QuestTemplate,
    faction: FactionProfile
  ): FactionQuestTemplate {
    const factionQuest: FactionQuestTemplate = {
      ...baseTemplate,
      factionId: faction.id,
      factionRequirements: this.generateFactionRequirements(faction),
      factionRewards: this.generateFactionRewards(faction, baseTemplate),
      factionObjectives: this.generateFactionObjectives(faction, baseTemplate),
      competingFactions: this.generateCompetingFactions(faction)
    }
    this.applyFactionModifiers(factionQuest, faction)
    this.addFactionDialogue(factionQuest, faction)
    return factionQuest
  }
  /**
   * Register a base quest template
   */
  registerBaseTemplate(template: QuestTemplate): void {
    this.baseTemplates.set(template.id, template)
  }
  /**
   * Get all available base templates
   */
  getBaseTemplates(): QuestTemplate[] {
    return Array.from(this.baseTemplates.values())
  }
  private initializeConfig(
    partialConfig: Partial<FactionQuestGeneratorConfig>
  ): FactionQuestGeneratorConfig {
    return {
      baseTemplateModifiers: Dict[str, Any],
      factionSpecificModifiers: Dict[str, Any],
        [FactionType.WARRIORS]: {
          difficultyMultiplier: 1.2,
          rewardMultiplier: 1.0,
          preferredObjectiveTypes: ['combat', 'exploration']
        },
        [FactionType.SCHOLARS]: {
          difficultyMultiplier: 0.9,
          rewardMultiplier: 1.1,
          preferredObjectiveTypes: ['exploration', 'diplomacy']
        },
        [FactionType.MYSTICS]: {
          difficultyMultiplier: 1.1,
          rewardMultiplier: 1.0,
          preferredObjectiveTypes: ['stealth', 'exploration']
        },
        [FactionType.OUTLAWS]: {
          difficultyMultiplier: 1.2,
          rewardMultiplier: 1.3,
          preferredObjectiveTypes: ['stealth', 'combat']
        },
        ...partialConfig.factionSpecificModifiers
      },
      competingQuestProbability: 0.3,
      specialRewardProbability: 0.2,
      ...partialConfig
    }
  }
  private generateFactionRequirements(
    faction: FactionProfile
  ): FactionQuestTemplate['factionRequirements'] {
    return {
      minimumStanding: 0, 
      maximumStanding: 100,
      requiredTier: faction.tier > 0 ? faction.tier - 1 : undefined,
      specialRequirements: faction.specialResources.length > 0 
        ? [faction.specialResources[Math.floor(Math.random() * faction.specialResources.length)]]
        : undefined
    }
  }
  private generateFactionRewards(
    faction: FactionProfile,
    baseTemplate: QuestTemplate
  ): FactionQuestTemplate['factionRewards'] {
    const baseStandingGain = Math.ceil(baseTemplate.difficulty * 10)
    const hasSpecialReward = Math.random() < this.config.specialRewardProbability
    return {
      standingGain: baseStandingGain,
      specialRewards: hasSpecialReward && faction.specialResources.length > 0
        ? [faction.specialResources[Math.floor(Math.random() * faction.specialResources.length)]]
        : undefined
    }
  }
  private generateFactionObjectives(
    faction: FactionProfile,
    baseTemplate: QuestTemplate
  ): FactionObjective[] {
    const factionModifiers = this.config.factionSpecificModifiers[faction.id]
    const objectives: List[FactionObjective] = []
    for (const baseObjective of baseTemplate.objectives) {
      const objective: FactionObjective = {
        type: this.mapObjectiveType(baseObjective.type, factionModifiers.preferredObjectiveTypes),
        difficulty: baseObjective.difficulty * factionModifiers.difficultyMultiplier,
        description: this.generateObjectiveDescription(baseObjective, faction),
        factionImpact: Dict[str, Any]
      }
      if (baseObjective.alternatives) {
        objective.alternatives = baseObjective.alternatives.map(alt => ({
          type: this.mapObjectiveType(alt.type, factionModifiers.preferredObjectiveTypes),
          description: this.generateObjectiveDescription(alt, faction),
          difficulty: alt.difficulty * factionModifiers.difficultyMultiplier,
          factionImpact: Dict[str, Any]
        }))
      }
      objectives.push(objective)
    }
    return objectives
  }
  private generateCompetingFactions(
    faction: FactionProfile
  ): FactionQuestTemplate['competingFactions'] {
    if (Math.random() >= this.config.competingQuestProbability) {
      return undefined
    }
    const competingFactions: FactionQuestTemplate['competingFactions'] = []
    const opposingFactions = Array.from(faction.relationships.entries())
      .filter(([_, standing]) => standing < -30)
      .map(([factionId]) => factionId)
    if (opposingFactions.length > 0) {
      const selectedFaction = opposingFactions[Math.floor(Math.random() * opposingFactions.length)]
      competingFactions.push({
        factionId: selectedFaction,
        standingImpact: -20 
      })
    }
    return competingFactions
  }
  private applyFactionModifiers(
    quest: FactionQuestTemplate,
    faction: FactionProfile
  ): void {
    const factionModifiers = this.config.factionSpecificModifiers[faction.id]
    quest.difficulty *= factionModifiers.difficultyMultiplier
    quest.rewards.gold *= factionModifiers.rewardMultiplier
    quest.rewards.experience *= factionModifiers.rewardMultiplier
    if (faction.specialResources.length > 0 && Math.random() < this.config.specialRewardProbability) {
      quest.rewards.items.push(
        faction.specialResources[Math.floor(Math.random() * faction.specialResources.length)]
      )
    }
    if (faction.questPreferences[quest.type as QuestType] > 0.7) {
      quest.requirements.minimumReputation *= 0.8 
    }
  }
  private addFactionDialogue(
    quest: FactionQuestTemplate,
    faction: FactionProfile
  ): void {
    quest.dialogue = quest.dialogue.map(dialogue => {
      const baseDialogue: QuestDialogue = {
        npcId: dialogue.npcId,
        text: dialogue.text,
        variations: [
          ...(dialogue.variations || []),
          this.generateFactionDialogueVariation(faction, 'low', 0),
          this.generateFactionDialogueVariation(faction, 'medium', 30),
          this.generateFactionDialogueVariation(faction, 'high', 70)
        ]
      }
      return baseDialogue
    })
  }
  private mapObjectiveType(
    baseType: str,
    preferredTypes: List[string]
  ): FactionObjective['type'] {
    const typeMap: Record<string, FactionObjective['type']> = {
      'collect': 'trade',
      'kill': 'combat',
      'explore': 'exploration',
      'talk': 'diplomacy',
      'infiltrate': 'stealth'
    }
    return typeMap[baseType] || preferredTypes[0] || 'diplomacy'
  }
  private generateObjectiveDescription(
    objective: Dict[str, Any],
    faction: FactionProfile
  ): str {
    return `${objective.description} for the ${faction.name}`
  }
  private generateFactionDialogueVariation(
    faction: FactionProfile,
    level: 'low' | 'medium' | 'high',
    threshold: float
  ): DialogueVariation {
    const tones = {
      low: faction.values.power > 0.5 ? 'dismissive' : 'neutral',
      medium: faction.values.tradition > 0.5 ? 'respectful' : 'friendly',
      high: faction.values.honor > 0.5 ? 'reverent' : 'enthusiastic'
    }
    return {
      standingThreshold: threshold,
      text: `[${level} standing dialogue placeholder]`,
      tone: tones[level]
    }
  }
} 