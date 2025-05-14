import { QuestTemplate, QuestObjective } from '../types';
import { ConsequenceSystem, WorldState, Consequence } from '../consequences/ConsequenceSystem';
import { ConsequenceSeverity } from '../consequences/ConsequenceSystem';
import { FactionType, FactionProfile, FactionStanding } from '../../types/factions/faction';
import { FactionQuestTemplate, FactionQuestConfig } from './types';
import { WorldStateChange } from '../consequences/ConsequenceSystem';

/**
 * Configuration for the faction quest system
 */
export interface FactionQuestConfig {
  reputationGainRate: number;
  reputationLossRate: number;
  tierThresholds: number[];
  competingQuestProbability: number;
  mutuallyExclusiveThreshold: number;
  minimumStandingForSpecialQuests: number;
  standingGainMultiplier: number;
}

interface DialoguePhrase {
  type: string;
  text: string;
}

interface DialogueVariation {
  text: string;
  tone: string;
  additionalPhrases: DialoguePhrase[];
}

/**
 * Manages faction-specific quest variations and relationships
 */
export class FactionQuestSystem {
  private factions: Map<FactionType, FactionProfile> = new Map();
  private quests: Map<string, FactionQuestTemplate> = new Map();
  private playerStandings: Map<string, FactionStanding> = new Map();
  private config: FactionQuestConfig;
  private consequenceSystem: ConsequenceSystem;

  constructor(
    config: FactionQuestConfig,
    consequenceSystem: ConsequenceSystem
  ) {
    this.config = config;
    this.consequenceSystem = consequenceSystem;
  }

  /**
   * Register a new faction in the system
   */
  registerFaction(profile: FactionProfile): void {
    this.factions.set(profile.id, profile);
    
    // Initialize relationships with other factions
    for (const [otherId, standing] of Object.entries(profile.relationships)) {
      const otherFaction = this.factions.get(otherId);
      if (otherFaction) {
        otherFaction.relationships[profile.id] = standing;
      }
    }
  }

  /**
   * Initialize or update player standing with a faction
   */
  initializePlayerStanding(playerId: string, factionId: FactionType): void {
    const standing: FactionStanding = {
      reputation: 0,
      tier: 0,
      completedQuests: 0,
      failedQuests: 0,
      specialActions: []
    };

    this.playerStandings.set(playerId, standing);
  }

  /**
   * Modify a quest template based on faction preferences
   */
  modifyQuestForFaction(quest: QuestTemplate, factionId: FactionType): QuestTemplate {
    const faction = this.factions.get(factionId);
    if (!faction) return quest;

    // Apply faction-specific modifications
    const modifiedQuest = { ...quest };

    // Modify rewards based on faction preferences
    const rewardMultiplier = faction.questModifiers.rewardMultipliers[quest.type] ?? 1;
    modifiedQuest.rewards = {
      ...quest.rewards,
      gold: quest.rewards.gold * rewardMultiplier,
      experience: quest.rewards.experience * rewardMultiplier
    };

    // Adjust difficulty based on faction modifiers
    const difficultyModifier = faction.questModifiers.difficultyModifiers[quest.type] ?? 1;
    modifiedQuest.difficulty *= difficultyModifier;

    // Modify objectives
    modifiedQuest.objectives = this.adjustObjectives(quest.objectives, faction);

    // Modify dialogue
    modifiedQuest.dialogue = this.addFactionDialogue(quest.dialogue, faction);

    // Add faction-specific consequences
    const baseSeverity = quest.difficulty;
    const factionConsequences = this.generateFactionConsequences(faction, baseSeverity);
    const opposingConsequences = this.generateOpposingConsequences(faction, baseSeverity);

    modifiedQuest.consequences = {
      success: [
        ...factionConsequences.success,
        ...opposingConsequences.success
      ],
      failure: [
        ...factionConsequences.failure,
        ...opposingConsequences.failure
      ]
    };

    return modifiedQuest;
  }

  /**
   * Generate competing quests from opposing factions
   */
  generateCompetingQuests(
    originalQuest: QuestTemplate,
    factionId: string
  ): QuestTemplate[] {
    const faction = this.factions.get(this.getFactionById(factionId));
    if (!faction) return [];

    const competingQuests: QuestTemplate[] = [];
    
    // Find opposing factions
    const opposingFactions = Array.from(this.factions.values())
      .filter(other => 
        other.id !== faction.id &&
        faction.relationships[other.id] <= -this.config.mutuallyExclusiveThreshold
      );

    // Generate competing quests
    for (const opposing of opposingFactions) {
      if (Math.random() < this.config.competingQuestProbability) {
        const competingQuest = this.createOpposingQuest(
          originalQuest,
          opposing
        );
        competingQuests.push(competingQuest);
      }
    }

    return competingQuests;
  }

