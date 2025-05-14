from typing import Any, Dict, List


class ApiRaceAbility:
    name: str
    description: str
class ApiRace:
    id: str
    name: str
    description: str
    abilityScoreIncrease: Dict[str, float>
    speed: float
    size: str
    abilities: List[ApiRaceAbility]
    languages: List[str]
    traits: List[str]
class RaceAbility:
    name: str
    description: str
class Race:
    id: str
    name: str
    description: str
    ability_modifiers: Dict[str, float>
    speed: float
    size: str
    skill_bonuses: Dict[str, float>
    special_traits: Dict[str, Any]
class RaceService {
  private static instance: \'RaceService\'
  private apiService: ApiService
  private constructor() {
    this.apiService = ApiService.getInstance()
  }
  public static getInstance(): \'RaceService\' {
    if (!RaceService.instance) {
      RaceService.instance = new RaceService()
    }
    return RaceService.instance
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
        ...race.traits.map((trait: str) => ({
          type: 'trait',
          effect: trait,
        })),
        ...race.languages.map((language: str) => ({
          type: 'language',
          effect: language,
        })),
      ],
      extra_feats_at_1st_level: 0,
      extra_skill_points_at_1st_level: 0,
      extra_skill_points_per_level: 0,
    }
  }
  public async getAllRaces(): Promise<ApiResponse<CharacterRace[]>> {
    const response = await this.apiService.get<ApiRace[]>('/character-builder/races')
    if (response.error) {
      return {
        ...response,
        data: [],
      }
    }
    const transformedRaces: List[CharacterRace] = response.data.map(race =>
      this.transformApiRace(race)
    )
    return {
      ...response,
      data: transformedRaces,
    }
  }
  public async getRaceById(id: str): Promise<ApiResponse<CharacterRace>> {
    const response = await this.apiService.get<ApiRace>(`/character-builder/races/${id}`)
    if (response.error) {
      return {
        ...response,
        data: null as unknown as CharacterRace,
      }
    }
    const transformedRace: CharacterRace = this.transformApiRace(response.data)
    return {
      ...response,
      data: transformedRace,
    }
  }
  public async getRaceAbilities(id: str): Promise<ApiResponse<RaceAbility[]>> {
    return this.apiService.get<RaceAbility[]>(`/character-builder/races/${id}/abilities`)
  }
}
default RaceService