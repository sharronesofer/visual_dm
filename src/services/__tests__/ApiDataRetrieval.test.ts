import { vi } from 'vitest';
import { ApiService } from '../ApiService';
import RaceService from '../RaceService';
import ClassService from '../ClassService';
import BackgroundService from '../BackgroundService';
import CharacterBuilderService from '../CharacterBuilderService';
import type { ApiResponse, ApiError } from '../ApiService';
import type {
  Race,
  Background,
  Skill,
  StarterKit,
} from '../../types/character';
import type { CharacterClass } from '../../components/CharacterCreation/steps/ClassSelection';

// Mock ApiService
vi.mock('../ApiService');

// Mock the services
vi.mock('../RaceService');
vi.mock('../ClassService');
vi.mock('../BackgroundService');
vi.mock('../CharacterBuilderService');

describe('API Data Retrieval', () => {
  let apiService: jest.Mocked<ReturnType<typeof ApiService.getInstance>>;
  let raceService: RaceService;
  let classService: ClassService;
  let backgroundService: BackgroundService;
  let characterBuilderService: CharacterBuilderService;

  beforeEach(() => {
    // Reset all mocks
    vi.clearAllMocks();

    // Setup API service mock
    apiService = {
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
    } as any;

    (ApiService.getInstance as jest.Mock).mockReturnValue(apiService);

    // Get service instances
    raceService = RaceService.getInstance();
    classService = ClassService.getInstance();
    backgroundService = BackgroundService.getInstance();
    characterBuilderService = CharacterBuilderService.getInstance();
  });

  describe('Race Data Retrieval', () => {
    const mockRaceData = {
      id: '1',
      name: 'Elf',
      description: 'Graceful and long-lived',
      abilityScoreIncrease: { dexterity: 2 },
      speed: 30,
      size: 'Medium',
      abilities: [{ name: 'Darkvision', description: 'See in darkness' }],
      languages: ['Common', 'Elvish'],
      traits: ['Keen Senses'],
    };

    it('successfully retrieves all races', async () => {
      apiService.get.mockResolvedValueOnce({
        data: [mockRaceData],
        error: null,
      });

      const result = await raceService.getAllRaces();
      expect(result.error).toBeNull();
      expect(result.data).toHaveLength(1);
      expect(result.data[0].name).toBe('Elf');
      expect(apiService.get).toHaveBeenCalledWith('/character-builder/races');
    });

    it('handles race retrieval errors', async () => {
      const mockError: ApiError = {
        message: 'Failed to fetch races',
        code: 'FETCH_ERROR',
        status: 500,
      };

      apiService.get.mockResolvedValueOnce({
        data: [],
        error: mockError,
      });

      const result = await raceService.getAllRaces();
      expect(result.error).toBeDefined();
      expect(result.error?.message).toBe('Failed to fetch races');
      expect(result.data).toEqual([]);
    });
  });

  describe('Class Data Retrieval', () => {
    const mockClassData = {
      id: '1',
      name: 'Fighter',
      description: 'Master of martial combat',
      hitDie: 10,
      primaryAbility: 'Strength',
      savingThrows: ['Strength', 'Constitution'],
      features: [{ name: 'Second Wind', description: 'Regain HP', level: 1 }],
    };

    it('successfully retrieves all classes', async () => {
      apiService.get.mockResolvedValueOnce({
        data: [mockClassData],
        error: null,
      });

      const result = await classService.getAllClasses();
      expect(result.error).toBeNull();
      expect(result.data).toHaveLength(1);
      expect(result.data[0].name).toBe('Fighter');
      expect(apiService.get).toHaveBeenCalledWith('/character-builder/classes');
    });

    it('handles class retrieval errors', async () => {
      const mockError: ApiError = {
        message: 'Failed to fetch classes',
        code: 'FETCH_ERROR',
        status: 500,
      };

      apiService.get.mockResolvedValueOnce({
        data: [],
        error: mockError,
      });

      const result = await classService.getAllClasses();
      expect(result.error).toBeDefined();
      expect(result.error?.message).toBe('Failed to fetch classes');
    });
  });

  describe('Background Data Retrieval', () => {
    const mockBackgroundData = {
      id: '1',
      name: 'Soldier',
      description: 'Military background',
      skillProficiencies: ['Athletics', 'Intimidation'],
      equipment: ['Military rank insignia', 'Trophy from battle'],
      features: [
        { name: 'Military Rank', description: 'You have a military rank' },
      ],
    };

    it('successfully retrieves all backgrounds', async () => {
      apiService.get.mockResolvedValueOnce({
        data: [mockBackgroundData],
        error: null,
      });

      const result = await backgroundService.getAllBackgrounds();
      expect(result.error).toBeNull();
      expect(result.data).toHaveLength(1);
      expect(result.data[0].name).toBe('Soldier');
      expect(apiService.get).toHaveBeenCalledWith(
        '/character-builder/backgrounds'
      );
    });

    it('handles background retrieval errors', async () => {
      const mockError: ApiError = {
        message: 'Failed to fetch backgrounds',
        code: 'FETCH_ERROR',
        status: 500,
      };

      apiService.get.mockResolvedValueOnce({
        data: [],
        error: mockError,
      });

      const result = await backgroundService.getAllBackgrounds();
      expect(result.error).toBeDefined();
      expect(result.error?.message).toBe('Failed to fetch backgrounds');
    });
  });

  describe('Character Builder Service', () => {
    it('successfully sets character race', async () => {
      apiService.post.mockResolvedValueOnce({
        data: null,
        error: null,
      });

      await characterBuilderService.setRace('Elf');
      expect(apiService.post).toHaveBeenCalledWith('/character-builder/race', {
        race: 'Elf',
      });
    });

    it('handles race setting errors', async () => {
      const mockError: ApiError = {
        message: 'Invalid race',
        code: 'VALIDATION_ERROR',
        status: 400,
      };

      apiService.post.mockResolvedValueOnce({
        data: null,
        error: mockError,
      });

      await expect(
        characterBuilderService.setRace('InvalidRace')
      ).rejects.toThrow('Invalid race');
    });

    it('successfully sets character class', async () => {
      apiService.post.mockResolvedValueOnce({
        data: null,
        error: null,
      });

      await characterBuilderService.setClass('Fighter');
      expect(apiService.post).toHaveBeenCalledWith('/character-builder/class', {
        class: 'Fighter',
      });
    });

    it('handles class setting errors', async () => {
      const mockError: ApiError = {
        message: 'Invalid class',
        code: 'VALIDATION_ERROR',
        status: 400,
      };

      apiService.post.mockResolvedValueOnce({
        data: null,
        error: mockError,
      });

      await expect(
        characterBuilderService.setClass('InvalidClass')
      ).rejects.toThrow('Invalid class');
    });
  });

  describe('Network Error Handling', () => {
    it('handles network timeouts', async () => {
      const mockError: ApiError = {
        message: 'Request timed out',
        code: 'TIMEOUT',
        status: 408,
      };

      apiService.get.mockResolvedValueOnce({
        data: null,
        error: mockError,
      });

      const result = await raceService.getAllRaces();
      expect(result.error).toBeDefined();
      expect(result.error?.code).toBe('TIMEOUT');
      expect(result.data).toEqual([]);
    });

    it('handles server errors', async () => {
      const mockError: ApiError = {
        message: 'Internal server error',
        code: 'SERVER_ERROR',
        status: 500,
      };

      apiService.get.mockResolvedValueOnce({
        data: null,
        error: mockError,
      });

      const result = await classService.getAllClasses();
      expect(result.error).toBeDefined();
      expect(result.error?.status).toBe(500);
    });

    it('handles unauthorized access', async () => {
      const mockError: ApiError = {
        message: 'Unauthorized access',
        code: 'UNAUTHORIZED',
        status: 401,
      };

      apiService.get.mockResolvedValueOnce({
        data: null,
        error: mockError,
      });

      const result = await backgroundService.getAllBackgrounds();
      expect(result.error).toBeDefined();
      expect(result.error?.status).toBe(401);
    });
  });
});