  /**
   * Update faction standings based on quest outcome
   */
  updateStandings(
    questId: string,
    factionId: string,
    outcome: 'success' | 'failure' | 'abandoned',
    choices: string[]
  ): void {
    const standing = this.playerStandings.get(factionId);
    if (!standing) return;

    const faction = this.factions.get(this.getFactionById(factionId));
    if (!faction) return;

    // Update basic stats
    if (outcome === 'success') {
      standing.completedQuests++;
      this.adjustReputation(standing, this.config.reputationGainRate);
    } else if (outcome === 'failure') {
      standing.failedQuests++;
      this.adjustReputation(standing, -this.config.reputationLossRate);
    }

    // Record special actions
    for (const choice of choices) {
      if (this.isSpecialAction(choice, faction)) {
        standing.specialActions.push({
          type: choice,
          impact: this.calculateActionImpact(choice, faction),
          timestamp: Date.now()
        });
      }
    }

    // Update tier progress
    this.updateTierProgress(standing);

    // Apply consequences to other factions
    this.applyInterFactionConsequences(
      factionId,
      outcome,
      choices
    );
  }

  /**
   * Check if a quest is available based on faction standing
   */
  isQuestAvailable(
    template: QuestTemplate,
    factionId: string
  ): boolean {
    const standing = this.playerStandings.get(factionId);
    if (!standing) return false;

    const faction = this.factions.get(this.getFactionById(factionId));
    if (!faction) return false;

    // Check basic reputation requirement
    if (template.minimumReputation &&
        standing.reputation < template.minimumReputation) {
      return false;
    }

    // Check tier requirement
    if (template.minimumTier &&
        standing.tier < template.minimumTier) {
      return false;
    }

    // Check for conflicting quests
    if (this.hasConflictingActiveQuests(template, factionId)) {
      return false;
    }

    // Check special requirements
    return this.meetsSpecialRequirements(template, faction, standing);
  }

  /**
   * Get all available quests for a faction
   */
  getAvailableQuests(factionId: string): QuestTemplate[] {
    const standing = this.playerStandings.get(factionId);
    if (!standing) return [];

    const faction = this.factions.get(this.getFactionById(factionId));
    if (!faction) return [];

    // Get base quests
    const baseQuests = this.getBaseQuestsForTier(standing.tier);
    
    // Filter and modify based on availability
    return baseQuests
      .filter(quest => this.isQuestAvailable(quest, factionId))
      .map(quest => this.modifyQuestForFaction(quest, factionId));
  }

  /**
   * Get a player's standing with all factions
   */
  getPlayerStandings(playerId: string): Map<FactionType, number> {
    const standings = new Map<FactionType, number>();
    
    // Get all faction standings for the player
    for (const [factionId, faction] of this.factions) {
      const standing = this.playerStandings.get(playerId);
      if (standing) {
        standings.set(factionId as FactionType, standing.reputation);
      }
    }
    
    return standings;
  }

  /**
   * Get a player's standing with a specific faction
   */
  public async getFactionStanding(playerId: string, faction: FactionType): Promise<number> {
    // TODO: Implement actual faction standing retrieval from database/state
    // For now, return a default neutral value
    return 0;
  }

  /**
   * Modify a player's standing with a specific faction
   */
  public async modifyFactionStanding(
    playerId: string,
    faction: FactionType,
    change: number
  ): Promise<void> {
    // TODO: Implement actual faction standing modification in database/state
    console.log(`Modifying faction standing for player ${playerId} with ${faction} by ${change}`);
  }

  // Private helper methods

  private adjustObjectives(
    objectives: QuestTemplate['objectives'],
    faction: FactionProfile
  ): QuestTemplate['objectives'] {
    return objectives.map(objective => ({
      ...objective,
      difficulty: objective.difficulty * (
        faction.questModifiers.difficultyModifiers[objective.type] ?? 1
      )
    }));
  }

  private adjustRewards(
    rewards: QuestTemplate['rewards'],
    faction: FactionProfile
  ): QuestTemplate['rewards'] {
    const modified = { ...rewards };

    // Apply faction-specific multipliers
    for (const [type, multiplier] of Object.entries(faction.questModifiers.rewardMultipliers)) {
      if (modified[type]) {
        modified[type] *= multiplier;
      }
    }

    // Add faction-specific rewards
    if (faction.specialResources.length > 0) {
      modified.items = [
        ...(modified.items || []),
        faction.specialResources[
          Math.floor(Math.random() * faction.specialResources.length)
        ]
      ];
    }

    return modified;
  }

