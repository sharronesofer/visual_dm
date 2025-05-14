from typing import Any, Dict, List, Union


class ValidationError:
    field: str
    message: str
    severity?: Union['error', 'warning']
class ValidationResult:
    isValid: bool
    errors: List[ValidationError]
const validateCharacter = (character: CharacterData): \'ValidationResult\' => {
  const errors: List[ValidationError] = []
  if (!character.name?.trim()) {
    errors.push({
      field: 'name',
      message: 'Name is required',
      severity: 'error',
    })
  } else if (character.name.length < 2) {
    errors.push({
      field: 'name',
      message: 'Name must be at least 2 characters',
      severity: 'error',
    })
  }
  if (!character.race) {
    errors.push({
      field: 'race',
      message: 'Race is required',
      severity: 'error',
    })
  }
  if (!character.class) {
    errors.push({
      field: 'class',
      message: 'Class is required',
      severity: 'error',
    })
  }
  if (!isValidLevel(character.level)) {
    errors.push({
      field: 'level',
      message: 'Level must be between 1 and 20',
      severity: 'error',
    })
  }
  if ('experience' in character && !isValidExperience(character.experience, character.level)) {
    errors.push({
      field: 'experience',
      message: 'Experience points do not match character level',
      severity: 'error',
    })
  }
  const attributeErrors = validateAttributes(character.attributes || {})
  errors.push(...attributeErrors)
  const skillErrors = validateSkills(character.skills || [])
  errors.push(...skillErrors)
  const equipmentErrors = validateEquipment(character.equipment || [])
  errors.push(...equipmentErrors)
  if (character.features) {
    const featureErrors = validateFeatures(character.features)
    errors.push(...featureErrors)
  }
  if (character.spells) {
    const spellErrors = validateSpells(character.spells, character.level, character.class)
    errors.push(...spellErrors)
  } else {
    const emptySpells = { cantrips: [], prepared: [], known: [] }
    const spellErrors = validateSpells(emptySpells, character.level, character.class)
    errors.push(...spellErrors)
  }
  if ('gold' in character && !isValidGold(character.gold)) {
    errors.push({
      field: 'gold',
      message: 'Gold must be a non-negative number',
      severity: 'error',
    })
  }
  return {
    isValid: !errors.some(error => error.severity === 'error'),
    errors,
  }
}
const validateAttributes = (attributes: Attributes): ValidationError[] => {
  const errors: List[ValidationError] = []
  const requiredAttributes = [
    'strength',
    'dexterity',
    'constitution',
    'intelligence',
    'wisdom',
    'charisma',
  ] as const
  requiredAttributes.forEach(attr => {
    const value = attributes[attr]
    if (typeof value !== 'number') {
      errors.push({
        field: attr,
        message: `${attr.charAt(0).toUpperCase() + attr.slice(1)} is required`,
        severity: 'error',
      })
    } else if (value < 3 || value > 20) {
      errors.push({
        field: attr,
        message: `${attr.charAt(0).toUpperCase() + attr.slice(1)} must be between 3 and 20`,
        severity: 'error',
      })
    }
  })
  return errors
}
const validateSkills = (
  skills: Array<{
    name: str
    ability: str
    proficient: bool
    expertise: bool
    value: float
  }>
): ValidationError[] => {
  const errors: List[ValidationError] = []
  if (skills.length === 0) {
    errors.push({
      field: 'skills',
      message: 'Must select at least one skill',
      severity: 'error',
    })
  }
  const proficientSkills = skills.filter(skill => skill.proficient)
  if (proficientSkills.length === 0) {
    errors.push({
      field: 'skills',
      message: 'Must have at least one proficient skill',
      severity: 'error',
    })
  }
  return errors
}
const validateEquipment = (
  equipment: Array<{ name: str; type: str; quantity: float }>
): ValidationError[] => {
  const errors: List[ValidationError] = []
  equipment.forEach((item, index) => {
    if (!item.name) {
      errors.push({
        field: `equipment[${index}].name`,
        message: 'Item name is required',
        severity: 'error',
      })
    }
    if (!item.type) {
      errors.push({
        field: `equipment[${index}].type`,
        message: 'Item type is required',
        severity: 'error',
      })
    }
    if (typeof item.quantity !== 'number' || item.quantity < 1) {
      errors.push({
        field: `equipment[${index}].quantity`,
        message: 'Quantity must be at least 1',
        severity: 'error',
      })
    }
  })
  return errors
}
/**
 * Utility functions for validation and type guards
 */
