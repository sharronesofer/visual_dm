import { AutoSaveService } from '../autoSaveService';
import { ValidationService } from '../validationService';
import { CharacterData } from '../../types/character';

// Mock ValidationService
jest.mock('../validationService', () => ({
  ValidationService: {
    getInstance: jest.fn(() => ({
      validateCharacter: jest.fn().mockReturnValue({
        isValid: true,
        errors: [],
        warnings: [],
        incompleteFields: [],
      }),
    })),
  },
}));

describe('AutoSaveService', () => {
  let autoSaveService: AutoSaveService;
  let mockLocalStorage: { [key: string]: string };
  let mockValidationService: jest.Mocked<ValidationService>;
  let mockSetInterval: jest.Mock;
  let mockClearInterval: jest.Mock;
  let intervalCallback: Function;

  beforeEach(() => {
    // Clear all instances and calls to constructor and all methods:
    jest.clearAllMocks();

    // Mock localStorage
    mockLocalStorage = {};
    const localStorageMock = {
      getItem: jest.fn((key: string) => mockLocalStorage[key] || null),
      setItem: jest.fn((key: string, value: string) => {
        mockLocalStorage[key] = value;
      }),
      removeItem: jest.fn((key: string) => {
        delete mockLocalStorage[key];
      }),
      clear: jest.fn(() => {
        mockLocalStorage = {};
      }),
      length: 0,
      key: jest.fn((index: number) => ''),
    };
    Object.defineProperty(window, 'localStorage', { value: localStorageMock });

    // Mock setInterval and clearInterval
    mockSetInterval = jest.fn((callback: Function, interval: number) => {
      intervalCallback = callback;
      return 123; // Return a dummy interval ID
    });
    mockClearInterval = jest.fn();

    // Reset singleton instance
    (AutoSaveService as any).instance = null;
    autoSaveService = AutoSaveService.getInstance();
    autoSaveService.setTimerFunctions(mockSetInterval, mockClearInterval);
  });

  describe('getInstance', () => {
    it('should create a singleton instance', () => {
      const instance1 = AutoSaveService.getInstance();
      const instance2 = AutoSaveService.getInstance();
      expect(instance1).toBe(instance2);
    });
  });

  describe('configure', () => {
    it('should update configuration with partial config', () => {
      autoSaveService.configure({ interval: 60000 });
      expect((autoSaveService as any).config.interval).toBe(60000);
      expect((autoSaveService as any).config.maxSaves).toBe(5); // Default value preserved
    });

    it('should maintain default values for unspecified config options', () => {
      const originalConfig = { ...(autoSaveService as any).config };
      autoSaveService.configure({ storageKey: 'custom_key' });
      expect((autoSaveService as any).config.interval).toBe(
        originalConfig.interval
      );
      expect((autoSaveService as any).config.storageKey).toBe('custom_key');
    });
  });

  describe('startAutoSave', () => {
    beforeEach(() => {
      jest.useFakeTimers();
    });

    afterEach(() => {
      jest.useRealTimers();
    });

    it('should start interval and perform initial save', () => {
      const mockCharacterData: CharacterData = {
        name: 'Test Character',
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
        gold: 0,
        selectedFeats: [],
        availableFeats: [],
      };
      const mockOnChange = jest.fn();

      autoSaveService.startAutoSave(mockCharacterData, mockOnChange);

      // Verify initial save was called
      expect(localStorage.setItem).toHaveBeenCalledTimes(1);
      const initialSave = JSON.parse(
        mockLocalStorage['dnd_character_autosaves'] || '[]'
      );
      expect(initialSave[0].isAutosave).toBe(true);

      // Verify interval was set up
      expect(mockSetInterval).toHaveBeenCalledTimes(1);
      expect(mockSetInterval).toHaveBeenCalledWith(expect.any(Function), 30000);

      // Fast-forward time and verify interval save
      jest.advanceTimersByTime(30000); // Default interval
      intervalCallback(); // Execute the interval callback
      expect(localStorage.setItem).toHaveBeenCalledTimes(2);
      expect(mockOnChange).toHaveBeenCalledTimes(1);
    });

    it('should clear existing interval when starting new one', () => {
      const mockCharacterData: CharacterData = {
        name: 'Test Character',
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
        gold: 0,
        selectedFeats: [],
        availableFeats: [],
      };
      const mockOnChange = jest.fn();

      // Start first interval
      autoSaveService.startAutoSave(mockCharacterData, mockOnChange);
      expect(mockSetInterval).toHaveBeenCalledTimes(1);

      // Start second interval
      autoSaveService.startAutoSave(mockCharacterData, mockOnChange);
      expect(mockClearInterval).toHaveBeenCalledTimes(1);
      expect(mockSetInterval).toHaveBeenCalledTimes(2);
    });
  });

  describe('stopAutoSave', () => {
    beforeEach(() => {
      jest.useFakeTimers();
    });

    afterEach(() => {
      jest.useRealTimers();
    });

    it('should clear interval and stop autosaving', () => {
      const mockCharacterData: CharacterData = {
        name: 'Test Character',
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
        gold: 0,
        selectedFeats: [],
        availableFeats: [],
      };
      const mockOnChange = jest.fn();

      autoSaveService.startAutoSave(mockCharacterData, mockOnChange);
      autoSaveService.stopAutoSave();

      jest.advanceTimersByTime(30000);
      expect(mockOnChange).not.toHaveBeenCalled();
      expect(mockClearInterval).toHaveBeenCalledTimes(1);
    });
  });

  describe('saveCharacter', () => {
    it('should save character data with timestamp and validation status', () => {
      const mockCharacterData: CharacterData = {
        name: 'Test Character',
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
        gold: 0,
        selectedFeats: [],
        availableFeats: [],
      };

      autoSaveService.saveCharacter(mockCharacterData, true);

      const savedData = JSON.parse(
        mockLocalStorage['dnd_character_autosaves'] || '[]'
      );
      expect(savedData[0]).toMatchObject({
        data: mockCharacterData,
        isValid: true,
        isAutosave: true,
      });
      expect(savedData[0].timestamp).toBeDefined();
    });

    it('should maintain max saves limit', () => {
      const mockCharacterData: CharacterData = {
        name: 'Test Character',
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
        gold: 0,
        selectedFeats: [],
        availableFeats: [],
      };

      // Save more than maxSaves times
      for (let i = 0; i < 7; i++) {
        autoSaveService.saveCharacter(
          { ...mockCharacterData, name: `Test ${i}` },
          true
        );
      }

      const savedData = JSON.parse(
        mockLocalStorage['dnd_character_autosaves'] || '[]'
      );
      expect(savedData.length).toBe(5); // Default maxSaves
      expect(savedData[0].data.name).toBe('Test 6'); // Most recent save
      expect(savedData[4].data.name).toBe('Test 2'); // Oldest save
    });

    it('should handle validation errors', () => {
      // Mock validation service to return invalid result
      (ValidationService.getInstance as jest.Mock).mockReturnValueOnce({
        validateCharacter: jest.fn().mockReturnValue({
          isValid: false,
          errors: ['Invalid character data'],
          warnings: [],
          incompleteFields: ['name'],
        }),
      });

      // Reset singleton to use new mock
      (AutoSaveService as any).instance = null;
      autoSaveService = AutoSaveService.getInstance();
      autoSaveService.setTimerFunctions(mockSetInterval, mockClearInterval);

      const mockCharacterData: CharacterData = {
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
        gold: 0,
        selectedFeats: [],
        availableFeats: [],
      };

      autoSaveService.saveCharacter(mockCharacterData, true);

      const savedData = JSON.parse(
        mockLocalStorage['dnd_character_autosaves'] || '[]'
      );
      expect(savedData[0].isValid).toBe(false);
    });
  });

  describe('Integration with Character Creation', () => {
    it('should not conflict with manual submission', async () => {
      const mockCharacterData: CharacterData = {
        name: 'Test Character',
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
        gold: 0,
        selectedFeats: [],
        availableFeats: [],
      };

      // Start autosave
      autoSaveService.startAutoSave(mockCharacterData, jest.fn());

      // Simulate manual save
      autoSaveService.saveCharacter(mockCharacterData, false);

      const savedData = JSON.parse(
        mockLocalStorage['dnd_character_autosaves'] || '[]'
      );
      const manualSave = savedData.find((save: any) => !save.isAutosave);
      const autoSave = savedData.find((save: any) => save.isAutosave);

      expect(manualSave).toBeDefined();
      expect(autoSave).toBeDefined();
      expect(savedData.length).toBeLessThanOrEqual(5);
    });
  });

  describe('Error Handling', () => {
    it('should handle localStorage errors gracefully', () => {
      // Mock localStorage.setItem to throw
      const localStorageMock = {
        ...window.localStorage,
        setItem: jest.fn().mockImplementation(() => {
          throw new Error('Storage full');
        }),
      };
      Object.defineProperty(window, 'localStorage', {
        value: localStorageMock,
      });

      const mockCharacterData: CharacterData = {
        name: 'Test Character',
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
        gold: 0,
        selectedFeats: [],
        availableFeats: [],
      };

      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
      autoSaveService.saveCharacter(mockCharacterData, true);

      expect(consoleSpy).toHaveBeenCalledWith(
        'Failed to save character:',
        expect.any(Error)
      );
      consoleSpy.mockRestore();
    });

    it('should handle validation service errors', () => {
      // Mock validation service to throw
      (ValidationService.getInstance as jest.Mock).mockReturnValueOnce({
        validateCharacter: jest.fn().mockImplementation(() => {
          throw new Error('Validation failed');
        }),
      });

      // Reset singleton to use new mock
      (AutoSaveService as any).instance = null;
      autoSaveService = AutoSaveService.getInstance();
      autoSaveService.setTimerFunctions(mockSetInterval, mockClearInterval);

      const mockCharacterData: CharacterData = {
        name: 'Test Character',
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
        gold: 0,
        selectedFeats: [],
        availableFeats: [],
      };

      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
      autoSaveService.saveCharacter(mockCharacterData, true);

      expect(consoleSpy).toHaveBeenCalledWith(
        'Failed to save character:',
        expect.any(Error)
      );
      consoleSpy.mockRestore();
    });
  });

  describe('Edge Cases', () => {
    it('should handle rapid consecutive saves correctly', () => {
      const mockCharacterData: CharacterData = {
        name: 'Test Character',
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
        gold: 0,
        selectedFeats: [],
        availableFeats: [],
      };

      // Simulate rapid saves
      for (let i = 0; i < 3; i++) {
        autoSaveService.saveCharacter(
          { ...mockCharacterData, name: `Manual ${i}` },
          false
        );
        autoSaveService.saveCharacter(
          { ...mockCharacterData, name: `Auto ${i}` },
          true
        );
      }

      const savedData = JSON.parse(
        mockLocalStorage['dnd_character_autosaves'] || '[]'
      );
      expect(savedData.length).toBe(5); // Should still respect maxSaves
      expect(savedData[0].data.name).toBe('Auto 2'); // Most recent should be last auto save
      expect(savedData[1].data.name).toBe('Manual 2'); // Second most recent should be last manual save
    });

    it('should handle getSavedCharacters with corrupted localStorage data', () => {
      // Set corrupted data in localStorage
      localStorage.setItem('dnd_character_autosaves', 'invalid json{');

      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
      const saves = autoSaveService.getSavedCharacters();

      expect(saves).toEqual([]); // Should return empty array on error
      expect(consoleSpy).toHaveBeenCalledWith(
        'Failed to retrieve saved characters:',
        expect.any(Error)
      );
      consoleSpy.mockRestore();
    });
  });
});
