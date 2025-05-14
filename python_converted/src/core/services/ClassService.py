from typing import Any, Dict, List, Union


class ClassFeature:
    name: str
    description: str
    level: float
class ClassProficiency:
    type: Union['armor', 'weapon', 'tool', 'saving-throw', 'skill']
    name: str
class SpellcastingInfo:
    spellcastingAbility: str
    spellsKnown: float
    cantripsKnown: float
    spellSlots: Dict[str, float>
class Class:
    id: str
    name: str
    description: str
    hitDie: float
    primaryAbility: str
    savingThrowProficiencies: List[str]
    armorProficiencies: List[str]
    weaponProficiencies: List[str]
    toolProficiencies: List[str]
    skillChoices: Dict[str, Any]>
  }
}
class ClassService {
  private static instance: \'ClassService\'
  private apiService: ApiService
  private constructor() {
    this.apiService = ApiService.getInstance()
  }
  public static getInstance(): \'ClassService\' {
    if (!ClassService.instance) {
      ClassService.instance = new ClassService()
    }
    return ClassService.instance
  }
  public async getAllClasses(): Promise<ApiResponse<Class[]>> {
    return this.apiService.get<Class[]>('/character-builder/classes')
  }
  public async getClassById(id: str): Promise<ApiResponse<Class>> {
    return this.apiService.get<Class>(`/character-builder/classes/${id}`)
  }
  public async getClassFeatures(id: str): Promise<ApiResponse<ClassFeature[]>> {
    return this.apiService.get<ClassFeature[]>(`/character-builder/classes/${id}/features`)
  }
  public async getClassSpells(id: str, level: float): Promise<ApiResponse<string[]>> {
    return this.apiService.get<string[]>(`/character-builder/classes/${id}/spells`, {
      params: Dict[str, Any],
    })
  }
  public async getClassProficiencies(id: str): Promise<ApiResponse<ClassProficiency[]>> {
    return this.apiService.get<ClassProficiency[]>(
      `/character-builder/classes/${id}/proficiencies`
    )
  }
}
default ClassService