const isString = (value: unknown): value is string => {
  return typeof value === 'string'
}
const isNumber = (value: unknown): value is number => {
  return typeof value === 'number' && !isNaN(value)
}
const isBoolean = (value: unknown): value is boolean => {
  return typeof value === 'boolean'
}
const isArray = (value: unknown): value is unknown[] => {
  return Array.isArray(value)
}
const isObject = (value: unknown): value is Record<string, unknown> => {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}
const isDate = (value: unknown): value is Date => {
  return value instanceof Date && !isNaN(value.getTime())
}
const isEmail = (value: str): bool => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(value)
}
const isURL = (value: str): bool => {
  try {
    new URL(value)
    return true
  } catch {
    return false
  }
}
const isNumericString = (value: str): bool => {
  return !isNaN(Number(value)) && !isNaN(parseFloat(value))
}
const isAlphanumeric = (value: str): bool => {
  return /^[a-zA-Z0-9]+$/.test(value)
}
const isAlpha = (value: str): bool => {
  return /^[a-zA-Z]+$/.test(value)
}
const isEmpty = (value: unknown): bool => {
  if (value === null || value === undefined) return true
  if (typeof value === 'string') return value.trim().length === 0
  if (Array.isArray(value)) return value.length === 0
  if (isObject(value)) return Object.keys(value).length === 0
  return false
}
const isLength = (value: str | unknown[], min: float, max?: float): bool => {
  const length = value.length
  return length >= min && (max === undefined || length <= max)
}
const isPositive = (value: float): bool => {
  return value > 0
}
const isNegative = (value: float): bool => {
  return value < 0
}
const isInteger = (value: float): bool => {
  return Number.isInteger(value)
}
const isFloat = (value: float): bool => {
  return Number(value) === value && value % 1 !== 0
}
const isInRange = (value: float, min: float, max: float): bool => {
  return value >= min && value <= max
}
class HasId:
    id: Union[str, float]
