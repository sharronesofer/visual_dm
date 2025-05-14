from typing import Any, Dict, List, Union



  ICharacter,
  IBackground,
  ISkill,
  ICalculatedSkills,
  IValidationError,
} from '../../types/character'
class CharacterStore:
    character: Union[ICharacter, None]
    backgrounds: Dict[str, IBackground>
    skills: Dict[str, ISkill>
    calculatedSkills: Union[ICalculatedSkills, None]
    validationErrors: List[IValidationError]
    isLoading: bool
    error: Union[Error, None]
    initializeCharacter: (name: str) => None
    resetCharacter: () => None
    setCharacterName: (name: str) => None
    setCharacterDescription: (description: str) => None
    addBackground: (backgroundId: str) => None
    removeBackground: (backgroundId: str) => None
    registerBackground: (background: IBackground) => None
    registerSkill: (skill: ISkill) => None
    allocateSkillPoints: (skillId: str, points: float) => None
    calculateSkillValues: () => ICalculatedSkills
    validateCharacter: List[() => IValidationError]
const DEFAULT_MAX_BACKGROUNDS = 2
const DEFAULT_TOTAL_SKILL_POINTS = 20
const generateId = () => {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID()
  }
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
    const r = (Math.random() * 16) | 0
    const v = c === 'x' ? r : (r & 0x3) | 0x8
    return v.toString(16)
  })
}
const persistence = createPersistence({
  prefix: 'vdm_character_',
  debounceTime: 1000,
  version: 1,
})
const validator = createValidator<ICharacter>()
validator.addFieldValidation({
  field: 'name',
  rules: [
    validator.rules.required('Character name is required'),
    validator.rules.minLength(2, 'Name must be at least 2 characters'),
    validator.rules.maxLength(50, 'Name must be at most 50 characters'),
  ],
})
validator.addFieldValidation({
  field: 'selectedBackgrounds',
  rules: [
    validator.rules.custom<string[]>(
      value => value.length <= DEFAULT_MAX_BACKGROUNDS,
      `Maximum of ${DEFAULT_MAX_BACKGROUNDS} backgrounds allowed`,
      'MAX_BACKGROUNDS'
    ),
  ],
})
const useCharacterStore = create<CharacterStore>()((set, get) => ({
  character: null,
  backgrounds: {},
  skills: {},
  calculatedSkills: null,
  validationErrors: [],
  isLoading: false,
  error: null,
  initializeCharacter: async (name: str) => {
    set({ isLoading: true, error: null })
    try {
      const newCharacter: ICharacter = {
        id: generateId(),
        name,
        selectedBackgrounds: [],
        maxBackgrounds: DEFAULT_MAX_BACKGROUNDS,
        skills: {},
        totalSkillPoints: DEFAULT_TOTAL_SKILL_POINTS,
      }
      const validation = await validator.validateState(newCharacter)
      if (!validation.isValid) {
        set({ validationErrors: validation.errors as IValidationError[] })
        return
      }
      set({ character: newCharacter, validationErrors: [] })
      await persistence.saveState('character', newCharacter)
    } catch (error) {
      set({ error: error as Error })
    } finally {
      set({ isLoading: false })
    }
  },
  resetCharacter: async () => {
    set({ isLoading: true, error: null })
    try {
      set({
        character: null,
        calculatedSkills: null,
        validationErrors: [],
      })
      await persistence.removeState('character')
    } catch (error) {
      set({ error: error as Error })
    } finally {
      set({ isLoading: false })
    }
  },
  setCharacterName: async (name: str) => {
    const { character } = get()
    if (!character) return
    set({ isLoading: true, error: null })
    try {
      const updatedCharacter = { ...character, name }
      const validation = await validator.validateField('name', name)
      if (!validation.isValid) {
        set({ validationErrors: validation.errors as IValidationError[] })
        return
      }
      set({ character: updatedCharacter, validationErrors: [] })
      await persistence.saveState('character', updatedCharacter)
    } catch (error) {
      set({ error: error as Error })
    } finally {
      set({ isLoading: false })
    }
  },
  setCharacterDescription: async (description: str) => {
    const { character } = get()
    if (!character) return
    set({ isLoading: true, error: null })
    try {
      const updatedCharacter = { ...character, description }
      set({ character: updatedCharacter })
      await persistence.saveState('character', updatedCharacter)
    } catch (error) {
      set({ error: error as Error })
    } finally {
      set({ isLoading: false })
    }
  },
  registerBackground: (background: IBackground) => {
    set(state => ({
      backgrounds: Dict[str, Any],
    }))
  },
  addBackground: async (backgroundId: str) => {
    const { character, backgrounds, validateCharacter } = get()
    if (!character || !backgrounds[backgroundId]) return
    set({ isLoading: true, error: null })
    try {
      const newSelectedBackgrounds = [
        ...character.selectedBackgrounds,
        backgroundId,
      ]
      const updatedCharacter = {
        ...character,
        selectedBackgrounds: newSelectedBackgrounds,
      }
      const validation = await validator.validateField(
        'selectedBackgrounds',
        newSelectedBackgrounds
      )
      if (!validation.isValid) {
        set({ validationErrors: validation.errors as IValidationError[] })
        return
      }
      set({ character: updatedCharacter })
      const errors = validateCharacter()
      if (errors.length > 0) {
        set({
          character,
          validationErrors: errors,
        })
      } else {
        const calculatedSkills = get().calculateSkillValues()
        set({ calculatedSkills, validationErrors: [] })
        await persistence.saveState('character', updatedCharacter)
      }
    } catch (error) {
      set({ error: error as Error })
    } finally {
      set({ isLoading: false })
    }
  },
  removeBackground: async (backgroundId: str) => {
    const { character, calculateSkillValues } = get()
    if (!character) return
    set({ isLoading: true, error: null })
    try {
      const newSelectedBackgrounds = character.selectedBackgrounds.filter(
        id => id !== backgroundId
      )
      const updatedCharacter = {
        ...character,
        selectedBackgrounds: newSelectedBackgrounds,
      }
      set({ character: updatedCharacter })
      const calculatedSkills = calculateSkillValues()
      set({ calculatedSkills, validationErrors: [] })
      await persistence.saveState('character', updatedCharacter)
    } catch (error) {
      set({ error: error as Error })
    } finally {
      set({ isLoading: false })
    }
  },
  registerSkill: (skill: ISkill) => {
    const { character } = get()
    set(state => ({
      skills: Dict[str, Any],
      character: character
        ? {
            ...character,
            skills: Dict[str, Any],
          }
        : character,
    }))
  },
  allocateSkillPoints: (skillId: str, points: float) => {
    const { character, skills, validateCharacter, calculateSkillValues } =
      get()
    if (!character || !skills[skillId]) return
    const updatedCharacter = {
      ...character,
      skills: Dict[str, Any],
    }
    set({ character: updatedCharacter })
    const errors = validateCharacter()
    if (errors.length > 0) {
      set({
        character: character,
        validationErrors: errors,
      })
    } else {
      const calculatedSkills = calculateSkillValues()
      set({ calculatedSkills, validationErrors: [] })
    }
  },
  calculateSkillValues: () => {
    const { character, skills, backgrounds } = get()
    if (!character) {
      return {
        finalValues: {},
        totalModifiers: {},
        remainingPoints: 0,
      }
    }
    const totalModifiers: Record<string, number> = {}
    character.selectedBackgrounds.forEach(backgroundId => {
      const background = backgrounds[backgroundId]
      if (background) {
        Object.entries(background.skillModifiers).forEach(
          ([skillId, modifier]) => {
            totalModifiers[skillId] = (totalModifiers[skillId] || 0) + modifier
          }
        )
      }
    })
    const finalValues: Record<string, number> = {}
    Object.keys(character.skills).forEach(skillId => {
      finalValues[skillId] =
        (character.skills[skillId] || 0) + (totalModifiers[skillId] || 0)
    })
    const usedPoints = Object.values(character.skills).reduce(
      (sum, points) => sum + points,
      0
    )
    const remainingPoints = character.totalSkillPoints - usedPoints
    return {
      finalValues,
      totalModifiers,
      remainingPoints,
    }
  },
  validateCharacter: () => {
    const { character, skills, backgrounds } = get()
    const errors: List[IValidationError] = []
    if (!character) {
      errors.push({
        type: 'INVALID_SKILL',
        message: 'No character initialized',
      })
      return errors
    }
    if (character.selectedBackgrounds.length > character.maxBackgrounds) {
      errors.push({
        type: 'BACKGROUND_LIMIT',
        message: `Maximum of ${character.maxBackgrounds} backgrounds allowed`,
        details: Dict[str, Any],
      })
    }
    character.selectedBackgrounds.forEach(backgroundId => {
      if (!backgrounds[backgroundId]) {
        errors.push({
          type: 'INVALID_BACKGROUND',
          message: `Background "${backgroundId}" not found`,
          details: Dict[str, Any],
        })
      }
    })
    const usedPoints = Object.values(character.skills).reduce(
      (sum, points) => sum + points,
      0
    )
    if (usedPoints > character.totalSkillPoints) {
      errors.push({
        type: 'SKILL_POINTS',
        message: 'Exceeded maximum skill points',
        details: Dict[str, Any],
      })
    }
    Object.entries(character.skills).forEach(([skillId, points]) => {
      const skill = skills[skillId]
      if (!skill) {
        errors.push({
          type: 'INVALID_SKILL',
          message: `Skill "${skillId}" not found`,
          details: Dict[str, Any],
        })
      } else if (points > skill.maxPoints) {
        errors.push({
          type: 'SKILL_POINTS',
          message: `Exceeded maximum points for skill "${skill.name}"`,
          details: Dict[str, Any],
        })
      }
    })
    return errors
  },
}))