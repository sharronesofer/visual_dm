import { create } from 'zustand';
import {
  ICharacter,
  IBackground,
  ISkill,
  ICalculatedSkills,
  IValidationError,
} from '../../types/character';
import { createPersistence } from '../utils/persistence';
import { createValidator } from '../utils/validation';

interface CharacterStore {
  // State
  character: ICharacter | null;
  backgrounds: Record<string, IBackground>;
  skills: Record<string, ISkill>;
  calculatedSkills: ICalculatedSkills | null;
  validationErrors: IValidationError[];
  isLoading: boolean;
  error: Error | null;

  // Actions
  initializeCharacter: (name: string) => void;
  resetCharacter: () => void;
  setCharacterName: (name: string) => void;
  setCharacterDescription: (description: string) => void;

  // Background management
  addBackground: (backgroundId: string) => void;
  removeBackground: (backgroundId: string) => void;
  registerBackground: (background: IBackground) => void;

  // Skill management
  registerSkill: (skill: ISkill) => void;
  allocateSkillPoints: (skillId: string, points: number) => void;

  // Calculations and validation
  calculateSkillValues: () => ICalculatedSkills;
  validateCharacter: () => IValidationError[];
}

const DEFAULT_MAX_BACKGROUNDS = 2;
const DEFAULT_TOTAL_SKILL_POINTS = 20;

const generateId = () => {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
};

// Create persistence handler
const persistence = createPersistence({
  prefix: 'vdm_character_',
  debounceTime: 1000,
  version: 1,
});

// Create validator
const validator = createValidator<ICharacter>();

// Add validation rules
validator.addFieldValidation({
  field: 'name',
  rules: [
    validator.rules.required('Character name is required'),
    validator.rules.minLength(2, 'Name must be at least 2 characters'),
    validator.rules.maxLength(50, 'Name must be at most 50 characters'),
  ],
});

validator.addFieldValidation({
  field: 'selectedBackgrounds',
  rules: [
    validator.rules.custom<string[]>(
      value => value.length <= DEFAULT_MAX_BACKGROUNDS,
      `Maximum of ${DEFAULT_MAX_BACKGROUNDS} backgrounds allowed`,
      'MAX_BACKGROUNDS'
    ),
  ],
});

