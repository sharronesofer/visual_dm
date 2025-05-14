import { ApiService, ApiResponse } from './ApiService';
import {
  CharacterData,
  Attributes,
  Equipment,
  Skill,
  StarterKit,
  DerivedStats,
  Background,
} from '../types/character';

export interface CharacterBuilderState {
  characterName: string | null;
  attributes: Attributes;
  selectedFeats: string[];
  selectedSkills: string[];
  skillPoints: number;
  starterKit: Equipment[];
  level: number;
  gold: number;
  race?: string;
  class?: string;
  background?: string;
  backgroundFeature?: {
    name: string;
    description: string;
  };
  toolProficiencies: string[];
  languagesKnown: number;
  traits?: string[];
  features?: string[];
  derivedStats: DerivedStats;
}

class CharacterBuilderService {
  private static instance: CharacterBuilderService;
  private apiService: ApiService;
  private state: CharacterBuilderState;

  private constructor() {
    this.apiService = ApiService.getInstance();
    this.state = {
      characterName: null,
      attributes: {
        strength: 8,
        dexterity: 8,
        constitution: 8,
        intelligence: 8,
        wisdom: 8,
        charisma: 8,
      },
      selectedFeats: [],
      selectedSkills: [],
      skillPoints: 0,
      starterKit: [],
      level: 1,
      gold: 0,
      toolProficiencies: [],
      languagesKnown: 0,
      derivedStats: {
        armorClass: 10,
        initiative: -1,
        hitPoints: 8,
        proficiencyBonus: 2,
        savingThrows: {
          strength: -1,
          dexterity: -1,
          constitution: -1,
          intelligence: -1,
          wisdom: -1,
          charisma: -1,
        },
        passivePerception: 9,
      },
    };
  }

  public static getInstance(): CharacterBuilderService {
    if (!CharacterBuilderService.instance) {
      CharacterBuilderService.instance = new CharacterBuilderService();
    }
    return CharacterBuilderService.instance;
  }

  public async initialize(): Promise<void> {
    const response = await this.apiService.post<void>('/character-builder/initialize');
    if (response.error) {
      throw new Error(response.error.message);
    }
  }

  public async setName(name: string): Promise<void> {
    const response = await this.apiService.post<void>('/character-builder/name', { name });
    if (response.error) {
      throw new Error(response.error.message);
    }
    this.state.characterName = name;
  }

  public async setRace(race: string): Promise<void> {
    const response = await this.apiService.post<void>('/character-builder/race', { race });
    if (response.error) {
      throw new Error(response.error.message);
    }
    this.state.race = race;

    // Update racial traits based on race
    switch (race) {
      case 'Elf':
        this.state.traits = ['Darkvision', 'Keen Senses', 'Fey Ancestry'];
        break;
      case 'Dwarf':
        this.state.traits = ['Darkvision', 'Dwarven Resilience', 'Stonecunning'];
        break;
      // Add other races as needed
    }
  }

  public async setClass(characterClass: string): Promise<void> {
    const response = await this.apiService.post<void>('/character-builder/class', {
      class: characterClass,
    });
    if (response.error) {
      throw new Error(response.error.message);
    }
    this.state.class = characterClass;

    // Update class features based on class
    switch (characterClass) {
      case 'Fighter':
        this.state.features = ['Second Wind', 'Fighting Style'];
        this.state.derivedStats.hitPoints =
          10 + Math.floor((this.state.attributes.constitution - 10) / 2);
        break;
      case 'Wizard':
        this.state.features = ['Spellcasting', 'Arcane Recovery'];
        this.state.derivedStats.hitPoints =
          6 + Math.floor((this.state.attributes.constitution - 10) / 2);
        this.state.derivedStats.spellSaveDC =
          8 + 2 + Math.floor((this.state.attributes.intelligence - 10) / 2);
        this.state.derivedStats.spellAttackBonus =
          2 + Math.floor((this.state.attributes.intelligence - 10) / 2);
        break;
      // Add other classes as needed
    }
  }

  private updateDerivedStats(): void {
    const { attributes, class: characterClass } = this.state;

    // Update basic derived stats
    this.state.derivedStats = {
      ...this.state.derivedStats,
      initiative: Math.floor((attributes.dexterity - 10) / 2),
      armorClass: 10 + Math.floor((attributes.dexterity - 10) / 2),
      savingThrows: {
        strength: Math.floor((attributes.strength - 10) / 2),
        dexterity: Math.floor((attributes.dexterity - 10) / 2),
        constitution: Math.floor((attributes.constitution - 10) / 2),
        intelligence: Math.floor((attributes.intelligence - 10) / 2),
        wisdom: Math.floor((attributes.wisdom - 10) / 2),
        charisma: Math.floor((attributes.charisma - 10) / 2),
      },
      passivePerception: 10 + Math.floor((attributes.wisdom - 10) / 2),
    };

    // Update class-specific stats
    if (characterClass) {
      this.setClass(characterClass); // This will update HP and class-specific stats
    }
  }