  private addFactionDialogue(
    dialogue: QuestTemplate['dialogue'],
    faction: FactionProfile
  ): QuestTemplate['dialogue'] {
    return dialogue.map(d => ({
      ...d,
      text: this.addFactionFlavor(d.text, faction),
      variations: d.variations?.map(v => this.addFactionFlavor(v, faction))
    }));
  }

  private addFactionFlavor(text: string, faction: FactionProfile): string {
    // Add faction-specific terminology and style
    let modified = text;

    if (faction.values.tradition > 0.7) {
      modified = modified.replace(/(\w+)/g, match => {
        // Add traditional terms
        const traditionalTerms: Record<string, string> = {
          'money': 'gold',
          'payment': 'compensation',
          'job': 'quest',
          // Add more mappings as needed
        };
        return traditionalTerms[match.toLowerCase()] || match;
      });
    }

    return modified;
  }

  private addFactionConsequences(
    consequences: QuestTemplate['consequences'],
    faction: FactionProfile
  ): QuestTemplate['consequences'] {
    return {
      success: consequences.success.map(consequence => ({
        ...consequence,
        description: this.addFactionFlavor(consequence.description, faction)
      })),
      failure: consequences.failure.map(consequence => ({
        ...consequence,
        description: this.addFactionFlavor(consequence.description, faction)
      }))
    };
  }

  createOpposingQuest(
    original: FactionQuestTemplate,
    opposingFaction: FactionProfile
  ): FactionQuestTemplate {
    // Create a quest that directly opposes the original
    return {
      ...original,
      id: `opposing_${original.id}_${opposingFaction.id}`,
      objectives: this.createOpposingObjectives(
        original.objectives,
        opposingFaction
      ),
      rewards: this.adjustRewards(original.rewards, opposingFaction),
      consequences: this.createOpposingConsequences(
        original.consequences || [],
        opposingFaction
      ),
      factionId: opposingFaction.id,
      factionRequirements: {
        minimumStanding: 0,
        maximumStanding: 100
      },
      factionRewards: this.generateOpposingRewards(original, opposingFaction),
      factionObjectives: this.generateOpposingObjectives(original, opposingFaction)
    };
  }

  private adjustReputation(
    standing: FactionStanding,
    change: number
  ): void {
    standing.reputation = Math.max(
      -100,
      Math.min(100, standing.reputation + change)
    );
  }

  private updateTierProgress(standing: FactionStanding): void {
    // Check if ready for tier advancement
    if (standing.reputation >= 100 && standing.tier < 5) {
      standing.tier++;
      standing.reputation = 0;
    }
  }

  private applyInterFactionConsequences(
    factionId: string,
    outcome: string,
    choices: string[]
  ): void {
    const faction = this.factions.get(this.getFactionById(factionId));
    if (!faction) return;

    // Apply consequences to related factions
    for (const [otherId, relationship] of Object.entries(faction.relationships)) {
      const impact = this.calculateInterFactionImpact(
        relationship,
        outcome,
        choices
      );

      if (impact !== 0) {
        const consequence: Consequence = {
          id: `inter_faction_${factionId}_${otherId}_${Date.now()}`,
          type: 'faction_reputation',
          severity: this.getImpactSeverity(impact),
          description: `Impact on ${otherId} from ${factionId} quest ${outcome}`,
          trigger: { type: 'immediate' },
          effects: {
            immediate: (state: WorldState) => {
              state.factionStandings[otherId] += impact;
            }
          }
        };

        this.consequenceSystem.addConsequence(consequence);
      }
    }
  }

  private isSpecialAction(
    choice: string,
    faction: FactionProfile
  ): boolean {
    // Check if the choice is considered special for this faction
    return faction.specialResources.includes(choice) ||
           choice.startsWith(`${faction.id}_special_`);
  }

  private calculateActionImpact(
    choice: string,
    faction: FactionProfile
  ): number {
    let multiplier = 1.0;

    // Adjust impact based on faction values
    if (choice.includes('diplomatic')) {
      multiplier *= (1 + faction.values.tradition * 0.01);
    } else if (choice.includes('aggressive')) {
      multiplier *= (1 + faction.values.power * 0.01);
    } else if (choice.includes('trade')) {
      multiplier *= (1 + faction.values.wealth * 0.01);
    }

    // Base impact value
    const baseImpact = 10;

    return baseImpact * multiplier;
  }

