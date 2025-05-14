from typing import Any, List


class ValidationResult:
    isValid: bool
    errors: List[str]
    warnings: List[str]
    incompleteFields: List[str]
class FieldValidationRule:
    validate: (value: Any) => bool
    errorMessage: str
class ValidationRules:
    [field: List[str]: FieldValidationRule]
class ValidationStep:
    key: keyof CharacterData
    validate: (data: Partial<CharacterData>) => ValidationResult
    required: bool
const characterCreationSteps: List[ValidationStep] = [
  {
    key: 'race',
    required: true,
    validate: data => {
      const errors: List[string] = []
      const warnings: List[string] = []
      const incompleteFields: List[string] = []
      if (!data.race) {
        errors.push('Race is required')
        incompleteFields.push('race')
      }
      return {
        isValid: errors.length === 0,
        errors,
        warnings,
        incompleteFields,
      }
    },
  },
  {
    key: 'class',
    required: true,
    validate: data => {
      const errors: List[string] = []
      const warnings: List[string] = []
      const incompleteFields: List[string] = []
      if (!data.class) {
        errors.push('Class is required')
        incompleteFields.push('class')
      }
      return {
        isValid: errors.length === 0,
        errors,
        warnings,
        incompleteFields,
      }
    },
  },
  {
    key: 'attributes',
    required: true,
    validate: data => {
      const errors: List[string] = []
      const warnings: List[string] = []
      const incompleteFields: List[string] = []
      if (!data.attributes) {
        errors.push('Attributes are required')
        incompleteFields.push('attributes')
        return {
          isValid: false,
          errors,
          warnings,
          incompleteFields,
        }
      }
      const attrs = data.attributes
      const pointBuyLimit = 27
      let pointsUsed = 0
      Object.values(attrs).forEach(value => {
        if (value < 8) {
          errors.push('Attributes cannot be lower than 8')
        } else if (value > 15) {
          errors.push('Attributes cannot be higher than 15 before racial bonuses')
        } else {
          pointsUsed += value - 8
          if (value > 13) {
            pointsUsed += value - 13
          }
        }
      })
      if (pointsUsed > pointBuyLimit) {
        errors.push(`Exceeded point buy limit (${pointsUsed}/${pointBuyLimit} points used)`)
      } else if (pointsUsed < pointBuyLimit) {
        warnings.push(`Points remaining: ${pointBuyLimit - pointsUsed}`)
      }
      return {
        isValid: errors.length === 0,
        errors,
        warnings,
        incompleteFields,
      }
    },
  },
  {
    key: 'background',
    required: true,
    validate: data => {
      const errors: List[string] = []
      const warnings: List[string] = []
      const incompleteFields: List[string] = []
      if (!data.background) {
        errors.push('Background is required')
        incompleteFields.push('background')
      }
      return {
        isValid: errors.length === 0,
        errors,
        warnings,
        incompleteFields,
      }
    },
  },
  {
    key: 'skills',
    required: true,
    validate: data => {
      const errors: List[string] = []
      const warnings: List[string] = []
      const incompleteFields: List[string] = []
      if (!data.skills || data.skills.length === 0) {
        errors.push('At least one skill must be selected')
        incompleteFields.push('skills')
      }
      return {
        isValid: errors.length === 0,
        errors,
        warnings,
        incompleteFields,
      }
    },
  },
  {
    key: 'equipment',
    required: true,
    validate: data => {
      const errors: List[string] = []
      const warnings: List[string] = []
      const incompleteFields: List[string] = []
      if (!data.equipment || data.equipment.length === 0) {
        errors.push('Starting equipment must be selected')
        incompleteFields.push('equipment')
      }
      return {
        isValid: errors.length === 0,
        errors,
        warnings,
        incompleteFields,
      }
    },
  },
]
const validateStep = (
  step: \'ValidationStep\',
  data: Partial<CharacterData>
): \'ValidationResult\' => {
  return step.validate(data)
}
const validateUpToStep = (
  currentStep: float,
  data: Partial<CharacterData>
): \'ValidationResult\' => {
  const relevantSteps = characterCreationSteps.slice(0, currentStep + 1)
  const results = relevantSteps.map(step => validateStep(step, data))
  return {
    isValid: results.every(r => r.isValid),
    errors: results.flatMap(r => r.errors),
    warnings: results.flatMap(r => r.warnings),
    incompleteFields: results.flatMap(r => r.incompleteFields),
  }
}
const canProceedToNextStep = (
  currentStep: float,
  data: Partial<CharacterData>
): bool => {
  const currentStepValidation = validateStep(characterCreationSteps[currentStep], data)
  return currentStepValidation.isValid
}
class ValidationService {
  private static instance: \'ValidationService\'
  private constructor() {}
  public static getInstance(): \'ValidationService\' {
    if (!ValidationService.instance) {
      ValidationService.instance = new ValidationService()
    }
    return ValidationService.instance
  }
  public validateCharacter(character: CharacterData): \'ValidationResult\' {
    const result: \'ValidationResult\' = {
      isValid: true,
      errors: [],
      warnings: [],
      incompleteFields: [],
    }
    const requiredFields = ['name', 'race', 'class', 'background'] as const
    requiredFields.forEach(field => {
      if (!character[field]) {
        result.incompleteFields.push(field)
        result.isValid = false
      }
    })
    if (character.name) {
      if (character.name.length < 2) {
        result.errors.push('Name must be at least 2 characters long')
        result.isValid = false
      }
      if (character.name.length > 50) {
        result.errors.push('Name must not exceed 50 characters')
        result.isValid = false
      }
      if (!/^[a-zA-Z\s'-]+$/.test(character.name)) {
        result.errors.push('Name can only contain letters, spaces, hyphens, and apostrophes')
        result.isValid = false
      }
    }
    Object.entries(character.attributes).forEach(([attr, value]) => {
      if (typeof value !== 'number') {
        result.errors.push(`${attr} must be a number`)
        result.isValid = false
      } else {
        if (value < 3) {
          result.errors.push(`${attr} cannot be less than 3`)
          result.isValid = false
        }
        if (value > 20) {
          result.errors.push(`${attr} cannot be greater than 20`)
          result.isValid = false
        }
      }
    })
    this.validateSkills(character.skills, character.class, character.background, result)
    if (character.equipment.length === 0) {
      result.warnings.push('Character has no equipment selected')
    } else {
      const equipmentResult = validateEquipmentSelection({
        id: 'custom',
        name: 'Custom Equipment',
        description: 'Custom equipment selection',
        items: character.equipment,
        gold: character.gold,
      })
      result.errors.push(...equipmentResult.errors)
      result.warnings.push(...equipmentResult.warnings)
      if (!equipmentResult.isValid) {
        result.isValid = false
      }
      const compatibilityResult = validateEquipmentCompatibility(
        character.equipment,
        character.class
      )
      result.errors.push(...compatibilityResult.errors)
      result.warnings.push(...compatibilityResult.warnings)
      if (!compatibilityResult.isValid) {
        result.isValid = false
      }
    }
    this.validateClassSpecificRequirements(character, result)
    if (character.gold < 0) {
      result.errors.push('Gold cannot be negative')
      result.isValid = false
    }
    return result
  }
  private validateSkills(
    skills: List[Skill],
    characterClass: str,
    background: str,
    result: \'ValidationResult\'
  ): void {
    const proficientSkills = skills.filter(s => s.isProficient)
    const expectedSkillCount = this.getExpectedSkillCount(characterClass, background)
    if (proficientSkills.length !== expectedSkillCount) {
      result.errors.push(
        `Character must have exactly ${expectedSkillCount} skill proficiencies (currently has ${proficientSkills.length})`
      )
      result.isValid = false
    }
    const expertiseSkills = skills.filter(s => s.hasExpertise)
    if (expertiseSkills.some(s => !s.isProficient)) {
      result.errors.push('Cannot have expertise in skills without proficiency')
      result.isValid = false
    }
  }
  private getExpectedSkillCount(characterClass: str, background: str): float {
    let count = 0
    switch (characterClass.toLowerCase()) {
      case 'bard':
        count += 3
        break
      case 'ranger':
      case 'rogue':
        count += 4
        break
      case 'fighter':
      case 'wizard':
        count += 2
        break
      default:
        count += 2 
    }
    switch (background.toLowerCase()) {
      case 'acolyte':
      case 'criminal':
      case 'noble':
      case 'sage':
      case 'soldier':
        count += 2
        break
      default:
        count += 2 
    }
    return count
  }
  private validateClassSpecificRequirements(
    character: CharacterData,
    result: \'ValidationResult\'
  ): void {
    switch (character.class.toLowerCase()) {
      case 'wizard':
        const hasSpellbook = character.equipment.some(item =>
          item.name.toLowerCase().includes('spellbook')
        )
        if (!hasSpellbook) {
          result.warnings.push('Wizards typically need a spellbook')
        }
        if (character.attributes.intelligence < 13) {
          result.warnings.push('Wizards typically need at least 13 Intelligence')
        }
        break
      case 'fighter':
        const hasWeapon = character.equipment.some(item => item.type === 'weapon')
        if (!hasWeapon) {
          result.warnings.push('Fighters should have at least one weapon')
        }
        const hasArmor = character.equipment.some(item => item.type === 'armor')
        if (!hasArmor) {
          result.warnings.push('Fighters typically need armor')
        }
        break
      case 'rogue':
        const hasLightArmor = character.equipment.some(
          item => item.type === 'armor' && item.properties?.includes('Light')
        )
        if (!hasLightArmor) {
          result.warnings.push('Rogues typically use light armor')
        }
        break
      case 'cleric':
        const hasHolySymbol = character.equipment.some(item =>
          item.name.toLowerCase().includes('holy symbol')
        )
        if (!hasHolySymbol) {
          result.warnings.push('Clerics typically need a holy symbol')
        }
        break
    }
  }
  public validateField(fieldName: str, value: Any, rules: ValidationRules): \'ValidationResult\' {
    const result: \'ValidationResult\' = {
      isValid: true,
      errors: [],
      warnings: [],
      incompleteFields: [],
    }
    const fieldRules = rules[fieldName]
    if (!fieldRules) {
      return result
    }
    fieldRules.forEach(rule => {
      if (!rule.validate(value)) {
        result.errors.push(rule.errorMessage)
        result.isValid = false
      }
    })
    return result
  }
  public getFieldValidationRules(): \'ValidationRules\' {
    return {
      name: [
        {
          validate: (value: str) => value.length >= 2,
          errorMessage: 'Name must be at least 2 characters long',
        },
        {
          validate: (value: str) => value.length <= 50,
          errorMessage: 'Name must not exceed 50 characters',
        },
        {
          validate: (value: str) => /^[a-zA-Z\s'-]+$/.test(value),
          errorMessage: 'Name can only contain letters, spaces, hyphens, and apostrophes',
        },
      ],
      race: [
        {
          validate: (value: str) => value.length > 0,
          errorMessage: 'Race must be selected',
        },
      ],
      class: [
        {
          validate: (value: str) => value.length > 0,
          errorMessage: 'Class must be selected',
        },
      ],
      background: [
        {
          validate: (value: str) => value.length > 0,
          errorMessage: 'Background must be selected',
        },
      ],
      level: [
        {
          validate: (value: float) => value >= 1 && value <= 20,
          errorMessage: 'Level must be between 1 and 20',
        },
      ],
      gold: [
        {
          validate: (value: float) => value >= 0,
          errorMessage: 'Gold cannot be negative',
        },
      ],
    }
  }
  public formatErrorMessage(error: Any): str {
    if (error instanceof Error) {
      return error.message
    }
    if (typeof error === 'string') {
      return error
    }
    if (error?.message) {
      return error.message
    }
    return 'An unexpected error occurred'
  }
  public handleApiError(error: Any): \'ValidationResult\' {
    const result: \'ValidationResult\' = {
      isValid: false,
      errors: [],
      warnings: [],
      incompleteFields: [],
    }
    if (error.response?.status === 401) {
      result.errors.push('Authentication required. Please log in and try again.')
    } else if (error.response?.status === 403) {
      result.errors.push('You do not have permission to perform this action.')
    } else if (error.response?.status === 404) {
      result.errors.push('The requested resource was not found.')
    } else if (error.response?.status === 429) {
      result.errors.push('Too many requests. Please try again later.')
    } else if (error.response?.data?.errors) {
      result.errors = error.response.data.errors
    } else if (error.response?.data?.message) {
      result.errors.push(error.response.data.message)
    } else if (error.message) {
      result.errors.push(this.formatErrorMessage(error))
    } else {
      result.errors.push('An unexpected error occurred. Please try again.')
    }
    return result
  }
}