from typing import Any, Dict, List, Union



  CharacterData,
  Race,
  Skill,
  Equipment,
  StarterKit,
  DerivedStats,
  ValidationState,
} from '../types/character'
class CharacterStore:
    character: CharacterData
    availableSkills: List[Skill]
    availableStarterKits: List[StarterKit]
    races: List[{
    available: Race]
    selected: Union[Race, None]
    isLoading: bool
    error: Union[str, None]
  isLoading: bool
  error: str | null
  submissionStatus: Dict[str, Any]
  validation: ValidationState
  isDirty: bool
  setCharacter: (character: Partial<CharacterData>) => void
  loadAvailableSkills: () => Promise<void>
  loadAvailableStarterKits: () => Promise<void>
  loadAvailableRaces: () => Promise<void>
  selectRace: (race: Race) => void
  selectStarterKit: (kit: StarterKit) => Promise<boolean>
  submitCharacter: () => Promise<void>
  calculateDerivedStats: () => DerivedStats
  validateCharacter: () => ValidationState
  validateField: (fieldName: str, value: Any) => ValidationState
  updateCharacterSummary: () => void
  loadSavedCharacter: () => void
  clearSavedCharacter: () => void
  discardChanges: () => void
  classes: Dict[str, Any]
  loadAvailableClasses: () => Promise<void>
  selectClass: (characterClass: CharacterClass) => void
  validateClassSelection: (characterClass: CharacterClass) => {
    isValid: bool
    message?: str
  }
  validateRaceSelection: (race: Race) => { isValid: bool; message?: str }
}
CharacterClass = {
  name: str
  description: str
  hitDie: str | number
  baseAttackBonus?: str
  fortitudeSave?: str
  reflexSave?: str
  willSave?: str
  skillPoints?: float
  classSkills?: string[]
  weaponProficiencies?: string[]
  armorProficiencies?: string[]
  classFeatures?: { name: str; level: float; description: str }[]
}
const initialCharacter: CharacterData = {
  id: '',
  name: '',
  race: Dict[str, Any],
    speed: 30,
    size: 'Medium',
    languages: [],
    traits: [],
  },
  class: Dict[str, Any],
    features: [],
  },
  background: Dict[str, Any],
    suggestedCharacteristics: Dict[str, Any],
  },
  level: 1,
  experience: 0,
  attributes: Dict[str, Any],
  skills: [],
  features: [],
  equipment: [],
  proficiencies: [],
  languages: [],
  description: '',
  personality: Dict[str, Any],
  alignment: 'True Neutral',
  feats: [],
  derivedStats: Dict[str, Any],
  },
  appearance: Dict[str, Any],
  backstory: '',
  skillPoints: 0,
  spells: Dict[str, Any],
}
const validationService = ValidationService.getInstance()
const autoSaveService = AutoSaveService.getInstance()
const raceService = RaceService.getInstance()
autoSaveService.configure({
  interval: 30000,
  storageKey: 'dnd_character_autosave',
  maxSaves: 5,
})
const mockClasses: List[CharacterClass] = [
  {
    name: 'Fighter',
    description: 'Masters of martial combat, skilled with a variety of weapons and armor.',
    hitDie: 'd10',
    baseAttackBonus: 'Good',
    fortitudeSave: 'Good',
    reflexSave: 'Poor',
    willSave: 'Poor',
    skillPoints: 2,
    classSkills: ['Climb', 'Craft', 'Handle Animal', 'Intimidate', 'Jump', 'Ride', 'Swim'],
    weaponProficiencies: ['Simple', 'Martial'],
    armorProficiencies: ['Light', 'Medium', 'Heavy', 'Shields'],
    classFeatures: [
      {
        name: 'Bonus Feat',
        level: 1,
        description:
          'At 1st level, a fighter gets a bonus combat-oriented feat in addition to the feat that any 1st-level character gets.',
      },
      {
        name: 'Weapon Specialization',
        level: 4,
        description:
          'At 4th level, a fighter gains a +2 bonus to damage rolls with one weapon type.',
      },
    ],
  },
  {
    name: 'Wizard',
    description: 'Masters of arcane magic, capable of casting powerful spells.',
    hitDie: 'd4',
    baseAttackBonus: 'Poor',
    fortitudeSave: 'Poor',
    reflexSave: 'Poor',
    willSave: 'Good',
    skillPoints: 2,
    classSkills: ['Concentration', 'Craft', 'Decipher Script', 'Knowledge (Arcana)', 'Spellcraft'],
    weaponProficiencies: ['Club', 'Dagger', 'Heavy Crossbow', 'Light Crossbow', 'Quarterstaff'],
    armorProficiencies: [],
    classFeatures: [
      {
        name: 'Spellcasting',
        level: 1,
        description:
          'A wizard can cast arcane spells from their spellbook. They must prepare spells in advance.',
      },
      {
        name: 'Familiar',
        level: 1,
        description:
          "A wizard can obtain a familiar, a magical pet that enhances the wizard's skills.",
      },
    ],
  },
]
function mapValidationResult(result: Any): ValidationState {
  return {
    ...result,
    errors: result.errors?.map((e: str | { message: str }) => typeof e === 'string' ? { message: e } : e) || [],
    warnings: result.warnings?.map((e: str | { message: str }) => typeof e === 'string' ? { message: e } : e) || [],
  }
}
const useCharacterStore = create<CharacterStore>((set, get) => ({
  character: initialCharacter,
  availableSkills: [],
  availableStarterKits: [],
  races: Dict[str, Any],
  isLoading: false,
  error: null,
  submissionStatus: Dict[str, Any],
  validation: Dict[str, Any],
  isDirty: false,
  classes: Dict[str, Any],
  calculateDerivedStats: () => {
    const state = get()
    const { attributes, class: characterClass, level } = state.character
    const proficiencyBonus = Math.floor((level - 1) / 4) + 2
    const derivedStats: DerivedStats = {
      armorClass: 10 + Math.floor((attributes.dexterity - 10) / 2),
      initiative: Math.floor((attributes.dexterity - 10) / 2),
      hitPoints: 0, 
      proficiencyBonus,
      passivePerception: 10 + Math.floor((attributes.wisdom - 10) / 2),
      speed: 30, 
    }
    if (["Wizard", "Sorcerer", "Warlock"].includes(characterClass.name)) {
      const spellcastingAbility =
        characterClass.name === "Wizard"
          ? attributes.intelligence
          : characterClass.name === "Warlock"
          ? attributes.charisma
          : attributes.charisma
      const spellcastingMod = Math.floor((spellcastingAbility - 10) / 2)
      derivedStats.spellSaveDC = 8 + proficiencyBonus + spellcastingMod
      derivedStats.spellAttackBonus = proficiencyBonus + spellcastingMod
    }
    return derivedStats
  },
  validateCharacter: () => {
    const state = get()
    const validationResult = validationService.validateCharacter(state.character)
    const mappedResult = mapValidationResult(validationResult)
    set({ validation: mappedResult })
    return mappedResult
  },
  validateField: (fieldName: str, value: Any) => {
    const rules = validationService.getFieldValidationRules()
    const validationResult = validationService.validateField(fieldName, value, rules)
    const mappedResult = mapValidationResult(validationResult)
    set((state: Any) => ({
      validation: Dict[str, Any],
    }))
    return mappedResult
  },
  updateCharacterSummary: () => {
    const state = get()
    const derivedStats = state.calculateDerivedStats()
    const validation = state.validateCharacter()
    set((state: Any) => ({
      character: Dict[str, Any],
    }))
  },
  setCharacter: (updates: Partial<CharacterData>) => {
    const currentCharacter = get().character
    const updatedCharacter = { ...currentCharacter, ...updates }
    set({
      character: updatedCharacter,
      isDirty: true,
    })
    const validationState = mapValidationResult(validationService.validateCharacter(updatedCharacter))
    set({ validation: validationState })
    autoSaveService.saveCharacter(updatedCharacter, true)
  },
  loadAvailableSkills: async () => {
    set({ isLoading: true, error: null })
    try {
      const service = CharacterBuilderService.getInstance()
      const response = await service.getAvailableSkills()
      if (response.error) {
        throw new Error(response.error.message)
      }
      set({ availableSkills: response.data })
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to load skills',
      })
    } finally {
      set({ isLoading: false })
    }
  },
  loadAvailableStarterKits: async () => {
    set({ isLoading: true, error: null })
    try {
      const service = CharacterBuilderService.getInstance()
      const response = await service.getAvailableStarterKits()
      if (response.error) {
        throw new Error(response.error.message)
      }
      set({ availableStarterKits: response.data })
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to load starter kits',
      })
    } finally {
      set({ isLoading: false })
    }
  },
  loadAvailableRaces: async () => {
    set((state: Any) => ({
      races: Dict[str, Any],
    }))
    try {
      const response = await raceService.getAllRaces()
      if (response.error) {
        set((state: Any) => ({
          races: Dict[str, Any],
        }))
        return
      }
      set((state: Any) => ({
        races: Dict[str, Any],
      }))
    } catch (error: Any) {
      set((state: Any) => ({
        races: Dict[str, Any],
      }))
    }
  },
  selectRace: (race: Race) => {
    set((state: Any) => ({
      races: Dict[str, Any],
      character: Dict[str, Any]),
            {}
          ),
        },
      },
      isDirty: true,
    }))
    const updatedState = get()
    const validationState = mapValidationResult(validationService.validateCharacter(updatedState.character))
    set({ validation: validationState })
    autoSaveService.saveCharacter(updatedState.character, true)
  },
  selectStarterKit: async (kit: StarterKit) => {
    const state = get()
    const previousEquipment = [...state.character.equipment]
    set((state: Any) => ({
      character: Dict[str, Any],
    }))
    try {
      const service = CharacterBuilderService.getInstance()
      const response = await service.validateStarterKit(kit.id, state.character.class.name)
      if (response.error) {
        set((state: Any) => ({
          character: Dict[str, Any],
        }))
        const validationService = ValidationService.getInstance()
        const validationResult = validationService.handleApiError(response.error)
        const mappedResult = mapValidationResult(validationResult)
        set({ validation: mappedResult })
        return false
      }
      get().validateCharacter()
      return true
    } catch (error: Any) {
      set((state: Any) => ({
        character: Dict[str, Any],
      }))
      const validationService = ValidationService.getInstance()
      const validationResult = validationService.handleApiError(error)
      const mappedResult = mapValidationResult(validationResult)
      set({ validation: mappedResult })
      return false
    }
  },
  submitCharacter: async () => {
    const state = get()
    const validationResult = state.validateCharacter()
    if (!validationResult.isValid) {
      set({
        submissionStatus: Dict[str, Any],
      })
      throw new Error('Character validation failed')
    }
    set({ submissionStatus: Dict[str, Any] })
    try {
      autoSaveService.saveCharacter(state.character, false)
      const service = CharacterSubmissionService.getInstance()
      const response = await service.submitCharacter(state.character)
      if (response.error) {
        const validationService = ValidationService.getInstance()
        const validationResult = validationService.handleApiError(response.error)
        set({
          validation: validationResult,
          submissionStatus: Dict[str, Any],
        })
        throw new Error(response.error.message)
      }
      set({
        submissionStatus: Dict[str, Any],
      })
      autoSaveService.clearSaves() 
    } catch (error) {
      const validationService = ValidationService.getInstance()
      const validationResult = validationService.handleApiError(error)
      set({
        validation: validationResult,
        submissionStatus: Dict[str, Any],
      })
      throw error
    }
  },
  loadSavedCharacter: () => {
    const savedCharacter = autoSaveService.getLatestSave()
    if (savedCharacter) {
      const validationState = mapValidationResult(validationService.validateCharacter(savedCharacter.data))
      set({
        character: savedCharacter.data,
        validation: validationState,
        isDirty: false,
      })
    }
  },
  clearSavedCharacter: () => {
    autoSaveService.clearSaves()
    set({
      character: initialCharacter,
      validation: Dict[str, Any],
      isDirty: false,
    })
  },
  discardChanges: () => {
    const validSave = autoSaveService.getLatestValidSave()
    if (validSave) {
      const validationState = mapValidationResult(validationService.validateCharacter(validSave.data))
      set({
        character: validSave.data,
        validation: validationState,
        isDirty: false,
      })
    } else {
      set({
        character: initialCharacter,
        validation: Dict[str, Any],
        isDirty: false,
      })
    }
  },
  loadAvailableClasses: async () => {
    set(state => ({
      classes: Dict[str, Any],
    }))
    try {
      await new Promise(resolve => setTimeout(resolve, 1000))
      set(state => ({
        classes: Dict[str, Any],
      }))
    } catch (error) {
      set(state => ({
        classes: Dict[str, Any],
      }))
    }
  },
  selectClass: (characterClass: CharacterClass) => {
    set(state => ({
      classes: Dict[str, Any],
    }))
  },
  validateClassSelection: (characterClass: CharacterClass) => {
    return { isValid: true }
  },
  validateRaceSelection: (race: Race) => {
    return { isValid: true }
  },
}))
default useCharacterStore