  private hasConflictingActiveQuests(
    template: QuestTemplate,
    factionId: string
  ): boolean {
    // Check for conflicts with active quests
    return false; // Placeholder
  }

  private meetsSpecialRequirements(
    template: QuestTemplate,
    faction: FactionProfile,
    standing: FactionStanding
  ): boolean {
    // Check special requirements like items, skills, or previous quests
    return true; // Placeholder
  }

  private getBaseQuestsForTier(tier: number): QuestTemplate[] {
    // Get base quests for the given tier
    return this.questTemplates.filter(quest => {
      const minTier = quest.minimumTier ?? 0;
      return tier >= minTier;
    });
  }

  private generateQuestsForFaction(
    faction: FactionProfile,
    standing: FactionStanding
  ): QuestTemplate[] {
    // Get base quests for the current tier
    const baseQuests = this.getBaseQuestsForTier(standing.tier);
    
    // Filter and modify based on faction preferences
    return baseQuests
      .filter(quest => this.checkQuestRequirements(quest, standing))
      .map(quest => this.modifyQuestForFaction(quest, faction.id));
  }

  private generateOpposingQuests(
    faction: FactionProfile,
    standing: FactionStanding
  ): QuestTemplate[] {
    const opposingFactions = this.getOpposingFactions(faction);
    
    return opposingFactions.flatMap(opposing => 
      this.generateQuestsForFaction(opposing, {
        ...standing,
        reputation: -standing.reputation // Invert reputation for opposing factions
      })
    );
  }

  private generateAlternatives(
    objective: QuestTemplate['objectives'][0],
    faction: FactionProfile
  ): any[] {
    const alternatives = [];
    
    // Generate alternatives based on faction values and objective type
    switch (objective.type) {
      case 'fetch':
        // Trade-based alternative for wealth-focused factions
        if (faction.values.wealth > 0.5) {
          alternatives.push({
            type: 'trade',
            difficulty: objective.difficulty * 0.8,
            description: `Purchase or trade for the required items`,
            requirements: {
              gold: objective.difficulty * 100,
              tradingSkill: Math.floor(objective.difficulty / 2)
            }
          });
        }
        
        // Combat-based alternative for power-focused factions
        if (faction.values.power > 0.5) {
          alternatives.push({
            type: 'combat',
            difficulty: objective.difficulty * 1.2,
            description: `Defeat enemies to obtain the items`,
            requirements: {
              combatLevel: objective.difficulty + 2,
              equipment: ['weapon', 'armor']
            }
          });
        }
        break;

      case 'diplomacy':
        // Knowledge-based alternative for scholarly factions
        if (faction.values.knowledge > 0.5) {
          alternatives.push({
            type: 'research',
            difficulty: objective.difficulty * 0.9,
            description: `Research and present compelling evidence`,
            requirements: {
              researchSkill: objective.difficulty,
              knowledgeItems: ['relevant_documents', 'historical_records']
            }
          });
        }
        
        // Honor-based alternative for traditional factions
        if (faction.values.tradition > 0.5) {
          alternatives.push({
            type: 'ritual',
            difficulty: objective.difficulty * 1.1,
            description: `Complete traditional diplomatic rituals`,
            requirements: {
              traditionKnowledge: objective.difficulty,
              ritualItems: ['ceremonial_items']
            }
          });
        }
        break;

      case 'combat':
        // Stealth-based alternative for progress-focused factions
        if (faction.values.progress > 0.5) {
          alternatives.push({
            type: 'stealth',
            difficulty: objective.difficulty * 1.1,
            description: `Complete the objective without direct confrontation`,
            requirements: {
              stealthSkill: objective.difficulty + 1,
              equipment: ['stealth_gear']
            }
          });
        }
        
        // Strategy-based alternative for knowledge-focused factions
        if (faction.values.knowledge > 0.5) {
          alternatives.push({
            type: 'tactical',
            difficulty: objective.difficulty * 0.9,
            description: `Use tactical advantages to minimize combat`,
            requirements: {
              tacticalSkill: objective.difficulty,
              preparation: ['battle_plans', 'terrain_advantage']
            }
          });
        }
        break;
    }

    return alternatives;
  }