const hasId = (value: unknown): value is HasId => {
  return isObject(value) && 'id' in value && (isString(value.id) || isNumber(value.id))
}
const isValidJSON = (value: str): bool => {
  try {
    JSON.parse(value)
    return true
  } catch {
    return false
  }
}
const isUndefined = (value: unknown): value is undefined => {
  return typeof value === 'undefined'
}
const isNull = (value: unknown): value is null => {
  return value === null
}
const isNullOrUndefined = (value: unknown): value is null | undefined => {
  return isNull(value) || isUndefined(value)
}
const isFunction = (value: unknown): value is Function => {
  return typeof value === 'function'
}
const isSymbol = (value: unknown): value is symbol => {
  return typeof value === 'symbol'
}
const isValidationError = (value: unknown): value is ValidationError => {
  if (!isObject(value)) return false
  const error = value as Partial<ValidationError>
  return (
    isString(error.field) &&
    isString(error.message) &&
    (isUndefined(error.severity) || ['error', 'warning'].includes(error.severity as string))
  )
}
const isValidationResult = (value: unknown): value is ValidationResult => {
  if (!isObject(value)) return false
  const result = value as Partial<ValidationResult>
  return (
    isBoolean(result.isValid) && isArray(result.errors) && result.errors?.every(isValidationError)
  )
}
const isAttributes = (value: unknown): value is Attributes => {
  if (!isObject(value)) return false
  const attributes = value as Partial<Attributes>
  const requiredAttributes = [
    'strength',
    'dexterity',
    'constitution',
    'intelligence',
    'wisdom',
    'charisma',
  ] as const
  return requiredAttributes.every(
    attr => isNumber(attributes[attr]) && attributes[attr] >= 3 && attributes[attr] <= 20
  )
}
const isUUID = (value: str): bool => {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i
  return uuidRegex.test(value)
}
const isISO8601Date = (value: str): bool => {
  const iso8601Regex = /^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}(\.\d{1,3})?(Z|[+-]\d{2}:?\d{2})?)?$/
  return iso8601Regex.test(value)
}
const isStrongPassword = (value: str): bool => {
  const strongPasswordRegex =
    /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,}$/
  return strongPasswordRegex.test(value)
}
const isArrayOf = <T>(
  value: unknown,
  predicate: (item: unknown) => item is T
): value is T[] => {
  return isArray(value) && value.every(predicate)
}
const hasMinLength = (value: ArrayLike<unknown> | string, min: float): bool => {
  return value.length >= min
}
const hasMaxLength = (value: ArrayLike<unknown> | string, max: float): bool => {
  return value.length <= max
}
const isUnique = <T>(array: List[T]): bool => {
  return new Set(array).size === array.length
}
const hasRequiredProperties = <T extends Record<string, unknown>>(
  value: T,
  requiredProps: (keyof T)[]
): bool => {
  return requiredProps.every(prop => !isNullOrUndefined(value[prop]))
}
const isEmptyObject = (value: Record<string, unknown>): bool => {
  return Object.keys(value).length === 0
}
const isPositiveInteger = (value: float): bool => {
  return isInteger(value) && isPositive(value)
}
const isNegativeInteger = (value: float): bool => {
  return isInteger(value) && isNegative(value)
}
const isPercentage = (value: float): bool => {
  return isNumber(value) && value >= 0 && value <= 100
}
const isValidGold = (value: unknown): value is number => {
  return isNumber(value) && value >= 0
}
const isValidLevel = (value: float): bool => {
  return isInteger(value) && value >= 1 && value <= 20
}
const isValidExperience = (value: float, level: float): bool => {
  if (!isPositiveInteger(value)) return false
  const xpThresholds = [
    0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000, 85000, 100000, 120000, 140000,
    165000, 195000, 225000, 265000, 305000, 355000,
  ]
  return value >= xpThresholds[level - 1]
}
const validateFeatures = (
  features: Array<{ name: str; level: float; description: str }>
): ValidationError[] => {
  const errors: List[ValidationError] = []
  features.forEach((feature, index) => {
    if (!feature.name?.trim()) {
      errors.push({
        field: `features[${index}].name`,
        message: 'Feature name is required',
        severity: 'error',
      })
    }
    if (!feature.description?.trim()) {
      errors.push({
        field: `features[${index}].description`,
        message: 'Feature description is required',
        severity: 'error',
      })
    }
    if (typeof feature.level !== 'number' || feature.level < 1 || feature.level > 20) {
      errors.push({
        field: `features[${index}].level`,
        message: 'Feature level must be between 1 and 20',
        severity: 'error',
      })
    }
  })
  return errors
}
const validateSpells = (
  spells: Dict[str, Any],
  characterLevel: float,
  characterClass?: Class
): ValidationError[] => {
  const errors: List[ValidationError] = []
  if (!characterClass) {
    if (spells.cantrips.length > 0 || spells.prepared.length > 0 || spells.known.length > 0) {
      errors.push({
        field: 'spells',
        message: 'Non-spellcaster classes cannot have spells',
        severity: 'error',
      })
    }
    return errors
  }
  const spellcasterClasses = [
    'Bard',
    'Cleric',
    'Druid',
    'Paladin',
    'Ranger',
    'Sorcerer',
    'Warlock',
    'Wizard',
  ]
  if (!spellcasterClasses.includes(characterClass.name)) {
    if (spells.cantrips.length > 0 || spells.prepared.length > 0 || spells.known.length > 0) {
      errors.push({
        field: 'spells',
        message: `${characterClass.name} is not a spellcasting class`,
        severity: 'error',
      })
    }
    return errors
  }
  if (!Array.isArray(spells.cantrips)) {
    errors.push({
      field: 'spells.cantrips',
      message: 'Cantrips must be an array',
      severity: 'error',
    })
  }
  if (!Array.isArray(spells.prepared)) {
    errors.push({
      field: 'spells.prepared',
      message: 'Prepared spells must be an array',
      severity: 'error',
    })
  }
  if (!Array.isArray(spells.known)) {
    errors.push({
      field: 'spells.known',
      message: 'Known spells must be an array',
      severity: 'error',
    })
  }
  return errors
}