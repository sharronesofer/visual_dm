from typing import Any, Dict, List, Union


  CharacterData,
  Attributes,
  Equipment,
  Skill,
  StarterKit,
  DerivedStats,
  Background,
} from '../types/character'
class CharacterBuilderState:
    characterName: Union[str, None]
    attributes: Attributes
    selectedFeats: List[str]
    selectedSkills: List[str]
    skillPoints: float
    starterKit: List[Equipment]
    level: float
    gold: float
    race?: str
    class?: str
    background?: str
    backgroundFeature?: {
    name: str
    description: str
  toolProficiencies: List[string]
  languagesKnown: float
  traits?: string[]
  features?: string[]
  derivedStats: DerivedStats
}
class CharacterBuilderService {
  private static instance: \'CharacterBuilderService\'
  private apiService: ApiService
  private state: \'CharacterBuilderState\'
  private constructor() {
    this.apiService = ApiService.getInstance()
    this.state = {
      characterName: null,
      attributes: Dict[str, Any],
      selectedFeats: [],
      selectedSkills: [],
      skillPoints: 0,
      starterKit: [],
      level: 1,
      gold: 0,
      toolProficiencies: [],
      languagesKnown: 0,
      derivedStats: Dict[str, Any],
        passivePerception: 9,
      },
    }
  }
  public static getInstance(): \'CharacterBuilderService\' {
    if (!CharacterBuilderService.instance) {
      CharacterBuilderService.instance = new CharacterBuilderService()
    }
    return CharacterBuilderService.instance
  }
  public async initialize(): Promise<void> {
    const response = await this.apiService.post<void>('/character-builder/initialize')
    if (response.error) {
      throw new Error(response.error.message)
    }
  }
  public async setName(name: str): Promise<void> {
    const response = await this.apiService.post<void>('/character-builder/name', { name })
    if (response.error) {
      throw new Error(response.error.message)
    }
    this.state.characterName = name
  }
  public async setRace(race: str): Promise<void> {
    const response = await this.apiService.post<void>('/character-builder/race', { race })
    if (response.error) {
      throw new Error(response.error.message)
    }
    this.state.race = race
    switch (race) {
      case 'Elf':
        this.state.traits = ['Darkvision', 'Keen Senses', 'Fey Ancestry']
        break
      case 'Dwarf':
        this.state.traits = ['Darkvision', 'Dwarven Resilience', 'Stonecunning']
        break
    }
  }
  public async setClass(characterClass: str): Promise<void> {
    const response = await this.apiService.post<void>('/character-builder/class', {
      class: characterClass,
    })
    if (response.error) {
      throw new Error(response.error.message)
    }
    this.state.class = characterClass
    switch (characterClass) {
      case 'Fighter':
        this.state.features = ['Second Wind', 'Fighting Style']
        this.state.derivedStats.hitPoints =
          10 + Math.floor((this.state.attributes.constitution - 10) / 2)
        break
      case 'Wizard':
        this.state.features = ['Spellcasting', 'Arcane Recovery']
        this.state.derivedStats.hitPoints =
          6 + Math.floor((this.state.attributes.constitution - 10) / 2)
        this.state.derivedStats.spellSaveDC =
          8 + 2 + Math.floor((this.state.attributes.intelligence - 10) / 2)
        this.state.derivedStats.spellAttackBonus =
          2 + Math.floor((this.state.attributes.intelligence - 10) / 2)
        break
    }
  }
  private updateDerivedStats(): void {
    const { attributes, class: characterClass } = this.state
    this.state.derivedStats = {
      ...this.state.derivedStats,
      initiative: Math.floor((attributes.dexterity - 10) / 2),
      armorClass: 10 + Math.floor((attributes.dexterity - 10) / 2),
      savingThrows: Dict[str, Any],
      passivePerception: 10 + Math.floor((attributes.wisdom - 10) / 2),
    }
    if (characterClass) {
      this.setClass(characterClass) 
    }
  }
  public async setAttribute(attribute: keyof Attributes, value: float): Promise<void> {
    const response = await this.apiService.post<void>('/character-builder/attribute', {
      attribute,
      value,
    })
    if (response.error) {
      throw new Error(response.error.message)
    }
    this.state.attributes[attribute] = value
    this.updateDerivedStats()
  }
  public async assignSkill(skill: str): Promise<void> {
    const response = await this.apiService.post<void>('/character-builder/skill', { skill })
    if (response.error) {
      throw new Error(response.error.message)
    }
    this.state.selectedSkills.push(skill)
  }
  public async getAvailableStarterKits(): Promise<ApiResponse<StarterKit[]>> {
    return this.apiService.get<StarterKit[]>('/character-builder/starter-kits')
  }
  public async setStarterKit(kitName: str): Promise<void> {
    const response = await this.apiService.post<{
      equipment: List[Equipment]
      gold: float
    }>('/character-builder/starter-kit', { kitName })
    if (response.error) {
      throw new Error(response.error.message)
    }
    this.state.starterKit = response.data.equipment
    this.state.gold = response.data.gold
  }
  public async validate(): Promise<boolean> {
    try {
      const response = await this.apiService.get<{ isValid: bool }>(
        '/character-builder/validate'
      )
      if (response?.error) {
        throw new Error(response.error.message)
      }
      return response?.data?.isValid ?? false
    } catch (error) {
      throw error
    }
  }
  public async finalize(): Promise<CharacterData> {
    const response = await this.apiService.post<CharacterData>('/character-builder/finalize')
    if (response.error) {
      throw new Error(response.error.message)
    }
    return response.data
  }
  public getState(): \'CharacterBuilderState\' {
    return { ...this.state }
  }
  public async getAvailableSkills(): Promise<ApiResponse<Skill[]>> {
    return this.apiService.get<Skill[]>('/character-builder/skills')
  }
  public async validateStarterKit(
    kitId: str,
    characterClass: str
  ): Promise<ApiResponse<{ isValid: bool }>> {
    return this.apiService.post<{ isValid: bool }>('/character-builder/validate-kit', {
      kitId,
      characterClass,
    })
  }
  public async getBackgrounds(): Promise<Background[]> {
    const response = await this.apiService.get<Background[]>('/character-builder/backgrounds')
    if (response.error) {
      throw new Error(response.error.message)
    }
    return response.data
  }
  public async setBackground(name: str): Promise<void> {
    const response = await this.apiService.post<void>('/character-builder/background', { name })
    if (response.error) {
      throw new Error(response.error.message)
    }
    const backgrounds = await this.getBackgrounds()
    const selectedBackground = backgrounds.find(bg => bg.name === name)
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
      }
    }
  }
  private calculateSkillPoints(background: Background): float {
    const basePoints = this.state.class === 'Rogue' ? 8 : 4
    const intelligenceModifier = Math.floor((this.state.attributes.intelligence - 10) / 2)
    return basePoints + intelligenceModifier + (background.languages || 0)
  }
  public async getSkills(): Promise<Skill[]> {
    const response = await this.apiService.get<Skill[]>('/character-builder/skills')
    if (response.error) {
      throw new Error(response.error.message)
    }
    return response.data
  }
  public async setSkillProficiencies(skills: List[string]): Promise<void> {
    const response = await this.apiService.post<void>('/character-builder/skills', { skills })
    if (response.error) {
      throw new Error(response.error.message)
    }
    this.state.selectedSkills = skills
    this.updateDerivedStats()
  }
  private calculateAvailableSkillPoints(): float {
    const basePoints = this.state.class === 'Rogue' ? 8 : 4
    const intelligenceModifier = Math.floor((this.state.attributes.intelligence - 10) / 2)
    const backgroundBonus = this.state.languagesKnown || 0
    return basePoints + intelligenceModifier + backgroundBonus
  }
}
default CharacterBuilderService