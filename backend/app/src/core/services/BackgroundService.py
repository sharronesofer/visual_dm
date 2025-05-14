from typing import Any, Dict, List


class BackgroundFeature:
    name: str
    description: str
class Background:
    id: str
    name: str
    description: str
    skillProficiencies: List[str]
    toolProficiencies: List[str]
    languages: Dict[str, Any]
class BackgroundService {
  private static instance: \'BackgroundService\'
  private apiService: ApiService
  private constructor() {
    this.apiService = ApiService.getInstance()
  }
  public static getInstance(): \'BackgroundService\' {
    if (!BackgroundService.instance) {
      BackgroundService.instance = new BackgroundService()
    }
    return BackgroundService.instance
  }
  public async getAllBackgrounds(): Promise<ApiResponse<Background[]>> {
    return this.apiService.get<Background[]>('/character-builder/backgrounds')
  }
  public async getBackgroundById(id: str): Promise<ApiResponse<Background>> {
    return this.apiService.get<Background>(`/character-builder/backgrounds/${id}`)
  }
  public async getBackgroundFeature(id: str): Promise<ApiResponse<BackgroundFeature>> {
    return this.apiService.get<BackgroundFeature>(`/character-builder/backgrounds/${id}/feature`)
  }
  public async getRandomPersonalityOptions(id: str): Promise<
    ApiResponse<{
      traits: List[string]
      ideals: List[string]
      bonds: List[string]
      flaws: List[string]
    }>
  > {
    return this.apiService.get(`/character-builder/backgrounds/${id}/random-personality`)
  }
}
default BackgroundService