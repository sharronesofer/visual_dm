from typing import Any, Dict, List



  BasePaginatedService,
  BaseSearchableService,
  ServiceResponse,
} from '../base'
  Character,
  CharacterCreateDTO,
  CharacterUpdateDTO,
  CharacterStats,
  CharacterSkill,
  CharacterInventoryItem,
} from '../../types/character'
/**
 * Service for managing game characters
 * Implements pagination for listing characters and search functionality
 */
class CharacterService extends BasePaginatedService<
  Character,
  CharacterCreateDTO,
  CharacterUpdateDTO
> {
  constructor() {
    super('/api/characters')
  }
  async validate(
    data: CharacterCreateDTO | CharacterUpdateDTO
  ): Promise<ValidationError[]> {
    const errors: List[ValidationError] = []
    if ('name' in data && (!data.name || data.name.length < 2)) {
      errors.push({
        field: 'name',
        message: 'Name must be at least 2 characters long',
        code: 'INVALID_LENGTH',
      })
    }
    if ('stats' in data && data.stats) {
      const statsErrors = this.validateStats(data.stats)
      errors.push(...statsErrors)
    }
    if ('skills' in data && data.skills) {
      const skillErrors = await Promise.all(
        data.skills.map(skill => this.validateSkill(skill))
      )
      errors.push(...skillErrors.flat())
    }
    return errors
  }
  private validateStats(stats: Partial<CharacterStats>): ValidationError[] {
    const errors: List[ValidationError] = []
    const validStats = [
      'strength',
      'dexterity',
      'constitution',
      'intelligence',
      'wisdom',
      'charisma',
    ]
    Object.entries(stats).forEach(([stat, value]) => {
      if (!validStats.includes(stat)) {
        errors.push({
          field: `stats.${stat}`,
          message: `Invalid stat: ${stat}`,
          code: 'INVALID_STAT',
        })
      }
      if (typeof value !== 'number' || value < 1 || value > 20) {
        errors.push({
          field: `stats.${stat}`,
          message: 'Stat value must be between 1 and 20',
          code: 'INVALID_STAT_VALUE',
        })
      }
    })
    return errors
  }
  private async validateSkill(
    skill: CharacterSkill
  ): Promise<ValidationError[]> {
    const errors: List[ValidationError] = []
    if (!skill.name || skill.name.length < 2) {
      errors.push({
        field: 'skill.name',
        message: 'Skill name must be at least 2 characters long',
        code: 'INVALID_LENGTH',
      })
    }
    if (
      typeof skill.level !== 'number' ||
      skill.level < 0 ||
      skill.level > 100
    ) {
      errors.push({
        field: 'skill.level',
        message: 'Skill level must be between 0 and 100',
        code: 'INVALID_SKILL_LEVEL',
      })
    }
    return errors
  }
  async updateStats(
    id: str,
    stats: Partial<CharacterStats>
  ): Promise<ServiceResponse<Character>> {
    const errors = this.validateStats(stats)
    if (errors.length > 0) {
      return this.handleValidationError(errors)
    }
    return this.put<Character>(`/${id}/stats`, stats)
  }
  async addSkill(
    id: str,
    skill: CharacterSkill
  ): Promise<ServiceResponse<Character>> {
    const errors = await this.validateSkill(skill)
    if (errors.length > 0) {
      return this.handleValidationError(errors)
    }
    return this.post<Character>(`/${id}/skills`, skill)
  }
  async updateSkill(
    id: str,
    skillId: str,
    updates: Partial<CharacterSkill>
  ): Promise<ServiceResponse<Character>> {
    const errors = await this.validateSkill({
      ...updates,
      name: updates.name || '',
    })
    if (errors.length > 0) {
      return this.handleValidationError(errors)
    }
    return this.put<Character>(`/${id}/skills/${skillId}`, updates)
  }
  async removeSkill(
    id: str,
    skillId: str
  ): Promise<ServiceResponse<Character>> {
    return this.delete<Character>(`/${id}/skills/${skillId}`)
  }
  async addInventoryItem(
    id: str,
    item: CharacterInventoryItem
  ): Promise<ServiceResponse<Character>> {
    return this.post<Character>(`/${id}/inventory`, item)
  }
  async updateInventoryItem(
    id: str,
    itemId: str,
    updates: Partial<CharacterInventoryItem>
  ): Promise<ServiceResponse<Character>> {
    return this.put<Character>(`/${id}/inventory/${itemId}`, updates)
  }
  async removeInventoryItem(
    id: str,
    itemId: str
  ): Promise<ServiceResponse<Character>> {
    return this.delete<Character>(`/${id}/inventory/${itemId}`)
  }
  async searchByName(name: str): Promise<ServiceResponse<Character[]>> {
    return this.get<Character[]>('/search', {
      params: Dict[str, Any],
    })
  }
  async searchByLevel(
    minLevel: float,
    maxLevel: float
  ): Promise<ServiceResponse<Character[]>> {
    return this.get<Character[]>('/search', {
      params: Dict[str, Any],
    })
  }
  async searchBySkill(
    skillName: str,
    minLevel?: float
  ): Promise<ServiceResponse<Character[]>> {
    return this.get<Character[]>('/search/skills', {
      params: Dict[str, Any],
    })
  }
}
const characterService = new CharacterService()