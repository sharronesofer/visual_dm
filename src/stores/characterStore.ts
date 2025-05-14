import { create } from 'zustand';
import {
  CharacterData,
  Race,
  Skill,
  Equipment,
  StarterKit,
  DerivedStats,
  ValidationState,
} from '../types/character';
import CharacterBuilderService from '../services/CharacterBuilderService';
import CharacterSubmissionService from '../services/CharacterSubmissionService';
import RaceService from '../services/RaceService';
import { ValidationService } from '../utils/validationService';
import { AutoSaveService } from '../utils/autoSaveService';

export interface CharacterStore {
  character: CharacterData;
  availableSkills: Skill[];
  availableStarterKits: StarterKit[];
  races: {
    available: Race[];
    selected: Race | null;
    isLoading: boolean;
    error: string | null;
  };
  isLoading: boolean;
  error: string | null;
  submissionStatus: {
    id?: string;
    status: 'idle' | 'submitting' | 'success' | 'error';
    message?: string;
  };
  validation: ValidationState;
  isDirty: boolean;
  setCharacter: (character: Partial<CharacterData>) => void;
  loadAvailableSkills: () => Promise<void>;
  loadAvailableStarterKits: () => Promise<void>;
  loadAvailableRaces: () => Promise<void>;
  selectRace: (race: Race) => void;
  selectStarterKit: (kit: StarterKit) => Promise<boolean>;
  submitCharacter: () => Promise<void>;
  calculateDerivedStats: () => DerivedStats;
  validateCharacter: () => ValidationState;
  validateField: (fieldName: string, value: any) => ValidationState;
  updateCharacterSummary: () => void;
  loadSavedCharacter: () => void;
  clearSavedCharacter: () => void;
  discardChanges: () => void;
  classes: {
    available: CharacterClass[];
    selected: CharacterClass | null;
    isLoading: boolean;
    error: string | null;
  };
  loadAvailableClasses: () => Promise<void>;
  selectClass: (characterClass: CharacterClass) => void;
  validateClassSelection: (characterClass: CharacterClass) => {
    isValid: boolean;
    message?: string;
  };
  validateRaceSelection: (race: Race) => { isValid: boolean; message?: string };
}

// Define a local CharacterClass type to resolve missing type errors
export type CharacterClass = {
  name: string;
  description: string;
  hitDie: string | number;
  baseAttackBonus?: string;
  fortitudeSave?: string;
  reflexSave?: string;
  willSave?: string;
  skillPoints?: number;
  classSkills?: string[];
  weaponProficiencies?: string[];
  armorProficiencies?: string[];
  classFeatures?: { name: string; level: number; description: string }[];
};

const initialCharacter: CharacterData = {
  id: '',
  name: '',
  race: {
    name: 'Human',
    description: '',
    abilityScoreIncrease: {},
    speed: 30,
    size: 'Medium',
    languages: [],
    traits: [],
  },
  class: {
    name: 'Fighter',
    description: '',
    hitDie: 10,
    primaryAbility: 'strength',
    savingThrows: ['strength', 'constitution'],
    proficiencies: {
      armor: [],
      weapons: [],
      tools: [],
      skills: [],
    },
    features: [],
  },
  background: {
    name: 'Acolyte',
    description: '',
    skillProficiencies: [],
    toolProficiencies: [],
    languages: [],
    equipment: [],
    feature: { name: '', description: '' },
    suggestedCharacteristics: {
      personalityTraits: [],
      ideals: [],
      bonds: [],
      flaws: [],
    },
  },
  level: 1,
  experience: 0,
  attributes: {
    strength: 10,
    dexterity: 10,
    constitution: 10,
    intelligence: 10,
    wisdom: 10,
    charisma: 10,
  },
  skills: [],
  features: [],
  equipment: [],
  proficiencies: [],
  languages: [],
  description: '',
  personality: {
    traits: [],
    ideals: [],
    bonds: [],
    flaws: [],
  },
  alignment: 'True Neutral',
  feats: [],
  derivedStats: {
    hitPoints: 0,
    armorClass: 0,
    initiative: 0,
    speed: 30,
    proficiencyBonus: 2,
    savingThrows: {
      strength: 0,
      dexterity: 0,
      constitution: 0,
      intelligence: 0,
      wisdom: 0,
      charisma: 0,
    },
  },
  appearance: {
    height: '',
    weight: '',
    age: 0,
    eyes: '',
    skin: '',
    hair: '',
  },
  backstory: '',
  skillPoints: 0,
  spells: { cantrips: [], prepared: [], known: [] },
};

