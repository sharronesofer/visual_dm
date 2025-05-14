import { ApiService, ApiResponse } from './ApiService';
import { Race as CharacterRace } from '../types/character';

interface ApiRaceAbility {
  name: string;
  description: string;
}

interface ApiRace {
  id: string;
  name: string;
  description: string;
  abilityScoreIncrease: Record<string, number>;
  speed: number;
  size: string;
  abilities: ApiRaceAbility[];
  languages: string[];
  traits: string[];
}

export interface RaceAbility {
  name: string;
  description: string;
}

export interface Race {
  id: string;
  name: string;
  description: string;
  ability_modifiers: Record<string, number>;
  speed: number;
  size: string;
  skill_bonuses: Record<string, number>;
  special_traits: { type: string; effect: string }[];
  extra_feats_at_1st_level: number;
  extra_skill_points_at_1st_level: number;
  extra_skill_points_per_level: number;
}

class RaceService {
  private static instance: RaceService;
  private apiService: ApiService;

  private constructor() {
    this.apiService = ApiService.getInstance();
  }

  public static getInstance(): RaceService {
    if (!RaceService.instance) {
      RaceService.instance = new RaceService();
    }
    return RaceService.instance;
  }

  private transformApiRace(race: ApiRace): CharacterRace {
    return {
      name: race.name,
      description: race.description,
      ability_modifiers: race.abilityScoreIncrease || {},
      speed: race.speed,
      size: race.size as 'Small' | 'Medium' | 'Large',
      skill_bonuses: {},
      special_traits: [
        ...race.abilities.map((ability: ApiRaceAbility) => ({
          type: 'ability',
          effect: ability.name,
          detail: ability.description,
        })),
        ...race.traits.map((trait: string) => ({
          type: 'trait',
          effect: trait,
        })),
        ...race.languages.map((language: string) => ({
          type: 'language',
          effect: language,
        })),
      ],
      extra_feats_at_1st_level: 0,
      extra_skill_points_at_1st_level: 0,
      extra_skill_points_per_level: 0,
    };
  }

  public async getAllRaces(): Promise<ApiResponse<CharacterRace[]>> {
    const response = await this.apiService.get<ApiRace[]>('/character-builder/races');

    if (response.error) {
      return {
        ...response,
        data: [],
      };
    }

    // Transform the API response to match our Race interface
    const transformedRaces: CharacterRace[] = response.data.map(race =>
      this.transformApiRace(race)
    );

    return {
      ...response,
      data: transformedRaces,
    };
  }

  public async getRaceById(id: string): Promise<ApiResponse<CharacterRace>> {
    const response = await this.apiService.get<ApiRace>(`/character-builder/races/${id}`);

    if (response.error) {
      return {
        ...response,
        data: null as unknown as CharacterRace,
      };
    }

    // Transform the API response to match our Race interface
    const transformedRace: CharacterRace = this.transformApiRace(response.data);

    return {
      ...response,
      data: transformedRace,
    };
  }

  public async getRaceAbilities(id: string): Promise<ApiResponse<RaceAbility[]>> {
    return this.apiService.get<RaceAbility[]>(`/character-builder/races/${id}/abilities`);
  }
}

export default RaceService;
