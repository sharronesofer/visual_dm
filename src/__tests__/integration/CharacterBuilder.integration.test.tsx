// Mock the services
jest.mock('../../services/ApiService', () => ({
  ApiService: {
    getInstance: jest.fn().mockReturnValue({
      post: jest.fn().mockImplementation(async (path, data) => {
        switch (path) {
          case '/character-builder/initialize':
            return { data: { initialized: true }, error: null };
          case '/character-builder/validate':
            if (data?.shouldFail) {
              throw new Error('Network error');
            }
            return { data: { isValid: true }, error: null };
          case '/character-builder/race':
            return {
              data: {
                traits: ['Darkvision', 'Keen Senses', 'Fey Ancestry'],
                abilityScoreIncreases: { dexterity: 2, intelligence: 1 },
              },
              error: null,
            };
          case '/character-builder/class':
            return {
              data: {
                features: ['Spellcasting', 'Arcane Recovery'],
                proficiencies: ['Intelligence', 'Wisdom'],
                spellcasting: {
                  ability: 'intelligence',
                  spellList: ['Magic Missile', 'Shield'],
                },
              },
              error: null,
            };
          case '/character-builder/attribute':
            const attribute = data?.attribute;
            const value = data?.value;
            if (attribute && (value < 3 || value > 20)) {
              return { data: null, error: 'Invalid attribute value' };
            }
            return { data: { [attribute]: value }, error: null };
          case '/character-builder/finalize':
            return { data: mockCharacterData, error: null };
          default:
            return { data: null, error: null };
        }
      }),
      get: jest.fn().mockImplementation(async path => {
        if (path === '/character-builder/validate') {
          return { data: { isValid: true }, error: null };
        }
        return { data: null, error: null };
      }),
    }),
  },
}));

jest.mock('../../utils/validationService', () => {
  const validateCharacter = jest
    .fn()
    .mockImplementation((character: CharacterData) => {
      const errors: string[] = [];
      const incompleteFields: string[] = [];
      const warnings: string[] = [];

      // Required fields validation
      if (!character.name) {
        errors.push('Name is required');
        incompleteFields.push('name');
      }
      if (!character.race) {
        errors.push('Race is required');
        incompleteFields.push('race');
      }
      if (!character.class) {
        errors.push('Class is required');
        incompleteFields.push('class');
      }

      // Attribute validation
      Object.entries(character.attributes).forEach(
        ([attr, value]: [string, number]) => {
          if (value < 3) {
            errors.push(`${attr} cannot be less than 3`);
            incompleteFields.push(`attributes.${attr}`);
          }
          if (value > 20) {
            errors.push(`${attr} cannot be greater than 20`);
            incompleteFields.push(`attributes.${attr}`);
          }
          if (value < 8) {
            warnings.push(`${attr} is unusually low`);
          }
        }
      );

      // Skills validation
      if (
        character.skills &&
        character.skillPoints &&
        character.skills.length > character.skillPoints
      ) {
        errors.push('Too many skills selected');
      }

      return {
        isValid: errors.length === 0,
        errors,
        warnings,
        incompleteFields,
      };
    });

  return {
    ValidationService: {
      getInstance: jest.fn().mockReturnValue({
        validateCharacter,
        validateAttributes: jest
          .fn()
          .mockImplementation((attributes: Attributes) => {
            const errors: string[] = [];
            const warnings: string[] = [];
            const incompleteFields: string[] = [];

            Object.entries(attributes).forEach(
              ([attr, value]: [string, number]) => {
                if (value < 3) {
                  errors.push(`${attr} cannot be less than 3`);
                  incompleteFields.push(`attributes.${attr}`);
                }
                if (value > 20) {
                  errors.push(`${attr} cannot be greater than 20`);
                  incompleteFields.push(`attributes.${attr}`);
                }
                if (value < 8) {
                  warnings.push(`${attr} is unusually low`);
                }
              }
            );

            return {
              isValid: errors.length === 0,
              errors,
              warnings,
              incompleteFields,
            };
          }),
        validateEquipment: jest
          .fn()
          .mockImplementation((equipment: string[]) => ({
            isValid: true,
            errors: [],
            warnings: [],
            incompleteFields: [],
          })),
      }),
    },
  };
});

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { renderHook, act } from '@testing-library/react-hooks';
import CharacterBuilderService from '../../services/CharacterBuilderService';
import { ApiService } from '../../services/ApiService';
import { ValidationService } from '../../utils/validationService';
import { AutoSaveService } from '../../utils/autoSaveService';
import useCharacterStore from '../../stores/characterStore';
import { useWizardStore } from '../../stores/wizardStore';
import {
  CharacterData,
  DerivedStats,
  Attributes,
  Equipment,
  RaceType,
  ClassType,
  BackgroundType,
  Race,
  Class,
  Background,
} from '../../types/character';
import {
  ValidationService as ValidationServiceImport,
  ValidationResult,
} from '../../services/ValidationService';