export const useCharacterStore = create<CharacterStore>()((set, get) => ({
  // Initial state
  character: null,
  backgrounds: {},
  skills: {},
  calculatedSkills: null,
  validationErrors: [],
  isLoading: false,
  error: null,

  // Character initialization and basic management
  initializeCharacter: async (name: string) => {
    set({ isLoading: true, error: null });
    try {
      const newCharacter: ICharacter = {
        id: generateId(),
        name,
        selectedBackgrounds: [],
        maxBackgrounds: DEFAULT_MAX_BACKGROUNDS,
        skills: {},
        totalSkillPoints: DEFAULT_TOTAL_SKILL_POINTS,
      };

      const validation = await validator.validateState(newCharacter);
      if (!validation.isValid) {
        set({ validationErrors: validation.errors as IValidationError[] });
        return;
      }

      set({ character: newCharacter, validationErrors: [] });
      await persistence.saveState('character', newCharacter);
    } catch (error) {
      set({ error: error as Error });
    } finally {
      set({ isLoading: false });
    }
  },

  resetCharacter: async () => {
    set({ isLoading: true, error: null });
    try {
      set({
        character: null,
        calculatedSkills: null,
        validationErrors: [],
      });
      await persistence.removeState('character');
    } catch (error) {
      set({ error: error as Error });
    } finally {
      set({ isLoading: false });
    }
  },

  setCharacterName: async (name: string) => {
    const { character } = get();
    if (!character) return;

    set({ isLoading: true, error: null });
    try {
      const updatedCharacter = { ...character, name };
      const validation = await validator.validateField('name', name);
      if (!validation.isValid) {
        set({ validationErrors: validation.errors as IValidationError[] });
        return;
      }

      set({ character: updatedCharacter, validationErrors: [] });
      await persistence.saveState('character', updatedCharacter);
    } catch (error) {
      set({ error: error as Error });
    } finally {
      set({ isLoading: false });
    }
  },

  setCharacterDescription: async (description: string) => {
    const { character } = get();
    if (!character) return;

    set({ isLoading: true, error: null });
    try {
      const updatedCharacter = { ...character, description };
      set({ character: updatedCharacter });
      await persistence.saveState('character', updatedCharacter);
    } catch (error) {
      set({ error: error as Error });
    } finally {
      set({ isLoading: false });
    }
  },

  // Background management
  registerBackground: (background: IBackground) => {
    set(state => ({
      backgrounds: { ...state.backgrounds, [background.id]: background },
    }));
  },

  addBackground: async (backgroundId: string) => {
    const { character, backgrounds, validateCharacter } = get();
    if (!character || !backgrounds[backgroundId]) return;

    set({ isLoading: true, error: null });
    try {
      const newSelectedBackgrounds = [
        ...character.selectedBackgrounds,
        backgroundId,
      ];
      const updatedCharacter = {
        ...character,
        selectedBackgrounds: newSelectedBackgrounds,
      };

      const validation = await validator.validateField(
        'selectedBackgrounds',
        newSelectedBackgrounds
      );
      if (!validation.isValid) {
        set({ validationErrors: validation.errors as IValidationError[] });
        return;
      }

      set({ character: updatedCharacter });
      const errors = validateCharacter();
      if (errors.length > 0) {
        // Rollback if validation fails
        set({
          character,
          validationErrors: errors,
        });
      } else {
        // Recalculate skills with new background
        const calculatedSkills = get().calculateSkillValues();
        set({ calculatedSkills, validationErrors: [] });
        await persistence.saveState('character', updatedCharacter);
      }
    } catch (error) {
      set({ error: error as Error });
    } finally {
      set({ isLoading: false });
    }
  },

  removeBackground: async (backgroundId: string) => {
    const { character, calculateSkillValues } = get();
    if (!character) return;

    set({ isLoading: true, error: null });
    try {
      const newSelectedBackgrounds = character.selectedBackgrounds.filter(
        id => id !== backgroundId
      );
      const updatedCharacter = {
        ...character,
        selectedBackgrounds: newSelectedBackgrounds,
      };

      set({ character: updatedCharacter });
      const calculatedSkills = calculateSkillValues();
      set({ calculatedSkills, validationErrors: [] });
      await persistence.saveState('character', updatedCharacter);
    } catch (error) {
      set({ error: error as Error });
    } finally {
      set({ isLoading: false });
    }
  },

  // Skill management
  registerSkill: (skill: ISkill) => {
    const { character } = get();
    set(state => ({
      skills: { ...state.skills, [skill.id]: skill },
      character: character
        ? {
            ...character,
            skills: { ...character.skills, [skill.id]: 0 },
          }
        : character,
    }));
  },

  allocateSkillPoints: (skillId: string, points: number) => {
    const { character, skills, validateCharacter, calculateSkillValues } =
      get();
    if (!character || !skills[skillId]) return;

    const updatedCharacter = {
      ...character,
      skills: { ...character.skills, [skillId]: points },
    };

    set({ character: updatedCharacter });
    const errors = validateCharacter();
    if (errors.length > 0) {
      // Rollback if validation fails
      set({
        character: character,
        validationErrors: errors,
      });
    } else {
      // Recalculate skills with new point allocation
      const calculatedSkills = calculateSkillValues();
      set({ calculatedSkills, validationErrors: [] });
    }
  },

  // Calculations and validation
  calculateSkillValues: () => {
    const { character, skills, backgrounds } = get();
    if (!character) {
      return {
        finalValues: {},
        totalModifiers: {},
        remainingPoints: 0,
      };
    }

    // Calculate total modifiers from all selected backgrounds
    const totalModifiers: Record<string, number> = {};
    character.selectedBackgrounds.forEach(backgroundId => {
      const background = backgrounds[backgroundId];
      if (background) {
        Object.entries(background.skillModifiers).forEach(
          ([skillId, modifier]) => {
            totalModifiers[skillId] = (totalModifiers[skillId] || 0) + modifier;
          }
        );
      }
    });

    // Calculate final values (base points + modifiers)
    const finalValues: Record<string, number> = {};
    Object.keys(character.skills).forEach(skillId => {
      finalValues[skillId] =
        (character.skills[skillId] || 0) + (totalModifiers[skillId] || 0);
    });

    // Calculate remaining points
    const usedPoints = Object.values(character.skills).reduce(
      (sum, points) => sum + points,
      0
    );
    const remainingPoints = character.totalSkillPoints - usedPoints;

    return {
      finalValues,
      totalModifiers,
      remainingPoints,
    };
  },

  validateCharacter: () => {
    const { character, skills, backgrounds } = get();
    const errors: IValidationError[] = [];

    if (!character) {
      errors.push({
        type: 'INVALID_SKILL',
        message: 'No character initialized',
      });
      return errors;
    }

    // Validate background count
    if (character.selectedBackgrounds.length > character.maxBackgrounds) {
      errors.push({
        type: 'BACKGROUND_LIMIT',
        message: `Maximum of ${character.maxBackgrounds} backgrounds allowed`,
        details: {
          current: character.selectedBackgrounds.length,
          max: character.maxBackgrounds,
        },
      });
    }

    // Validate background existence
    character.selectedBackgrounds.forEach(backgroundId => {
      if (!backgrounds[backgroundId]) {
        errors.push({
          type: 'INVALID_BACKGROUND',
          message: `Background "${backgroundId}" not found`,
          details: { backgroundId },
        });
      }
    });

    // Validate skill points
    const usedPoints = Object.values(character.skills).reduce(
      (sum, points) => sum + points,
      0
    );
    if (usedPoints > character.totalSkillPoints) {
      errors.push({
        type: 'SKILL_POINTS',
        message: 'Exceeded maximum skill points',
        details: {
          current: usedPoints,
          max: character.totalSkillPoints,
        },
      });
    }

    // Validate individual skill allocations
    Object.entries(character.skills).forEach(([skillId, points]) => {
      const skill = skills[skillId];
      if (!skill) {
        errors.push({
          type: 'INVALID_SKILL',
          message: `Skill "${skillId}" not found`,
          details: { skillId },
        });
      } else if (points > skill.maxPoints) {
        errors.push({
          type: 'SKILL_POINTS',
          message: `Exceeded maximum points for skill "${skill.name}"`,
          details: {
            skillId,
            current: points,
            max: skill.maxPoints,
          },
        });
      }
    });

    return errors;
  },
}));
