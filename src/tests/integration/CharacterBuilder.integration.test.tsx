import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { renderHook, act } from '@testing-library/react-hooks';
import CharacterBuilderService from '../../services/CharacterBuilderService';
import { ApiService } from '../../services/ApiService';
import { ValidationService } from '../../utils/validationService';
import { AutoSaveService } from '../../utils/autoSaveService';
import useCharacterStore from '../../stores/characterStore';
import { useWizardStore } from '../../stores/wizardStore';

// Mock the services
jest.mock('../../services/ApiService');
jest.mock('../../utils/validationService');
jest.mock('../../utils/autoSaveService', () => ({
  AutoSaveService: {
    getInstance: jest.fn().mockReturnValue({
      configure: jest.fn(),
      saveCharacter: jest.fn(),
      getLatestSave: jest.fn(),
      clearSaves: jest.fn(),
      startAutoSave: jest.fn(),
      stopAutoSave: jest.fn(),
      isAutoSaveEnabled: jest.fn().mockReturnValue(true),
    }),
  },
}));

describe('CharacterBuilder Integration', () => {
  let characterBuilderService: CharacterBuilderService;
  let mockApiService: jest.Mocked<ApiService>;
  let mockValidationService: jest.Mocked<ValidationService>;
  let mockAutoSaveService: jest.Mocked<AutoSaveService>;

  const mockCharacterData = {
    name: 'Test Character',
    race: 'Human',
    class: 'Fighter',
    background: 'Soldier',
    level: 1,
    attributes: {
      strength: 15,
      dexterity: 14,
      constitution: 13,
      intelligence: 12,
      wisdom: 10,
      charisma: 8,
    },
    skills: [],
    equipment: [],
    selectedFeats: [],
    availableFeats: [],
    gold: 0,
  };

  beforeEach(() => {
    jest.clearAllMocks();

    // Setup API service mock
    mockApiService = {
      getInstance: jest.fn().mockReturnThis(),
      post: jest.fn(),
      get: jest.fn(),
    } as any;
    (ApiService.getInstance as jest.Mock).mockReturnValue(mockApiService);

    // Setup validation service mock
    mockValidationService = {
      getInstance: jest.fn().mockReturnThis(),
      validateCharacter: jest.fn().mockReturnValue({
        isValid: true,
        errors: [],
        warnings: [],
        incompleteFields: [],
      }),
    } as any;
    (ValidationService.getInstance as jest.Mock).mockReturnValue(
      mockValidationService
    );

    // Setup auto save service mock with configure method
    mockAutoSaveService = {
      getInstance: jest.fn().mockReturnThis(),
      configure: jest.fn(),
      saveCharacter: jest.fn(),
      getLatestSave: jest.fn(),
      clearSaves: jest.fn(),
      startAutoSave: jest.fn(),
      stopAutoSave: jest.fn(),
      isAutoSaveEnabled: jest.fn().mockReturnValue(true),
    } as any;
    (AutoSaveService.getInstance as jest.Mock).mockReturnValue(
      mockAutoSaveService
    );

    // Configure AutoSaveService before initializing CharacterBuilder
    mockAutoSaveService.configure.mockImplementation(() => {
      // Mock implementation doesn't need to store config
      return;
    });

    // Initialize CharacterBuilder service
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
      // Setup validation responses
      mockValidationService.validateCharacter.mockImplementation(character => ({
        isValid: !!character.name && character.attributes.strength >= 8,
        errors: [],
        warnings: [],
        incompleteFields: [],
      }));

      await characterBuilderService.initialize();

      // Should be invalid initially
      expect(await characterBuilderService.validate()).toBe(false);

      // Should become valid after setting required fields
      await characterBuilderService.setName('Test Character');
      await characterBuilderService.setAttribute('strength', 15);

      expect(await characterBuilderService.validate()).toBe(true);
    });
  });

  describe('State Synchronization', () => {
    it('should synchronize state between UI and service', async () => {
      const { result } = renderHook(() => useCharacterStore());

      // Update through store
      act(() => {
        result.current.setCharacter({ name: 'Test Character' });
      });

      // Verify service state is updated
      expect(characterBuilderService.getState().characterName).toBe(
        'Test Character'
      );

      // Update through service
      await characterBuilderService.setName('Updated Name');

      // Verify store state is updated
      expect(result.current.character.name).toBe('Updated Name');
    });

    it('should handle API failures gracefully', async () => {
      // Setup API error response
      const apiError = { message: 'Network error', code: 'NETWORK_ERROR' };
      mockApiService.post.mockRejectedValue(apiError);

      // Attempt to initialize with failing API
      await expect(characterBuilderService.initialize()).rejects.toThrow(
        'Network error'
      );

      // Verify error state
      expect(characterBuilderService.getState()).toMatchObject({
        characterName: null,
        attributes: expect.any(Object),
        selectedFeats: [],
        selectedSkills: [],
      });
    });

    it('should handle validation errors during state updates', async () => {
      // Setup validation error
      mockValidationService.validateCharacter.mockReturnValue({
        isValid: false,
        errors: ['Invalid attribute value'],
        warnings: [],
        incompleteFields: ['attributes.strength'],
      });

      // Setup API success response
      mockApiService.post.mockResolvedValue({ data: null, error: null });

      // Attempt to set invalid attribute
      await characterBuilderService.setAttribute('strength', 25); // Above maximum

      // Verify validation was called
      expect(mockValidationService.validateCharacter).toHaveBeenCalled();

      // Verify error state is captured
      const validationResult = await characterBuilderService.validate();
      expect(validationResult).toBe(false);
    });

    it('should recover from API errors and maintain consistent state', async () => {
      // Setup initial successful state
      mockApiService.post.mockResolvedValueOnce({ data: null, error: null });
      await characterBuilderService.setName('Initial Name');

      // Setup subsequent API failure
      mockApiService.post.mockRejectedValueOnce(new Error('API Error'));

      // Attempt operation that will fail
      try {
        await characterBuilderService.setAttribute('strength', 15);
      } catch (error: any) {
        // Verify error is thrown
        expect(error.message).toBe('API Error');
      }

      // Verify state remains consistent
      expect(characterBuilderService.getState()).toMatchObject({
        characterName: 'Initial Name', // Previous valid state maintained
        attributes: expect.objectContaining({
          strength: 8, // Should remain at initial value
        }),
      });
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

  describe('Error Handling', () => {
    // ... existing tests ...
  });

  describe('Event Handlers and UI State', () => {
    it('should update UI when form fields change', async () => {
      const { result } = renderHook(() => useCharacterStore());

      // Setup API success response
      mockApiService.post.mockResolvedValue({ data: null, error: null });

      // Simulate form field changes
      act(() => {
        result.current.setCharacter({
          name: 'New Character',
          attributes: {
            ...result.current.character.attributes,
            strength: 16,
          },
        });
      });

      // Verify store state is updated
      expect(result.current.character.name).toBe('New Character');
      expect(result.current.character.attributes.strength).toBe(16);

      // Verify API was called
      expect(mockApiService.post).toHaveBeenCalledWith(
        '/character-builder/name',
        expect.any(Object)
      );
    });

    it('should trigger validation on state changes', async () => {
      const { result } = renderHook(() => useCharacterStore());

      // Setup validation response
      mockValidationService.validateCharacter.mockImplementation(character => ({
        isValid: character.name.length > 0,
        errors: character.name.length > 0 ? [] : ['Name is required'],
        warnings: [],
        incompleteFields: character.name.length > 0 ? [] : ['name'],
      }));

      // Update with invalid state
      act(() => {
        result.current.setCharacter({ name: '' });
      });

      // Verify validation was triggered
      expect(mockValidationService.validateCharacter).toHaveBeenCalled();
      expect(result.current.validation.errors).toContain('Name is required');

      // Update with valid state
      act(() => {
        result.current.setCharacter({ name: 'Valid Name' });
      });

      // Verify validation passes
      expect(result.current.validation.isValid).toBe(true);
      expect(result.current.validation.errors).toHaveLength(0);
    });

    it('should persist state between navigation steps', async () => {
      const { result: wizardResult } = renderHook(() => useWizardStore());
      const { result: characterResult } = renderHook(() => useCharacterStore());

      // Setup initial character state
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

      // Navigate to next step
      act(() => {
        wizardResult.current.goToNextStep();
      });

      // Verify state is maintained
      expect(characterResult.current.character).toMatchObject({
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

    it('should handle autosave during state changes', async () => {
      const { result } = renderHook(() => useCharacterStore());

      // Make state changes
      act(() => {
        result.current.setCharacter({
          name: 'Autosave Test',
          race: 'Dwarf',
        });
      });

      // Verify autosave was triggered
      expect(mockAutoSaveService.saveCharacter).toHaveBeenCalledWith(
        expect.objectContaining({
          name: 'Autosave Test',
          race: 'Dwarf',
        }),
        true
      );

      // Simulate loading saved state
      mockAutoSaveService.getLatestSave.mockReturnValue({
        data: {
          name: 'Autosave Test',
          race: 'Dwarf',
          class: 'Fighter',
          background: 'Soldier',
          level: 1,
          alignment: 'Lawful Good',
          attributes: {
            strength: 16,
            dexterity: 12,
            constitution: 14,
            intelligence: 8,
            wisdom: 10,
            charisma: 8,
          },
          skills: [],
          equipment: [],
          selectedFeats: [],
          availableFeats: [],
          gold: 0,
        },
        timestamp: Date.now(),
        isValid: true,
        isAutosave: true,
      });

      // Load saved state
      act(() => {
        result.current.loadSavedCharacter();
      });

      // Verify state is restored
      expect(result.current.character).toMatchObject({
        name: 'Autosave Test',
        race: 'Dwarf',
        class: 'Fighter',
        background: 'Soldier',
        level: 1,
        alignment: 'Lawful Good',
        attributes: {
          strength: 16,
          dexterity: 12,
          constitution: 14,
          intelligence: 8,
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

    it('should update derived stats when attributes change', async () => {
      const { result } = renderHook(() => useCharacterStore());

      // Setup initial state
      act(() => {
        result.current.setCharacter({
          attributes: {
            strength: 16,
            dexterity: 14,
            constitution: 12,
            intelligence: 10,
            wisdom: 8,
            charisma: 8,
          },
        });
      });

      // Calculate derived stats
      const derivedStats = result.current.calculateDerivedStats();

      // Verify derived stats are calculated correctly
      expect(derivedStats).toMatchObject({
        armorClass: expect.any(Number),
        initiative: expect.any(Number),
        hitPoints: expect.any(Number),
        proficiencyBonus: expect.any(Number),
      });

      // Update attributes
      act(() => {
        result.current.setCharacter({
          attributes: {
            ...result.current.character.attributes,
            dexterity: 16,
          },
        });
      });

      // Verify derived stats are updated
      const updatedStats = result.current.calculateDerivedStats();
      expect(updatedStats.initiative).toBeGreaterThan(derivedStats.initiative);
    });
  });

  describe('Derived Stats', () => {
    it('should calculate derived stats when attributes change', async () => {
      // Setup API success response
      mockApiService.post.mockResolvedValue({ data: null, error: null });

      // Set initial attributes
      await characterBuilderService.setAttribute('strength', 16);
      await characterBuilderService.setAttribute('dexterity', 14);
      await characterBuilderService.setAttribute('constitution', 12);

      // Get state and verify derived stats
      const state = characterBuilderService.getState();
      expect(state.derivedStats).toMatchObject({
        carryingCapacity: expect.any(Number),
        initiative: expect.any(Number),
        hitPoints: expect.any(Number),
      });

      // Verify specific calculations
      expect(state.derivedStats.carryingCapacity).toBe(16 * 15); // Strength * 15
      expect(state.derivedStats.initiative).toBe(2); // (Dexterity - 10) / 2
      expect(state.derivedStats.hitPoints).toBe(10 + 1); // Base 10 + Constitution modifier
    });

    it('should update derived stats when class changes', async () => {
      // Setup API success response
      mockApiService.post.mockResolvedValue({ data: null, error: null });

      // Set attributes and class
      await characterBuilderService.setAttribute('constitution', 14);
      await characterBuilderService.setClass('Fighter');

      // Get state and verify class-specific derived stats
      const state = characterBuilderService.getState();
      expect(state.derivedStats.hitPoints).toBe(10 + 2); // Fighter base (10) + Constitution modifier (2)
      expect(state.derivedStats.hitDice).toBe('1d10'); // Fighter hit die
    });
  });

  describe('Concurrent Operations', () => {
    it('should handle multiple attribute updates correctly', async () => {
      // Setup API success response with delay to simulate network latency
      mockApiService.post.mockImplementation(async () => {
        await new Promise(resolve => setTimeout(resolve, 50));
        return { data: null, error: null };
      });

      // Start multiple concurrent attribute updates
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

      // Verify API calls were made in order
      expect(mockApiService.post.mock.calls).toEqual([
        ['/character-builder/attribute', { attribute: 'strength', value: 16 }],
        ['/character-builder/attribute', { attribute: 'dexterity', value: 14 }],
        [
          '/character-builder/attribute',
          { attribute: 'constitution', value: 12 },
        ],
      ]);
    });

    it('should handle race and class updates atomically', async () => {
      // Setup API success response with delay
      mockApiService.post.mockImplementation(async () => {
        await new Promise(resolve => setTimeout(resolve, 50));
        return { data: null, error: null };
      });

      // Start concurrent race and class updates
      const updates = [
        characterBuilderService.setRace('Elf'),
        characterBuilderService.setClass('Wizard'),
      ];

      // Wait for both updates
      await Promise.all(updates);

      // Verify final state
      const state = characterBuilderService.getState();
      expect(state).toMatchObject({
        race: 'Elf',
        class: 'Wizard',
      });

      // Verify racial traits and class features were applied
      expect(state.traits).toContain('Darkvision');
      expect(state.features).toContain('Spellcasting');
    });

    it('should handle validation during concurrent updates', async () => {
      // Setup validation to fail for specific combinations
      mockValidationService.validateCharacter.mockImplementation(character => ({
        isValid: !(character.race === 'Dwarf' && character.class === 'Wizard'),
        errors:
          character.race === 'Dwarf' && character.class === 'Wizard'
            ? ['Invalid race/class combination']
            : [],
        warnings: [],
        incompleteFields: [],
      }));

      // Setup API success response
      mockApiService.post.mockResolvedValue({ data: null, error: null });

      // Attempt invalid combination concurrently
      const updates = [
        characterBuilderService.setRace('Dwarf'),
        characterBuilderService.setClass('Wizard'),
      ];

      // Wait for both updates
      await Promise.all(updates);

      // Verify validation error is captured
      const validationResult = await characterBuilderService.validate();
      expect(validationResult).toBe(false);
      expect(characterBuilderService.getState().validation.errors).toContain(
        'Invalid race/class combination'
      );
    });
  });
});