const validationService = ValidationService.getInstance();
const autoSaveService = AutoSaveService.getInstance();
const raceService = RaceService.getInstance();

// Configure autosave interval (30 seconds)
autoSaveService.configure({
  interval: 30000,
  storageKey: 'dnd_character_autosave',
  maxSaves: 5,
});

// Mock data for testing
const mockClasses: CharacterClass[] = [
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
];

// Helper to map ValidationResult to ValidationState
function mapValidationResult(result: any): ValidationState {
  return {
    ...result,
    errors: result.errors?.map((e: string | { message: string }) => typeof e === 'string' ? { message: e } : e) || [],
    warnings: result.warnings?.map((e: string | { message: string }) => typeof e === 'string' ? { message: e } : e) || [],
  };
}

const useCharacterStore = create<CharacterStore>((set, get) => ({
  character: initialCharacter,
  availableSkills: [],
  availableStarterKits: [],
  races: {
    available: [],
    selected: null,
    isLoading: false,
    error: null,
  },
  isLoading: false,
  error: null,
  submissionStatus: {
    status: 'idle',
  },
  validation: {
    isValid: false,
    errors: [],
    warnings: [],
  },
  isDirty: false,
  classes: {
    available: [],
    selected: null,
    isLoading: false,
    error: null,
  },

  calculateDerivedStats: () => {
    const state = get();
    const { attributes, class: characterClass, level } = state.character;

    const proficiencyBonus = Math.floor((level - 1) / 4) + 2;

    const derivedStats: DerivedStats = {
      armorClass: 10 + Math.floor((attributes.dexterity - 10) / 2),
      initiative: Math.floor((attributes.dexterity - 10) / 2),
      hitPoints: 0, // Calculated based on class, level, and constitution
      proficiencyBonus,
      passivePerception: 10 + Math.floor((attributes.wisdom - 10) / 2),
      speed: 30, // Added to match DerivedStats interface
    };

    // Add class-specific calculations
    if (["Wizard", "Sorcerer", "Warlock"].includes(characterClass.name)) {
      const spellcastingAbility =
        characterClass.name === "Wizard"
          ? attributes.intelligence
          : characterClass.name === "Warlock"
          ? attributes.charisma
          : attributes.charisma;
      const spellcastingMod = Math.floor((spellcastingAbility - 10) / 2);

      derivedStats.spellSaveDC = 8 + proficiencyBonus + spellcastingMod;
      derivedStats.spellAttackBonus = proficiencyBonus + spellcastingMod;
    }

    return derivedStats;
  },

  validateCharacter: () => {
    const state = get();
    const validationResult = validationService.validateCharacter(state.character);
    const mappedResult = mapValidationResult(validationResult);
    set({ validation: mappedResult });
    return mappedResult;
  },

  validateField: (fieldName: string, value: any) => {
    const rules = validationService.getFieldValidationRules();
    const validationResult = validationService.validateField(fieldName, value, rules);
    const mappedResult = mapValidationResult(validationResult);
    set((state: any) => ({
      validation: {
        ...state.validation,
        errors: [
          ...state.validation.errors.filter((error: any) => !error.message.includes(fieldName)),
          ...mappedResult.errors,
        ],
        warnings: [
          ...state.validation.warnings.filter((warning: any) => !warning.message.includes(fieldName)),
          ...mappedResult.warnings,
        ],
        isValid: state.validation.isValid && mappedResult.isValid,
      },
    }));
    return mappedResult;
  },

  updateCharacterSummary: () => {
    const state = get();
    const derivedStats = state.calculateDerivedStats();
    const validation = state.validateCharacter();
    set((state: any) => ({
      character: {
        ...state.character,
        // summary: { // Removed, CharacterSummary is not defined
        //   isComplete: validation.isValid && validation.incompleteFields.length === 0,
        //   derivedStats,
        //   validation,
        // },
      },
    }));
  },

  setCharacter: (updates: Partial<CharacterData>) => {
    const currentCharacter = get().character;
    const updatedCharacter = { ...currentCharacter, ...updates };

    set({
      character: updatedCharacter,
      isDirty: true,
    });

    // Validate and autosave
    const validationState = mapValidationResult(validationService.validateCharacter(updatedCharacter));
    set({ validation: validationState });

    // Autosave the character
    autoSaveService.saveCharacter(updatedCharacter, true);
  },

  loadAvailableSkills: async () => {
    set({ isLoading: true, error: null });
    try {
      const service = CharacterBuilderService.getInstance();
      const response = await service.getAvailableSkills();
      if (response.error) {
        throw new Error(response.error.message);
      }
      set({ availableSkills: response.data });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to load skills',
      });
    } finally {
      set({ isLoading: false });
    }
  },

  loadAvailableStarterKits: async () => {
    set({ isLoading: true, error: null });
    try {
      const service = CharacterBuilderService.getInstance();
      const response = await service.getAvailableStarterKits();
      if (response.error) {
        throw new Error(response.error.message);
      }
      set({ availableStarterKits: response.data });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to load starter kits',
      });
    } finally {
      set({ isLoading: false });
    }
  },

  loadAvailableRaces: async () => {
    set((state: any) => ({
      races: {
        ...state.races,
        isLoading: true,
        error: null,
      },
    }));

    try {
      const response = await raceService.getAllRaces();
      if (response.error) {
        set((state: any) => ({
          races: {
            ...state.races,
            isLoading: false,
            error: typeof response.error === 'string' ? response.error : 'Failed to load races',
          },
        }));
        return;
      }

      set((state: any) => ({
        races: {
          ...state.races,
          available: response.data,
          isLoading: false,
        },
      }));
    } catch (error: any) {
      set((state: any) => ({
        races: {
          ...state.races,
          isLoading: false,
          error: error instanceof Error ? error.message : 'Failed to load races',
        },
      }));
    }
  },

  selectRace: (race: Race) => {
    set((state: any) => ({
      races: {
        ...state.races,
        selected: race,
      },
      character: {
        ...state.character,
        race: race.name,
        attributes: {
          ...state.character.attributes,
          ...Object.entries(race.abilityScoreIncrease).reduce(
            (acc, [attr, mod]) => ({
              ...acc,
              [attr.toLowerCase()]:
                state.character.attributes[
                  attr.toLowerCase() as keyof typeof state.character.attributes
                ] + mod,
            }),
            {}
          ),
        },
      },
      isDirty: true,
    }));

    // Validate and autosave
    const updatedState = get();
    const validationState = mapValidationResult(validationService.validateCharacter(updatedState.character));
    set({ validation: validationState });
    autoSaveService.saveCharacter(updatedState.character, true);
  },

  selectStarterKit: async (kit: StarterKit) => {
    const state = get();
    const previousEquipment = [...state.character.equipment];

    set((state: any) => ({
      character: {
        ...state.character,
        equipment: kit.equipment,
      },
    }));

    try {
      const service = CharacterBuilderService.getInstance();
      const response = await service.validateStarterKit(kit.id, state.character.class.name);

      if (response.error) {
        set((state: any) => ({
          character: {
            ...state.character,
            equipment: previousEquipment,
          },
        }));

        const validationService = ValidationService.getInstance();
        const validationResult = validationService.handleApiError(response.error);
        const mappedResult = mapValidationResult(validationResult);
        set({ validation: mappedResult });
        return false;
      }

      get().validateCharacter();
      return true;
    } catch (error: any) {
      set((state: any) => ({
        character: {
          ...state.character,
          equipment: previousEquipment,
        },
      }));

      const validationService = ValidationService.getInstance();
      const validationResult = validationService.handleApiError(error);
      const mappedResult = mapValidationResult(validationResult);
      set({ validation: mappedResult });
      return false;
    }
  },

  submitCharacter: async () => {
    const state = get();

    // Validate before submission
    const validationResult = state.validateCharacter();
    if (!validationResult.isValid) {
      set({
        submissionStatus: {
          status: 'error',
          message: 'Please fix validation errors before submitting',
        },
      });
      throw new Error('Character validation failed');
    }

    set({ submissionStatus: { status: 'submitting' } });

    try {
      // Save as a manual save before submission
      autoSaveService.saveCharacter(state.character, false);

      const service = CharacterSubmissionService.getInstance();
      const response = await service.submitCharacter(state.character);

      if (response.error) {
        const validationService = ValidationService.getInstance();
        const validationResult = validationService.handleApiError(response.error);
        set({
          validation: validationResult,
          submissionStatus: {
            status: 'error',
            message: response.error.message,
          },
        });
        throw new Error(response.error.message);
      }

      set({
        submissionStatus: {
          status: 'success',
          id: response.data.id,
          message: 'Character submitted successfully',
        },
      });
      autoSaveService.clearSaves(); // Clear autosaves after successful submission
    } catch (error) {
      const validationService = ValidationService.getInstance();
      const validationResult = validationService.handleApiError(error);
      set({
        validation: validationResult,
        submissionStatus: {
          status: 'error',
          message: validationService.formatErrorMessage(error),
        },
      });
      throw error;
    }
  },

  loadSavedCharacter: () => {
    const savedCharacter = autoSaveService.getLatestSave();
    if (savedCharacter) {
      const validationState = mapValidationResult(validationService.validateCharacter(savedCharacter.data));
      set({
        character: savedCharacter.data,
        validation: validationState,
        isDirty: false,
      });
    }
  },

  clearSavedCharacter: () => {
    autoSaveService.clearSaves();
    set({
      character: initialCharacter,
      validation: {
        isValid: false,
        errors: [],
        warnings: [],
      },
      isDirty: false,
    });
  },

  discardChanges: () => {
    const validSave = autoSaveService.getLatestValidSave();
    if (validSave) {
      const validationState = mapValidationResult(validationService.validateCharacter(validSave.data));
      set({
        character: validSave.data,
        validation: validationState,
        isDirty: false,
      });
    } else {
      set({
        character: initialCharacter,
        validation: {
          isValid: false,
          errors: [],
          warnings: [],
        },
        isDirty: false,
      });
    }
  },

  loadAvailableClasses: async () => {
    set(state => ({
      classes: {
        ...state.classes,
        isLoading: true,
        error: null,
      },
    }));

    try {
      // Simulating API call
      await new Promise(resolve => setTimeout(resolve, 1000));

      set(state => ({
        classes: {
          ...state.classes,
          available: mockClasses,
          isLoading: false,
        },
      }));
    } catch (error) {
      set(state => ({
        classes: {
          ...state.classes,
          error: 'Failed to load classes',
          isLoading: false,
        },
      }));
    }
  },

  selectClass: (characterClass: CharacterClass) => {
    set(state => ({
      classes: {
        ...state.classes,
        selected: characterClass,
      },
    }));
  },

  validateClassSelection: (characterClass: CharacterClass) => {
    // Add validation logic here
    // For now, all classes are valid
    return { isValid: true };
  },

  validateRaceSelection: (race: Race) => {
    // Add validation logic here
    return { isValid: true };
  },
}));

export default useCharacterStore;
