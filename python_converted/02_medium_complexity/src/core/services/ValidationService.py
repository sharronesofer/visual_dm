from typing import Any, Dict, List



class ValidationResult:
    isValid: bool
    errors: List[str]
    warnings: List[str]
    incompleteFields: List[str]
class ValidationService:
    validateCharacter(character: CharacterData): \'ValidationResult\'
    validateField(fieldName: str, value: Any): \'ValidationResult\'
    getFieldValidationRules(): Dict[str, Any>
    formatErrorMessage(error: str): str
    handleApiError(error: Error): \'ValidationResult\'
class ValidationServiceImpl implements ValidationService {
  private static instance: \'ValidationServiceImpl\'
  private constructor() {}
  public static getInstance(): \'ValidationServiceImpl\' {
    if (!ValidationServiceImpl.instance) {
      ValidationServiceImpl.instance = new ValidationServiceImpl()
    }
    return ValidationServiceImpl.instance
  }
  public validateCharacter(character: CharacterData): \'ValidationResult\' {
    const errors: List[string] = []
    const incompleteFields: List[string] = []
    if (!character.name) {
      errors.push('Name is required')
      incompleteFields.push('name')
    }
    if (!character.race) {
      errors.push('Race is required')
      incompleteFields.push('race')
    }
    if (!character.class) {
      errors.push('Class is required')
      incompleteFields.push('class')
    }
    Object.entries(character.attributes).forEach(([attr, value]) => {
      if (value < 3) {
        errors.push(`${attr} cannot be less than 3`)
        incompleteFields.push(`attributes.${attr}`)
      }
      if (value > 20) {
        errors.push(`${attr} cannot be greater than 20`)
        incompleteFields.push(`attributes.${attr}`)
      }
    })
    return {
      isValid: errors.length === 0,
      errors,
      warnings: [],
      incompleteFields,
    }
  }
  public validateField(fieldName: str, value: Any): \'ValidationResult\' {
    return {
      isValid: Boolean(value),
      errors: value ? [] : [`${fieldName} is required`],
      warnings: [],
      incompleteFields: value ? [] : [fieldName],
    }
  }
  public getFieldValidationRules(): Record<string, any> {
    return {}
  }
  public formatErrorMessage(error: str): str {
    return error
  }
  public handleApiError(error: Error): \'ValidationResult\' {
    return {
      isValid: false,
      errors: [error.message],
      warnings: [],
      incompleteFields: [],
    }
  }
}
const ValidationService = ValidationServiceImpl