interface ValidationState {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  incompleteFields: string[];
}

interface StoreState {
  character: CharacterData & {
    derivedStats?: DerivedStats;
  };
  validation: ValidationState;
}

interface SavedCharacter {
  data: CharacterData;
  timestamp: number;
  isValid: boolean;
  isAutosave: boolean;
}

interface CharacterBuilderState {
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
  traits?: string[];
  features?: string[];
  derivedStats: DerivedStats;
  validation: {
    isValid: boolean;
    errors: string[];
    warnings: string[];
    incompleteFields: string[];
  };
}

// Mock the stores
jest.mock('../../stores/characterStore', () => {
  const state = {
    character: {
      name: '',
      race: '',
      class: '',
      background: '',
      level: 1,
      alignment: '',
      attributes: {
        strength: 10,
        dexterity: 10,
        constitution: 10,
        intelligence: 10,
        wisdom: 10,
        charisma: 10,
      },
      skills: [],
      equipment: [],
      selectedFeats: [],
      availableFeats: [],
      gold: 0,
      derivedStats: {
        hitPoints: 10,
        armorClass: 10,
        initiative: 0,
        proficiencyBonus: 2,
        passivePerception: 10,
        savingThrows: {
          strength: 0,
          dexterity: 0,
          constitution: 0,
          intelligence: 0,
          wisdom: 0,
          charisma: 0,
        },
      },
    },
    validation: {
      isValid: true,
      errors: [],
      warnings: [],
      incompleteFields: [],
    },
  };

  return {
    __esModule: true,
    default: jest.fn(() => ({
      ...state,
      setCharacter: jest.fn(updates => {
        state.character = { ...state.character, ...updates };
      }),
      setValidation: jest.fn(validation => {
        state.validation = validation;
      }),
      calculateDerivedStats: jest.fn(() => state.character.derivedStats),
    })),
  };
});

jest.mock('../../stores/wizardStore', () => {
  let currentStep = 0;
  const stepValidation: Record<number, boolean> = {};
  const validationErrors: Record<number, string[]> = {};

  return {
    useWizardStore: jest.fn(() => ({
      currentStep,
      stepValidation,
      validationErrors,
      goToNextStep: jest.fn(() => {
        currentStep += 1;
      }),
      goToPreviousStep: jest.fn(() => {
        currentStep -= 1;
      }),
      setStepValidation: jest.fn((step: number, isValid: boolean) => {
        stepValidation[step] = isValid;
      }),
      isStepValid: jest.fn((step: number) => stepValidation[step] || false),
      validateCurrentStep: jest.fn(),
      setValidationErrors: jest.fn((step: number, errors: string[]) => {
        validationErrors[step] = errors;
      }),
      getValidationErrors: jest.fn(
        (step: number) => validationErrors[step] || []
      ),
      resetWizard: jest.fn(() => {
        currentStep = 0;
        Object.keys(stepValidation).forEach(
          key => delete stepValidation[Number(key)]
        );
        Object.keys(validationErrors).forEach(
          key => delete validationErrors[Number(key)]
        );
      }),
    })),
  };
});

jest.mock('../../utils/autoSaveService', () => {
  let savedCharacter: SavedCharacter | null = null;
  let isEnabled = true;
  let autoSaveInterval: number | null = null;
  let config: AutoSaveConfig | null = null;

  return {
    AutoSaveService: {
      getInstance: jest.fn().mockReturnValue({
        configure: jest.fn().mockImplementation((newConfig: AutoSaveConfig) => {
          config = newConfig;
          if (autoSaveInterval) {
            clearInterval(autoSaveInterval);
          }
          if (config.enabled) {
            autoSaveInterval = window.setInterval(() => {
              if (config.onAutoSave) {
                config.onAutoSave();
              }
            }, config.interval || 30000);
          }
        }),
        saveCharacter: jest
          .fn()
          .mockImplementation((character: CharacterData, isAutosave = true) => {
            savedCharacter = {
              data: { ...character },
              timestamp: Date.now(),
              isValid: true,
              isAutosave,
            };
            return savedCharacter;
          }),
        getLatestSave: jest.fn().mockImplementation(() => savedCharacter),
        clearSaves: jest.fn().mockImplementation(() => {
          savedCharacter = null;
        }),
        startAutoSave: jest.fn().mockImplementation(() => {
          isEnabled = true;
          if (config?.onAutoSave && !autoSaveInterval) {
            autoSaveInterval = window.setInterval(
              config.onAutoSave,
              config.interval || 30000
            );
          }
        }),
        stopAutoSave: jest.fn().mockImplementation(() => {
          isEnabled = false;
          if (autoSaveInterval) {
            clearInterval(autoSaveInterval);
            autoSaveInterval = null;
          }
        }),
        isAutoSaveEnabled: jest.fn().mockImplementation(() => isEnabled),
      }),
    },
  };
});

