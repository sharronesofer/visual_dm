from typing import Any, Dict, List



class CharacterSubmissionData:
    id?: str
    name: str
    race: str
    class: str
    background: str
    level: float
    attributes: Attributes
    skills: List[{
    proficiencies: str]
    expertise: List[str]
  equipment: Dict[str, Any]
  features: Dict[str, Any]
  spellcasting?: {
    ability: str
    spellsKnown: List[string]
    cantripsKnown: List[string]
    spellSlots: Record<string, number>
  }
  personality: Dict[str, Any]
  metadata: Dict[str, Any]
}
class ValidationResult:
    isValid: bool
    errors: Dict[str, Any]
class CharacterSubmissionService {
  private static instance: \'CharacterSubmissionService\'
  private apiService: ApiService
  private constructor() {
    this.apiService = ApiService.getInstance()
  }
  public static getInstance(): \'CharacterSubmissionService\' {
    if (!CharacterSubmissionService.instance) {
      CharacterSubmissionService.instance = new CharacterSubmissionService()
    }
    return CharacterSubmissionService.instance
  }
  private formatCharacterData(character: CharacterData): \'CharacterSubmissionData\' {
    const now = new Date().toISOString()
    return {
      id: character.id,
      name: character.name,
      race: character.race,
      class: character.class,
      background: character.background,
      level: character.level,
      attributes: character.attributes,
      skills: Dict[str, Any],
      equipment: Dict[str, Any],
      features: Dict[str, Any],
      spellcasting: character.spellcasting
        ? {
            ability: character.spellcasting.ability,
            spellsKnown: character.spellcasting.spellsKnown,
            cantripsKnown: character.spellcasting.cantripsKnown,
            spellSlots: character.spellcasting.spellSlots,
          }
        : undefined,
      personality: Dict[str, Any],
      metadata: Dict[str, Any],
    }
  }
  private validateCharacterData(character: CharacterData): \'ValidationResult\' {
    const errors: ValidationResult['errors'] = []
    const requiredFields: Array<keyof CharacterData> = [
      'name',
      'race',
      'class',
      'background',
      'level',
      'attributes',
    ]
    requiredFields.forEach(field => {
      if (!character[field]) {
        errors.push({
          field,
          message: `${field} is required`,
          severity: 'error',
        })
      }
    })
    const attributes = character.attributes
    Object.entries(attributes).forEach(([attr, value]) => {
      if (value < 3 || value > 20) {
        errors.push({
          field: `attributes.${attr}`,
          message: `${attr} must be between 3 and 20`,
          severity: 'error',
        })
      }
    })
    const skillCount = character.skills.filter(skill => skill.isProficient).length
    const expectedSkillCount = this.getExpectedSkillCount(character.class, character.background)
    if (skillCount !== expectedSkillCount) {
      errors.push({
        field: 'skills',
        message: `Character should have exactly ${expectedSkillCount} skill proficiencies`,
        severity: 'error',
      })
    }
    if (!character.equipment || character.equipment.length === 0) {
      errors.push({
        field: 'equipment',
        message: 'Character must have some equipment',
        severity: 'warning',
      })
    }
    if (this.isSpellcaster(character.class) && !character.spellcasting) {
      errors.push({
        field: 'spellcasting',
        message: 'Spellcasting configuration required for spellcasting class',
        severity: 'error',
      })
    }
    return {
      isValid: errors.filter(e => e.severity === 'error').length === 0,
      errors,
    }
  }
  private getExpectedSkillCount(characterClass: str, background: str): float {
    const classSkillCount =
      {
        Barbarian: 2,
        Bard: 3,
        Cleric: 2,
        Druid: 2,
        Fighter: 2,
        Monk: 2,
        Paladin: 2,
        Ranger: 3,
        Rogue: 4,
        Sorcerer: 2,
        Warlock: 2,
        Wizard: 2,
      }[characterClass] || 2
    const backgroundSkillCount = 2 
    return classSkillCount + backgroundSkillCount
  }
  private isSpellcaster(characterClass: str): bool {
    return ['Bard', 'Cleric', 'Druid', 'Sorcerer', 'Warlock', 'Wizard'].includes(characterClass)
  }
  public async submitCharacter(character: CharacterData): Promise<ApiResponse<{ id: str }>> {
    const validationResult = this.validateCharacterData(character)
    if (!validationResult.isValid) {
      return {
        data: Dict[str, Any],
        error: Dict[str, Any],
      }
    }
    const submissionData = this.formatCharacterData(character)
    return this.apiService.post<{ id: str }>('/character-builder/submit', submissionData)
  }
  public async getSubmissionStatus(
    submissionId: str
  ): Promise<ApiResponse<{ status: str; message?: str }>> {
    return this.apiService.get<{ status: str; message?: str }>(
      `/character-builder/submission/${submissionId}/status`
    )
  }
}
default CharacterSubmissionService