  public async setAttribute(attribute: keyof Attributes, value: number): Promise<void> {
    const response = await this.apiService.post<void>('/character-builder/attribute', {
      attribute,
      value,
    });
    if (response.error) {
      throw new Error(response.error.message);
    }
    this.state.attributes[attribute] = value;
    this.updateDerivedStats();
  }

  public async assignSkill(skill: string): Promise<void> {
    const response = await this.apiService.post<void>('/character-builder/skill', { skill });
    if (response.error) {
      throw new Error(response.error.message);
    }
    this.state.selectedSkills.push(skill);
  }

  public async getAvailableStarterKits(): Promise<ApiResponse<StarterKit[]>> {
    return this.apiService.get<StarterKit[]>('/character-builder/starter-kits');
  }

  public async setStarterKit(kitName: string): Promise<void> {
    const response = await this.apiService.post<{
      equipment: Equipment[];
      gold: number;
    }>('/character-builder/starter-kit', { kitName });
    if (response.error) {
      throw new Error(response.error.message);
    }
    this.state.starterKit = response.data.equipment;
    this.state.gold = response.data.gold;
  }

  public async validate(): Promise<boolean> {
    try {
      const response = await this.apiService.get<{ isValid: boolean }>(
        '/character-builder/validate'
      );
      if (response?.error) {
        throw new Error(response.error.message);
      }
      return response?.data?.isValid ?? false;
    } catch (error) {
      throw error;
    }
  }

  public async finalize(): Promise<CharacterData> {
    const response = await this.apiService.post<CharacterData>('/character-builder/finalize');
    if (response.error) {
      throw new Error(response.error.message);
    }
    return response.data;
  }

  public getState(): CharacterBuilderState {
    return { ...this.state };
  }

  public async getAvailableSkills(): Promise<ApiResponse<Skill[]>> {
    return this.apiService.get<Skill[]>('/character-builder/skills');
  }

  public async validateStarterKit(
    kitId: string,
    characterClass: string
  ): Promise<ApiResponse<{ isValid: boolean }>> {
    return this.apiService.post<{ isValid: boolean }>('/character-builder/validate-kit', {
      kitId,
      characterClass,
    });
  }

  public async getBackgrounds(): Promise<Background[]> {
    const response = await this.apiService.get<Background[]>('/character-builder/backgrounds');
    if (response.error) {
      throw new Error(response.error.message);
    }
    return response.data;
  }

  public async setBackground(name: string): Promise<void> {
    const response = await this.apiService.post<void>('/character-builder/background', { name });
    if (response.error) {
      throw new Error(response.error.message);
    }
    // Update state with background
    const backgrounds = await this.getBackgrounds();
    const selectedBackground = backgrounds.find(bg => bg.name === name);
    if (selectedBackground) {
      this.state = {
        ...this.state,
        background: name,
        backgroundFeature: selectedBackground.feature,
        toolProficiencies: [
          ...this.state.toolProficiencies,
          ...selectedBackground.toolProficiencies,
        ],
        languagesKnown: this.state.languagesKnown + selectedBackground.languages,
        selectedSkills: [...this.state.selectedSkills, ...selectedBackground.skillProficiencies],
        skillPoints: this.calculateSkillPoints(selectedBackground),
      };
    }
  }

  private calculateSkillPoints(background: Background): number {
    const basePoints = this.state.class === 'Rogue' ? 8 : 4;
    const intelligenceModifier = Math.floor((this.state.attributes.intelligence - 10) / 2);
    return basePoints + intelligenceModifier + (background.languages || 0);
  }

  public async getSkills(): Promise<Skill[]> {
    const response = await this.apiService.get<Skill[]>('/character-builder/skills');
    if (response.error) {
      throw new Error(response.error.message);
    }
    return response.data;
  }

  public async setSkillProficiencies(skills: string[]): Promise<void> {
    const response = await this.apiService.post<void>('/character-builder/skills', { skills });
    if (response.error) {
      throw new Error(response.error.message);
    }
    this.state.selectedSkills = skills;
    this.updateDerivedStats();
  }

  private calculateAvailableSkillPoints(): number {
    const basePoints = this.state.class === 'Rogue' ? 8 : 4;
    const intelligenceModifier = Math.floor((this.state.attributes.intelligence - 10) / 2);
    const backgroundBonus = this.state.languagesKnown || 0;
    return basePoints + intelligenceModifier + backgroundBonus;
  }
}

export default CharacterBuilderService;
