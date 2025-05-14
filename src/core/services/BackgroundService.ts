import { ApiService, ApiResponse } from './ApiService';

export interface BackgroundFeature {
  name: string;
  description: string;
}

export interface Background {
  id: string;
  name: string;
  description: string;
  skillProficiencies: string[];
  toolProficiencies: string[];
  languages: {
    choose: number;
    from: string[];
  };
  equipment: string[];
  feature: BackgroundFeature;
  personalityTraits: string[];
  ideals: string[];
  bonds: string[];
  flaws: string[];
  gold: number;
}

class BackgroundService {
  private static instance: BackgroundService;
  private apiService: ApiService;

  private constructor() {
    this.apiService = ApiService.getInstance();
  }

  public static getInstance(): BackgroundService {
    if (!BackgroundService.instance) {
      BackgroundService.instance = new BackgroundService();
    }
    return BackgroundService.instance;
  }

  public async getAllBackgrounds(): Promise<ApiResponse<Background[]>> {
    return this.apiService.get<Background[]>('/character-builder/backgrounds');
  }

  public async getBackgroundById(id: string): Promise<ApiResponse<Background>> {
    return this.apiService.get<Background>(`/character-builder/backgrounds/${id}`);
  }

  public async getBackgroundFeature(id: string): Promise<ApiResponse<BackgroundFeature>> {
    return this.apiService.get<BackgroundFeature>(`/character-builder/backgrounds/${id}/feature`);
  }

  public async getRandomPersonalityOptions(id: string): Promise<
    ApiResponse<{
      traits: string[];
      ideals: string[];
      bonds: string[];
      flaws: string[];
    }>
  > {
    return this.apiService.get(`/character-builder/backgrounds/${id}/random-personality`);
  }
}

export default BackgroundService;