  private generateFactionDialogue(
    entry: QuestTemplate['dialogue'][0],
    faction: FactionProfile
  ): DialogueVariation {
    // Generate dialogue variations based on faction values
    const variations: DialogueVariation = {
      text: entry.text,
      tone: this.getFactionDialogueTone(faction),
      additionalPhrases: []
    };

    // Add value-specific phrases
    if (faction.values.honor > 0.5) {
      variations.additionalPhrases.push({
        type: 'honorable',
        text: `Remember, our honor depends on this.`
      });
    }

    if (faction.values.wealth > 0.5) {
      variations.additionalPhrases.push({
        type: 'profit',
        text: `This venture will be quite profitable.`
      });
    }

    if (faction.values.knowledge > 0.5) {
      variations.additionalPhrases.push({
        type: 'wisdom',
        text: `This knowledge will serve us well.`
      });
    }

    if (faction.values.tradition > 0.5) {
      variations.additionalPhrases.push({
        type: 'traditional',
        text: `We must uphold our ancient traditions.`
      });
    }

    if (faction.values.progress > 0.5) {
      variations.additionalPhrases.push({
        type: 'progressive',
        text: `This will advance our cause significantly.`
      });
    }

    return variations;
  }

  private getFactionDialogueTone(faction: FactionProfile): string {
    // Determine dialogue tone based on faction values
    if (faction.values.honor > 0.7) return 'formal';
    if (faction.values.wealth > 0.7) return 'businesslike';
    if (faction.values.power > 0.7) return 'commanding';
    if (faction.values.knowledge > 0.7) return 'scholarly';
    if (faction.values.tradition > 0.7) return 'reverent';
    if (faction.values.progress > 0.7) return 'innovative';
    return 'neutral';
  }

  private createOpposingObjectives(
    objectives: QuestObjective[],
    opposingFaction: FactionProfile
  ): QuestObjective[] {
    return objectives.map(obj => ({
      ...obj,
      id: `opposing_${obj.id}_${opposingFaction.id}`,
      description: this.reverseObjectiveDescription(obj.description, opposingFaction)
    }));
  }

  private reverseObjectiveDescription(
    description: string,
    opposingFaction: FactionProfile
  ): string {
    // Simple reversal - in practice you'd want more sophisticated logic
    return description
      .replace(/collect/i, 'prevent collection of')
      .replace(/kill/i, 'protect')
      .replace(/destroy/i, 'defend')
      .replace(/capture/i, 'maintain control of');
  }

  private createOpposingConsequences(
    consequences: WorldStateChange[],
    opposingFaction: FactionProfile
  ): WorldStateChange[] {
    return consequences.map(consequence => ({
      ...consequence,
      value: -consequence.value, // Reverse the impact
      description: `${opposingFaction.name} prevents: ${consequence.description}`
    }));
  }

  private generateOpposingRewards(
    original: FactionQuestTemplate,
    opposingFaction: FactionProfile
  ): FactionQuestTemplate['factionRewards'] {
    return {
      standingGain: original.factionRewards.standingGain,
      reputationGain: original.factionRewards.reputationGain,
      specialRewards: original.factionRewards.specialRewards
    };
  }

  private generateOpposingObjectives(
    original: FactionQuestTemplate,
    opposingFaction: FactionProfile
  ): QuestObjective[] {
    return original.factionObjectives.map(obj => ({
      ...obj,
      id: `opposing_${obj.id}_${opposingFaction.id}`,
      description: this.reverseObjectiveDescription(obj.description, opposingFaction)
    }));
  }

  /**
   * Get a faction by ID
   */
  getFaction(factionId: FactionType): FactionProfile | undefined {
    return this.factions.get(factionId);
  }

  /**
   * Get all registered factions
   */
  getAllFactions(): FactionProfile[] {
    return Array.from(this.factions.values());
  }

  /**
   * Get factions that oppose the given faction
   */
  getOpposingFactions(faction: FactionProfile | FactionType): FactionProfile[] {
    const factionProfile = typeof faction === 'string' 
      ? this.factions.get(faction)
      : faction;

    if (!factionProfile) {
      throw new Error(`Faction not found: ${faction}`);
    }

    return Array.from(this.factions.values())
      .filter(other => 
        other.id !== factionProfile.id &&
        (factionProfile.relationships.get(other.id) || 0) <= -this.config.mutuallyExclusiveThreshold
      );
  }

