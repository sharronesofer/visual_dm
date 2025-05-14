import { ApiService, ApiResponse } from './ApiService';

export interface ClassFeature {
  name: string;
  description: string;
  level: number;
}

export interface ClassProficiency {
  type: 'armor' | 'weapon' | 'tool' | 'saving-throw' | 'skill';
  name: string;
}

export interface SpellcastingInfo {
  spellcastingAbility: string;
  spellsKnown: number;
  cantripsKnown: number;
  spellSlots: Record<string, number>;
}

export interface Class {
  id: string;
  name: string;
  description: string;
  hitDie: number;
  primaryAbility: string;
  savingThrowProficiencies: string[];
  armorProficiencies: string[];
  weaponProficiencies: string[];
  toolProficiencies: string[];
  skillChoices: {
    choose: number;
    from: string[];
  };
  features: ClassFeature[];
  spellcasting?: SpellcastingInfo;
  startingEquipment: {
    mandatory: string[];
    choices: Array<{
      choose: number;
      from: string[];
    }>;
  };
}

class ClassService {
  private static instance: ClassService;
  private apiService: ApiService;

  private constructor() {
    this.apiService = ApiService.getInstance();
  }

  public static getInstance(): ClassService {
    if (!ClassService.instance) {
      ClassService.instance = new ClassService();
    }
    return ClassService.instance;
  }

  public async getAllClasses(): Promise<ApiResponse<Class[]>> {
    return this.apiService.get<Class[]>('/character-builder/classes');
  }

  public async getClassById(id: string): Promise<ApiResponse<Class>> {
    return this.apiService.get<Class>(`/character-builder/classes/${id}`);
  }

  public async getClassFeatures(id: string): Promise<ApiResponse<ClassFeature[]>> {
    return this.apiService.get<ClassFeature[]>(`/character-builder/classes/${id}/features`);
  }

  public async getClassSpells(id: string, level: number): Promise<ApiResponse<string[]>> {
    return this.apiService.get<string[]>(`/character-builder/classes/${id}/spells`, {
      params: { level },
    });
  }

  public async getClassProficiencies(id: string): Promise<ApiResponse<ClassProficiency[]>> {
    return this.apiService.get<ClassProficiency[]>(
      `/character-builder/classes/${id}/proficiencies`
    );
  }
}

export default ClassService;