const mockRace: Race = {
  name: 'Elf',
  description: 'Graceful and long-lived',
  abilityScoreIncrease: {
    dexterity: 2,
    intelligence: 1,
  },
  speed: 30,
  size: 'Medium',
  languages: ['Common', 'Elvish'],
  traits: [
    {
      name: 'Darkvision',
      description:
        'You can see in dim light within 60 feet of you as if it were bright light.',
    },
  ],
};

const mockClass: Class = {
  name: 'Wizard',
  description: 'A scholarly magic-user',
  hitDie: 6,
  primaryAbility: 'intelligence',
  savingThrows: ['intelligence', 'wisdom'],
  proficiencies: {
    armor: [],
    weapons: ['dagger', 'dart', 'sling', 'quarterstaff', 'light crossbow'],
    tools: [],
    skills: ['Arcana', 'History', 'Investigation', 'Medicine', 'Religion'],
  },
  features: [
    {
      name: 'Spellcasting',
      level: 1,
      description: 'You can cast wizard spells.',
    },
  ],
  spellcasting: {
    ability: 'intelligence',
    level: 1,
  },
};

const mockBackground: Background = {
  name: 'Sage',
  description: 'You spent years learning the lore of the multiverse.',
  skillProficiencies: ['Arcana', 'History'],
  toolProficiencies: [],
  languages: ['Any two'],
  equipment: [
    {
      name: 'Ink (1 ounce bottle)',
      type: 'gear',
      quantity: 1,
      description: 'A bottle of black ink.',
      cost: {
        amount: 10,
        unit: 'gp',
      },
    },
  ],
  feature: {
    name: 'Researcher',
    description: 'When you attempt to learn or recall a piece of lore...',
  },
  suggestedCharacteristics: {
    personalityTraits: ['I use polysyllabic words...'],
    ideals: ['Knowledge. The path to power...'],
    bonds: ['I have an ancient text...'],
    flaws: ['I am easily distracted...'],
  },
};

// Mock character data
const mockCharacterData: CharacterData = {
  id: '1',
  name: 'Test Character',
  race: mockRace,
  class: mockClass,
  background: mockBackground,
  level: 1,
  experience: 0,
  attributes: {
    strength: 8,
    dexterity: 14,
    constitution: 12,
    intelligence: 16,
    wisdom: 10,
    charisma: 8,
  },
  skills: [],
  features: [],
  equipment: [],
  spells: {
    cantrips: [],
    prepared: [],
    known: [],
  },
  proficiencies: [],
  languages: ['Common', 'Elvish'],
  description: '',
  personality: {
    traits: [],
    ideals: [],
    bonds: [],
    flaws: [],
  },
};

const mockValidationService = {
  validateCharacter: jest.fn().mockImplementation(
    (character: CharacterData): ValidationResult => ({
      isValid: Boolean(character.name && character.race && character.class),
      errors:
        character.name && character.race && character.class
          ? []
          : ['Missing required fields'],
      warnings: [],
      incompleteFields: [],
    })
  ),
  validateField: jest.fn().mockImplementation(
    (fieldName: string, value: any): ValidationResult => ({
      isValid: Boolean(value),
      errors: value ? [] : [`${fieldName} is required`],
      warnings: [],
      incompleteFields: value ? [] : [fieldName],
    })
  ),
  getFieldValidationRules: jest.fn().mockReturnValue({}),
  formatErrorMessage: jest.fn().mockImplementation((error: string) => error),
  handleApiError: jest.fn().mockImplementation((error: Error) => ({
    isValid: false,
    errors: [error.message],
    warnings: [],
    incompleteFields: [],
  })),
};