  /**
   * Check if a faction meets the requirements for a quest
   */
  checkFactionRequirements(
    faction: FactionProfile,
    quest: FactionQuestTemplate
  ): boolean {
    const { factionRequirements } = quest;

    // Check standing requirements
    if (faction.standing < factionRequirements.minimumStanding ||
        faction.standing > factionRequirements.maximumStanding) {
      return false;
    }

    // Check reputation if specified
    if (factionRequirements.minimumReputation !== undefined &&
        (quest.requirements.minimumReputation || 0) < factionRequirements.minimumReputation) {
      return false;
    }

    // Check tier if specified
    if (factionRequirements.minimumTier !== undefined &&
        faction.tier < factionRequirements.minimumTier) {
      return false;
    }

    return true;
  }

  /**
   * Get all quests available to a faction
   */
  getAvailableQuests(faction: FactionProfile): FactionQuestTemplate[] {
    return Array.from(this.quests.values())
      .filter(quest => this.checkFactionRequirements(faction, quest));
  }

  /**
   * Register a new faction quest
   */
  registerQuest(quest: FactionQuestTemplate): void {
    this.quests.set(quest.id, quest);
  }

  /**
   * Get a specific quest by ID
   */
  getQuest(id: string): FactionQuestTemplate | undefined {
    return this.quests.get(id);
  }

  /**
   * Update faction relationships based on quest completion
   */
  updateFactionRelationships(
    completedQuest: FactionQuestTemplate,
    successfulFaction: FactionProfile
  ): void {
    const questFaction = this.factions.get(completedQuest.factionId);
    if (!questFaction) return;

    // Update relationship between quest faction and successful faction
    const currentRelationship = questFaction.relationships.get(successfulFaction.id) || 0;
    const relationshipChange = completedQuest.factionRewards.standingGain * this.config.standingGainMultiplier;

    questFaction.relationships.set(
      successfulFaction.id,
      currentRelationship + (questFaction.id === successfulFaction.id ? relationshipChange : -relationshipChange)
    );
  }

  private calculateInterFactionImpact(
    relationship: number,
    outcome: string,
    choices: string[]
  ): number {
    // Calculate how actions with one faction affect others
    return 0; // Placeholder
  }

  private getImpactSeverity(impact: number): ConsequenceSeverity {
    if (Math.abs(impact) > 0.75) return 'critical';
    if (Math.abs(impact) > 0.5) return 'major';
    if (Math.abs(impact) > 0.25) return 'moderate';
    return 'minor';
  }

  initializeFaction(
    id: FactionType,
    name: string,
    description: string,
    values: FactionProfile['values']
  ): void {
    const faction: FactionProfile = {
      id,
      name,
      description,
      values,
      specialResources: [],
      questPreferences: {
        combat: 0,
        diplomacy: 0,
        stealth: 0,
        trade: 0,
        exploration: 0
      },
      questModifiers: {
        rewardMultipliers: {},
        difficultyModifiers: {},
        objectivePreferences: {}
      },
      relationships: new Map(),
      tier: 0,
      reputation: 0
    };

    this.factions.set(id, faction);
  }

  setFactionRelationship(
    factionId: FactionType,
    otherFactionId: FactionType,
    value: number
  ): void {
    const faction = this.factions.get(factionId);
    const otherFaction = this.factions.get(otherFactionId);
    
    if (faction && otherFaction) {
      faction.relationships.set(otherFactionId, value);
      otherFaction.relationships.set(factionId, value);
    }
  }

  getFactionRelationship(
    factionId: FactionType,
    otherFactionId: FactionType
  ): number {
    const faction = this.factions.get(factionId);
    if (!faction) return 0;

    return faction.relationships.get(otherFactionId) ?? 0;
  }

  private getFactionById(factionId: string): FactionType {
    try {
      return FactionType[factionId.toUpperCase() as keyof typeof FactionType];
    } catch (e) {
      throw new Error(`Invalid faction ID: ${factionId}`);
    }
  }

  private checkQuestRequirements(
    quest: QuestTemplate,
    standing: FactionStanding
  ): boolean {
    // Check reputation requirement
    if (quest.requirements.minimumReputation &&
        standing.reputation < quest.requirements.minimumReputation) {
      return false;
    }

    // Check tier requirement
    if (quest.minimumTier &&
        standing.tier < quest.minimumTier) {
      return false;
    }

    return true;
  }

  private generateOpposingTitle(originalTitle: string, opposingFaction: FactionProfile): string {
    const prefixes = [
      'Counter:',
      'Oppose:',
      'Thwart:',
      'Prevent:',
      'Stop:'
    ];
    const prefix = prefixes[Math.floor(Math.random() * prefixes.length)];
    return `${prefix} ${originalTitle}`;
  }
} 