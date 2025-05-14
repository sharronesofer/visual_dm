from typing import Any, List



class POIValidator:
    validate(poi: POI): \'ValidationResult\'
ValidationError = {
  code: str
  message: str
  remediation: str
}
ValidationWarning = {
  code: str
  message: str
}
class ValidationResult {
  errors: List[ValidationError] = []
  warnings: List[ValidationWarning] = []
  isValid(): bool {
    return this.errors.length === 0
  }
  addError(code: str, message: str, remediation: str): void {
    this.errors.push({ code, message, remediation })
  }
  addWarning(code: str, message: str): void {
    this.warnings.push({ code, message })
  }
}
class SchemaValidator implements POIValidator {
  validate(poi: POI): \'ValidationResult\' {
    const result = new ValidationResult()
    if (!poi.id) result.addError('missing_id', 'POI is missing id', 'Add a unique id')
    if (!poi.type) result.addError('missing_type', 'POI is missing type', 'Specify a POI type')
    if (!poi.name) result.addWarning('missing_name', 'POI is missing name')
    if (!poi.layout || !poi.layout.rooms || poi.layout.rooms.length === 0) {
      result.addError('missing_layout', 'POI has no rooms/layout', 'Generate at least one room')
    }
    return result
  }
}
class NarrativeConsistencyValidator implements POIValidator {
  static seenDescriptions = new Set<string>()
  validate(poi: POI): \'ValidationResult\' {
    const result = new ValidationResult()
    if (!poi.description || poi.description.trim() === '') {
      result.addWarning('empty_description', 'POI description is empty')
    } else if (NarrativeConsistencyValidator.seenDescriptions.has(poi.description)) {
      result.addWarning('duplicate_description', 'POI description is duplicated')
    } else {
      NarrativeConsistencyValidator.seenDescriptions.add(poi.description)
    }
    return result
  }
}
class DifficultyScalingValidator implements POIValidator {
  validate(poi: POI): \'ValidationResult\' {
    const result = new ValidationResult()
    const difficulty = (poi as any).properties?.difficulty
    const region = (poi as any).properties?.region
    if (region && typeof difficulty === 'number') {
      if (region === 'starter' && difficulty > 3) {
        result.addError(
          'difficulty_too_high',
          'Starter region POI has high difficulty',
          'Lower difficulty for starter region'
        )
      }
      if (region === 'endgame' && difficulty < 7) {
        result.addWarning('difficulty_too_low', 'Endgame region POI has low difficulty')
      }
    }
    return result
  }
}
class ComprehensivePOIValidator implements POIValidator {
  private validators: List[POIValidator] = [
    new SchemaValidator(),
    new NarrativeConsistencyValidator(),
    new DifficultyScalingValidator(),
  ]
  validate(poi: POI): \'ValidationResult\' {
    const result = new ValidationResult()
    this.validators.forEach(validator => {
      const validationResult = validator.validate(poi)
      result.errors.push(...validationResult.errors)
      result.warnings.push(...validationResult.warnings)
    })
    return result
  }
}