jest.mock('../../services/ValidationService', () => ({
  ValidationService: {
    getInstance: () => mockValidationService,
  },
}));

describe('CharacterBuilder Integration', () => {
  let mockApiService: jest.Mocked<ApiService>;
  let mockValidationService: jest.Mocked<ValidationServiceImport>;
  let mockAutoSaveService: jest.Mocked<{
    configure: (config: any) => void;
    saveCharacter: (
      character: CharacterData,
      isAutosave?: boolean
    ) => SavedCharacter;
    getLatestSave: () => SavedCharacter | null;
    clearSaves: () => void;
    startAutoSave: () => void;
    stopAutoSave: () => void;
    isAutoSaveEnabled: () => boolean;
  }>;
  let characterBuilderService: CharacterBuilderService;

  beforeEach(() => {
    jest.clearAllMocks();

    // Setup API service mock with proper state handling
    mockApiService = {
      getInstance: jest.fn().mockReturnThis(),
      post: jest.fn().mockImplementation((endpoint: string, data?: any) => {
        if (endpoint === '/character-builder/initialize') {
          return Promise.resolve({ data: { isValid: true }, error: null });
        }
        if (endpoint === '/character-builder/name') {
          return Promise.resolve({ data: { isValid: true }, error: null });
        }
        if (endpoint === '/character-builder/attribute') {
          return Promise.resolve({ data: { isValid: true }, error: null });
        }
        if (endpoint === '/character-builder/race') {
          return Promise.resolve({
            data: {
              traits: ['Darkvision', 'Keen Senses', 'Fey Ancestry'],
              abilityScoreIncreases: { dexterity: 2, intelligence: 1 },
            },
            error: null,
          });
        }
        if (endpoint === '/character-builder/class') {
          return Promise.resolve({
            data: {
              features: ['Spellcasting', 'Arcane Recovery'],
              spellcasting: {
                ability: 'intelligence',
                spellList: ['Magic Missile', 'Shield'],
              },
            },
            error: null,
          });
        }
        return Promise.resolve({ data: null, error: null });
      }),
      get: jest.fn().mockImplementation((endpoint: string) => {
        if (endpoint === '/character-builder/validate') {
          return Promise.resolve({ data: { isValid: true }, error: null });
        }
        return Promise.resolve({ data: null, error: null });
      }),
    } as any;
    (ApiService.getInstance as jest.Mock).mockReturnValue(mockApiService);

    // Setup validation service mock with proper validation logic
    mockValidationService = {
      validateCharacter: jest.fn().mockImplementation(character => ({
        isValid: character.name && character.race && character.class,
        errors:
          character.name && character.race && character.class
            ? []
            : ['Missing required fields'],
      })),
    };
    (ValidationServiceImport.getInstance as jest.Mock).mockReturnValue(
      mockValidationService
    );

    // Setup autosave service mock with proper state tracking
    let savedState: SavedCharacter | null = null;
    mockAutoSaveService = {
      configure: jest.fn(),
      saveCharacter: jest
        .fn()
        .mockImplementation((character: CharacterData, isAutosave = true) => {
          savedState = {
            data: character,
            timestamp: Date.now(),
            isValid: true,
            isAutosave,
          };
          return savedState;
        }),
      getLatestSave: jest.fn().mockImplementation(() => savedState),
      clearSaves: jest.fn().mockImplementation(() => {
        savedState = null;
      }),
      startAutoSave: jest.fn(),
      stopAutoSave: jest.fn(),
      isAutoSaveEnabled: jest.fn().mockReturnValue(true),
    };
    (AutoSaveService.getInstance as jest.Mock).mockReturnValue(
      mockAutoSaveService
    );

    // Initialize service
    characterBuilderService = CharacterBuilderService.getInstance();
  });

  describe('Complete Character Creation Flow', () => {
    it('should maintain state through the entire character creation process', async () => {
      // Setup API responses
      mockApiService.post.mockImplementation((endpoint, data) => {
        switch (endpoint) {
          case '/character-builder/initialize':
            return Promise.resolve({ data: null, error: null });
          case '/character-builder/name':
            return Promise.resolve({ data: null, error: null });
          case '/character-builder/attribute':
            return Promise.resolve({ data: null, error: null });
          case '/character-builder/skill':
            return Promise.resolve({ data: null, error: null });
          case '/character-builder/finalize':
            return Promise.resolve({ data: mockCharacterData, error: null });
          default:
            return Promise.resolve({ data: null, error: null });
        }
      });

      // Initialize character builder
      await characterBuilderService.initialize();
      expect(mockApiService.post).toHaveBeenCalledWith(
        '/character-builder/initialize'
      );

      // Set character name
      await characterBuilderService.setName('Test Character');
      expect(mockApiService.post).toHaveBeenCalledWith(
        '/character-builder/name',
        { name: 'Test Character' }
      );
      expect(characterBuilderService.getState().characterName).toBe(
        'Test Character'
      );

      // Set attributes
      await characterBuilderService.setAttribute('strength', 15);
      expect(mockApiService.post).toHaveBeenCalledWith(
        '/character-builder/attribute',
        {
          attribute: 'strength',
          value: 15,
        }
      );
      expect(characterBuilderService.getState().attributes.strength).toBe(15);

      // Validate final state
      const finalState = characterBuilderService.getState();
      expect(finalState).toMatchObject({
        characterName: 'Test Character',
        attributes: expect.objectContaining({
          strength: 15,
        }),
      });

      // Finalize character
      const finalCharacter = await characterBuilderService.finalize();
      expect(mockApiService.post).toHaveBeenCalledWith(
        '/character-builder/finalize'
      );
      expect(finalCharacter).toMatchObject(mockCharacterData);
    });

    it('should handle validation throughout the creation process', async () => {
      // Setup API success response
      mockApiService.post.mockResolvedValue({
        data: { isValid: true },
        error: null,
      });
      mockApiService.get.mockResolvedValue({
        data: { isValid: true },
        error: null,
      });

      // Initialize with empty state
      await characterBuilderService.initialize();

      // Set invalid state
      await characterBuilderService.setName('');
      await characterBuilderService.setAttribute('strength', 2); // Invalid value

      // Verify validation fails
      const initialValidation = await characterBuilderService.validate();
      expect(initialValidation).toBe(false);
      expect(mockValidationService.validateCharacter).toHaveBeenCalled();
      expect(mockValidationService.validateCharacter).toHaveReturnedWith(
        expect.objectContaining({
          isValid: false,
          errors: expect.arrayContaining([
            'Name is required',
            'strength cannot be less than 3',
          ]),
        })
      );

      // Set valid state
      await characterBuilderService.setName('Test Character');
      await characterBuilderService.setAttribute('strength', 15);
      await characterBuilderService.setRace('Elf');
      await characterBuilderService.setClass('Fighter');

      // Verify validation passes
      const finalValidation = await characterBuilderService.validate();
      expect(finalValidation).toBe(true);
      expect(mockValidationService.validateCharacter).toHaveReturnedWith(
        expect.objectContaining({
          isValid: true,
          errors: [],
        })
      );
    });
  });

  describe('State Synchronization', () => {
    it('should synchronize state between UI and service', async () => {
      // Setup initial store state
      const { result } = renderHook(() => useCharacterStore());

      // Initialize service
      await characterBuilderService.initialize();

      // Update through service
      await characterBuilderService.setName('Updated Name');
      await characterBuilderService.setAttribute('strength', 16);

      // Update store state
      act(() => {
        result.current.setCharacter({
          ...result.current.character,
          name: 'Updated Name',
          attributes: {
            ...result.current.character.attributes,
            strength: 16,
          },
        });
      });

      // Verify store state is updated
      expect(result.current.character.name).toBe('Updated Name');
      expect(result.current.character.attributes.strength).toBe(16);

      // Verify service state matches
      const serviceState = characterBuilderService.getState();
      expect(serviceState.characterName).toBe('Updated Name');
      expect(serviceState.attributes.strength).toBe(16);
    });

    it('should persist state between navigation steps', async () => {
      // Setup initial state
      await characterBuilderService.initialize();

      // Setup store hooks
      const { result: wizardResult } = renderHook(() => useWizardStore());
      const { result: characterResult } = renderHook(() => useCharacterStore());

      // Set initial character data
      act(() => {
        characterResult.current.setCharacter({
          name: 'Test Character',
          race: 'Elf',
          class: 'Wizard',
          background: 'Sage',
          level: 1,
          alignment: 'Neutral Good',
          attributes: {
            strength: 8,
            dexterity: 14,
            constitution: 12,
            intelligence: 16,
            wisdom: 10,
            charisma: 8,
          },
          skills: [],
          equipment: [],
          selectedFeats: [],
          availableFeats: [],
          gold: 0,
        });
      });

      // Navigate forward
      act(() => {
        wizardResult.current.goToNextStep();
      });

      // Verify state is maintained
      expect(characterResult.current.character).toMatchObject({
        name: 'Test Character',
        race: 'Elf',
        class: 'Wizard',
        background: 'Sage',
        attributes: {
          strength: 8,
          dexterity: 14,
          constitution: 12,
          intelligence: 16,
          wisdom: 10,
          charisma: 8,
        },
      });

      // Navigate back
      act(() => {
        wizardResult.current.goToPreviousStep();
      });

      // Verify state is still maintained
      expect(characterResult.current.character).toMatchObject({
        name: 'Test Character',
        race: 'Elf',
        class: 'Wizard',
        background: 'Sage',
      });
    });
  });

  describe('Error Handling', () => {
    it('should handle API failures gracefully', async () => {
      // Setup API failure
      mockApiService.post.mockRejectedValue(new Error('Network error'));
      mockApiService.get.mockRejectedValue(new Error('Network error'));

      // Attempt to initialize with failing API
      await expect(characterBuilderService.initialize()).rejects.toThrow(
        'Network error'
      );

      // Verify validation service is called with error state
      expect(mockValidationService.validateCharacter).toHaveBeenCalled();
      expect(mockValidationService.validateCharacter).toHaveReturnedWith(
        expect.objectContaining({
          isValid: false,
          errors: expect.arrayContaining(['Failed to initialize character']),
        })
      );
    });

    it('should handle validation errors during state updates', async () => {
      // Setup validation failure
      mockValidationService.validateCharacter.mockReturnValue({
        isValid: false,
        errors: ['Invalid attribute value'],
        warnings: [],
        incompleteFields: ['attributes.strength'],
      });

      // Initialize with valid state
      await characterBuilderService.initialize();

      // Attempt invalid update
      await characterBuilderService.setAttribute('strength', 2);

      // Verify validation was called
      expect(mockValidationService.validateCharacter).toHaveBeenCalled();

      // Verify error state is captured
      const validationResult = await characterBuilderService.validate();
      expect(validationResult).toBe(false);
      expect(mockValidationService.validateCharacter).toHaveReturnedWith(
        expect.objectContaining({
          isValid: false,
          errors: ['Invalid attribute value'],
        })
      );
    });

    it('should recover from API errors and maintain consistent state', async () => {
      // Setup initial state
      await characterBuilderService.initialize();
      await characterBuilderService.setName('Initial Name');
      await characterBuilderService.setAttribute('strength', 8);

      // Setup API failure for next call
      mockApiService.post.mockRejectedValueOnce(new Error('Network error'));

      // Attempt update that will fail
      await expect(
        characterBuilderService.setAttribute('strength', 15)
      ).rejects.toThrow('Network error');

      // Verify state remains consistent
      const state = characterBuilderService.getState();
      expect(state).toMatchObject({
        characterName: 'Initial Name',
        attributes: {
          strength: 8, // Should remain at initial value
        },
      });

      // Setup API success for retry
      mockApiService.post.mockResolvedValueOnce({
        data: { isValid: true },
        error: null,
      });

      // Retry update
      await characterBuilderService.setAttribute('strength', 15);

      // Verify state is updated after recovery
      expect(characterBuilderService.getState().attributes.strength).toBe(15);
    });

    it('should handle multiple concurrent API requests correctly', async () => {
      // Setup delayed API responses
      const createDelayedResponse = (delay: number) =>
        new Promise(resolve => setTimeout(resolve, delay));

      mockApiService.post.mockImplementation(async endpoint => {
        if (endpoint === '/character-builder/name') {
          await createDelayedResponse(100);
          return { data: null, error: null };
        }
        if (endpoint === '/character-builder/attribute') {
          await createDelayedResponse(50);
          return { data: null, error: null };
        }
        return { data: null, error: null };
      });

      // Send concurrent requests
      const namePromise = characterBuilderService.setName('New Name');
      const attributePromise = characterBuilderService.setAttribute(
        'strength',
        16
      );

      // Wait for both to complete
      await Promise.all([namePromise, attributePromise]);

      // Verify final state is consistent
      const finalState = characterBuilderService.getState();
      expect(finalState).toMatchObject({
        characterName: 'New Name',
        attributes: expect.objectContaining({
          strength: 16,
        }),
      });
    });
  });

  describe('Event Handlers and UI State', () => {
    it('should update UI when form fields change', async () => {
      // Setup initial state
      await characterBuilderService.initialize();
      const { result } = renderHook(() => useCharacterStore());

      // Update character through service
      await characterBuilderService.setName('New Character');
      await characterBuilderService.setAttribute('strength', 16);

      // Verify store state is updated
      expect(result.current.character.name).toBe('New Character');
      expect(result.current.character.attributes.strength).toBe(16);

      // Verify API was called
      expect(mockApiService.post).toHaveBeenCalledWith(
        '/character-builder/name',
        expect.any(Object)
      );
      expect(mockApiService.post).toHaveBeenCalledWith(
        '/character-builder/attribute',
        expect.any(Object)
      );
    });

    it('should trigger validation on state changes', async () => {
      // Setup initial state
      await characterBuilderService.initialize();
      const { result } = renderHook(() => useCharacterStore());

      // Setup validation response
      mockValidationService.validateCharacter.mockImplementation(character => ({
        isValid: character.name.length > 0,
        errors: character.name.length > 0 ? [] : ['Name is required'],
        warnings: [],
        incompleteFields: character.name.length > 0 ? [] : ['name'],
      }));

      // Update with invalid state
      await characterBuilderService.setName('');

      // Verify validation was triggered
      expect(mockValidationService.validateCharacter).toHaveBeenCalled();
      expect(mockValidationService.validateCharacter).toHaveReturnedWith(
        expect.objectContaining({
          isValid: false,
          errors: ['Name is required'],
        })
      );

      // Update with valid state
      await characterBuilderService.setName('Valid Name');

      // Verify validation passes
      expect(mockValidationService.validateCharacter).toHaveReturnedWith(
        expect.objectContaining({
          isValid: true,
          errors: [],
        })
      );
    });

    it('should handle autosave during state changes', async () => {
      // Setup initial state
      await characterBuilderService.initialize();

      // Make multiple changes
      await characterBuilderService.setName('Autosave Test');
      await characterBuilderService.setRace('Dwarf');
      await characterBuilderService.setAttribute('strength', 16);

      // Verify autosave was triggered
      expect(mockAutoSaveService.saveCharacter).toHaveBeenCalledWith(
        expect.objectContaining({
          name: 'Autosave Test',
          race: 'Dwarf',
          attributes: expect.objectContaining({
            strength: 16,
          }),
        }),
        true
      );
    });

    it('should update derived stats when attributes change', async () => {
      // Setup initial state
      await characterBuilderService.initialize();
      const { result } = renderHook(() => useCharacterStore());

      // Record initial derived stats
      const initialStats = characterBuilderService.getState().derivedStats;

      // Update attributes
      await characterBuilderService.setAttribute('dexterity', 16);
      await characterBuilderService.setAttribute('constitution', 14);

      // Get updated state
      const state = characterBuilderService.getState();

      // Verify derived stats are updated
      expect(state.derivedStats).toMatchObject({
        hitPoints: expect.any(Number),
        armorClass: expect.any(Number),
        initiative: expect.any(Number),
        savingThrows: expect.objectContaining({
          dexterity: expect.any(Number),
          constitution: expect.any(Number),
        }),
      });

      // Verify specific stat changes
      expect(state.derivedStats.armorClass).toBeGreaterThan(
        initialStats.armorClass
      );
      expect(state.derivedStats.initiative).toBeGreaterThan(
        initialStats.initiative
      );
    });
  });

  describe('Race and Class Selection', () => {
    it('should update traits when race is selected', async () => {
      // Setup API success response
      mockApiService.post.mockResolvedValue({ data: null, error: null });

      // Set race to Elf
      await characterBuilderService.setRace('Elf');

      // Verify API call
      expect(mockApiService.post).toHaveBeenCalledWith(
        '/character-builder/race',
        { race: 'Elf' }
      );

      // Verify traits were updated
      const state = characterBuilderService.getState();
      expect(state.race).toBe('Elf');
      expect(state.traits).toContain('Darkvision');
      expect(state.traits).toContain('Keen Senses');
      expect(state.traits).toContain('Fey Ancestry');
    });

    it('should update features and derived stats when class is selected', async () => {
      // Setup API success response
      mockApiService.post.mockResolvedValue({ data: null, error: null });

      // Set attributes first (needed for derived stats)
      await characterBuilderService.setAttribute('constitution', 14);
      await characterBuilderService.setAttribute('intelligence', 16);

      // Set class to Wizard
      await characterBuilderService.setClass('Wizard');

      // Verify API call
      expect(mockApiService.post).toHaveBeenCalledWith(
        '/character-builder/class',
        { class: 'Wizard' }
      );

      // Verify features and derived stats were updated
      const state = characterBuilderService.getState();
      expect(state.class).toBe('Wizard');
      expect(state.features).toContain('Spellcasting');
      expect(state.features).toContain('Arcane Recovery');

      // Verify derived stats calculations
      expect(state.derivedStats.hitPoints).toBe(8); // 6 base + 2 from CON
      expect(state.derivedStats.spellSaveDC).toBe(13); // 8 + 2 prof + 3 from INT
      expect(state.derivedStats.spellAttackBonus).toBe(5); // 2 prof + 3 from INT
    });
  });

  describe('Derived Stats Calculation', () => {
    it('should recalculate derived stats when attributes change', async () => {
      // Setup API success response
      mockApiService.post.mockResolvedValue({ data: null, error: null });

      // Set class first
      await characterBuilderService.setClass('Fighter');

      // Set attributes and verify derived stats updates
      await characterBuilderService.setAttribute('strength', 16);
      await characterBuilderService.setAttribute('dexterity', 14);
      await characterBuilderService.setAttribute('constitution', 15);

      const state = characterBuilderService.getState();
      expect(state.derivedStats).toMatchObject({
        hitPoints: 12, // 10 base + 2 from CON
        armorClass: 12, // 10 + 2 from DEX
        initiative: 2, // DEX modifier
        savingThrows: expect.objectContaining({
          strength: 5, // 3 from STR + 2 proficiency (Fighter)
          dexterity: 2, // 2 from DEX
          constitution: 2, // 2 from CON
        }),
      });
    });
  });

  describe('Concurrent Operations', () => {
    it('should handle multiple attribute updates correctly', async () => {
      // Setup API success response with delay to simulate network latency
      mockApiService.post.mockImplementation(
        () =>
          new Promise(resolve =>
            setTimeout(() => resolve({ data: null, error: null }), 100)
          )
      );

      // Send multiple attribute updates concurrently
      const updates = [
        characterBuilderService.setAttribute('strength', 16),
        characterBuilderService.setAttribute('dexterity', 14),
        characterBuilderService.setAttribute('constitution', 12),
      ];

      // Wait for all updates to complete
      await Promise.all(updates);

      // Verify final state
      const state = characterBuilderService.getState();
      expect(state.attributes).toMatchObject({
        strength: 16,
        dexterity: 14,
        constitution: 12,
      });

      // Verify all API calls were made
      expect(mockApiService.post).toHaveBeenCalledTimes(3);
    });
  });

  describe('AutoSave Integration', () => {
    it('should trigger autosave on state changes', async () => {
      // Setup API success response
      mockApiService.post.mockResolvedValue({ data: null, error: null });

      // Make several state changes
      await characterBuilderService.setName('Test Character');
      await characterBuilderService.setRace('Elf');
      await characterBuilderService.setAttribute('dexterity', 16);

      // Verify autosave was called for each change
      expect(mockAutoSaveService.saveCharacter).toHaveBeenCalledTimes(3);
      expect(mockAutoSaveService.saveCharacter).toHaveBeenLastCalledWith(
        expect.objectContaining({
          name: 'Test Character',
          race: 'Elf',
          attributes: expect.objectContaining({
            dexterity: 16,
          }),
        }),
        true
      );
    });

    it('should restore state from autosave', async () => {
      // Setup mock saved state
      const characterData = {
        name: 'Saved Character',
        race: 'Dwarf',
        class: 'Fighter',
        background: 'Soldier',
        level: 1,
        alignment: 'Lawful Good',
        attributes: {
          strength: 16,
          dexterity: 14,
          constitution: 12,
          intelligence: 10,
          wisdom: 8,
          charisma: 8,
        },
        skills: [],
        equipment: [],
        selectedFeats: [],
        availableFeats: [],
        gold: 0,
      };

      const savedState = {
        data: characterData,
        timestamp: Date.now(),
        isValid: true,
        isAutosave: true,
      };

      mockAutoSaveService.getLatestSave.mockReturnValue(savedState);

      // Initialize character builder (should restore from save)
      await characterBuilderService.initialize();

      // Verify state was restored
      const state = characterBuilderService.getState();
      expect(state).toMatchObject({
        characterName: characterData.name,
        race: characterData.race,
        attributes: expect.objectContaining({
          strength: characterData.attributes.strength,
          dexterity: characterData.attributes.dexterity,
        }),
      });
    });
  });
});
