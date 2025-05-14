import { CharacterData, Attributes, Character, Class } from '../types/character';

export interface ValidationError {
  field: string;
  message: string;
  severity?: 'error' | 'warning';
}

export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
}

export const validateCharacter = (character: CharacterData): ValidationResult => {
  const errors: ValidationError[] = [];

  // Required fields validation
  if (!character.name?.trim()) {
    errors.push({
      field: 'name',
      message: 'Name is required',
      severity: 'error',
    });
  } else if (character.name.length < 2) {
    errors.push({
      field: 'name',
      message: 'Name must be at least 2 characters',
      severity: 'error',
    });
  }

  if (!character.race) {
    errors.push({
      field: 'race',
      message: 'Race is required',
      severity: 'error',
    });
  }

  if (!character.class) {
    errors.push({
      field: 'class',
      message: 'Class is required',
      severity: 'error',
    });
  }

  // Level validation
  if (!isValidLevel(character.level)) {
    errors.push({
      field: 'level',
      message: 'Level must be between 1 and 20',
      severity: 'error',
    });
  }

  // Experience validation
  if ('experience' in character && !isValidExperience(character.experience, character.level)) {
    errors.push({
      field: 'experience',
      message: 'Experience points do not match character level',
      severity: 'error',
    });
  }

  // Attribute validation
  const attributeErrors = validateAttributes(character.attributes || {});
  errors.push(...attributeErrors);

  // Skills validation
  const skillErrors = validateSkills(character.skills || []);
  errors.push(...skillErrors);

  // Equipment validation
  const equipmentErrors = validateEquipment(character.equipment || []);
  errors.push(...equipmentErrors);

  // Features validation
  if (character.features) {
    const featureErrors = validateFeatures(character.features);
    errors.push(...featureErrors);
  }

  // Spells validation
  if (character.spells) {
    const spellErrors = validateSpells(character.spells, character.level, character.class);
    errors.push(...spellErrors);
  } else {
    // If spells is undefined, initialize with empty arrays
    const emptySpells = { cantrips: [], prepared: [], known: [] };
    const spellErrors = validateSpells(emptySpells, character.level, character.class);
    errors.push(...spellErrors);
  }

  // Gold validation (if present)
  if ('gold' in character && !isValidGold(character.gold)) {
    errors.push({
      field: 'gold',
      message: 'Gold must be a non-negative number',
      severity: 'error',
    });
  }

  return {
    isValid: !errors.some(error => error.severity === 'error'),
    errors,
  };
};

export const validateAttributes = (attributes: Attributes): ValidationError[] => {
  const errors: ValidationError[] = [];
  const requiredAttributes = [
    'strength',
    'dexterity',
    'constitution',
    'intelligence',
    'wisdom',
    'charisma',
  ] as const;

  requiredAttributes.forEach(attr => {
    const value = attributes[attr];
    if (typeof value !== 'number') {
      errors.push({
        field: attr,
        message: `${attr.charAt(0).toUpperCase() + attr.slice(1)} is required`,
        severity: 'error',
      });
    } else if (value < 3 || value > 20) {
      errors.push({
        field: attr,
        message: `${attr.charAt(0).toUpperCase() + attr.slice(1)} must be between 3 and 20`,
        severity: 'error',
      });
    }
  });

  return errors;
};

export const validateSkills = (
  skills: Array<{
    name: string;
    ability: string;
    proficient: boolean;
    expertise: boolean;
    value: number;
  }>
): ValidationError[] => {
  const errors: ValidationError[] = [];

  if (skills.length === 0) {
    errors.push({
      field: 'skills',
      message: 'Must select at least one skill',
      severity: 'error',
    });
  }

  const proficientSkills = skills.filter(skill => skill.proficient);
  if (proficientSkills.length === 0) {
    errors.push({
      field: 'skills',
      message: 'Must have at least one proficient skill',
      severity: 'error',
    });
  }

  return errors;
};

export const validateEquipment = (
  equipment: Array<{ name: string; type: string; quantity: number }>
): ValidationError[] => {
  const errors: ValidationError[] = [];

  equipment.forEach((item, index) => {
    if (!item.name) {
      errors.push({
        field: `equipment[${index}].name`,
        message: 'Item name is required',
        severity: 'error',
      });
    }

    if (!item.type) {
      errors.push({
        field: `equipment[${index}].type`,
        message: 'Item type is required',
        severity: 'error',
      });
    }

    if (typeof item.quantity !== 'number' || item.quantity < 1) {
      errors.push({
        field: `equipment[${index}].quantity`,
        message: 'Quantity must be at least 1',
        severity: 'error',
      });
    }
  });

  return errors;
};

/**
 * Utility functions for validation and type guards
 */

// Type Guards
export const isString = (value: unknown): value is string => {
  return typeof value === 'string';
};

export const isNumber = (value: unknown): value is number => {
  return typeof value === 'number' && !isNaN(value);
};

export const isBoolean = (value: unknown): value is boolean => {
  return typeof value === 'boolean';
};

export const isArray = (value: unknown): value is unknown[] => {
  return Array.isArray(value);
};

export const isObject = (value: unknown): value is Record<string, unknown> => {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
};

export const isDate = (value: unknown): value is Date => {
  return value instanceof Date && !isNaN(value.getTime());
};

// Common Validations
export const isEmail = (value: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(value);
};

export const isURL = (value: string): boolean => {
  try {
    new URL(value);
    return true;
  } catch {
    return false;
  }
};

export const isNumericString = (value: string): boolean => {
  return !isNaN(Number(value)) && !isNaN(parseFloat(value));
};

export const isAlphanumeric = (value: string): boolean => {
  return /^[a-zA-Z0-9]+$/.test(value);
};

export const isAlpha = (value: string): boolean => {
  return /^[a-zA-Z]+$/.test(value);
};

export const isEmpty = (value: unknown): boolean => {
  if (value === null || value === undefined) return true;
  if (typeof value === 'string') return value.trim().length === 0;
  if (Array.isArray(value)) return value.length === 0;
  if (isObject(value)) return Object.keys(value).length === 0;
  return false;
};

export const isLength = (value: string | unknown[], min: number, max?: number): boolean => {
  const length = value.length;
  return length >= min && (max === undefined || length <= max);
};

export const isPositive = (value: number): boolean => {
  return value > 0;
};

export const isNegative = (value: number): boolean => {
  return value < 0;
};

export const isInteger = (value: number): boolean => {
  return Number.isInteger(value);
};

export const isFloat = (value: number): boolean => {
  return Number(value) === value && value % 1 !== 0;
};

export const isInRange = (value: number, min: number, max: number): boolean => {
  return value >= min && value <= max;
};

// Custom Type Guards for Application-Specific Types
export interface HasId {
  id: string | number;
}

export const hasId = (value: unknown): value is HasId => {
  return isObject(value) && 'id' in value && (isString(value.id) || isNumber(value.id));
};

export const isValidJSON = (value: string): boolean => {
  try {
    JSON.parse(value);
    return true;
  } catch {
    return false;
  }
};

// Additional Primitive Type Validations
export const isUndefined = (value: unknown): value is undefined => {
  return typeof value === 'undefined';
};

export const isNull = (value: unknown): value is null => {
  return value === null;
};

export const isNullOrUndefined = (value: unknown): value is null | undefined => {
  return isNull(value) || isUndefined(value);
};

export const isFunction = (value: unknown): value is Function => {
  return typeof value === 'function';
};

export const isSymbol = (value: unknown): value is symbol => {
  return typeof value === 'symbol';
};

// Custom Type Predicates for Application Types
export const isValidationError = (value: unknown): value is ValidationError => {
  if (!isObject(value)) return false;

  const error = value as Partial<ValidationError>;
  return (
    isString(error.field) &&
    isString(error.message) &&
    (isUndefined(error.severity) || ['error', 'warning'].includes(error.severity as string))
  );
};

export const isValidationResult = (value: unknown): value is ValidationResult => {
  if (!isObject(value)) return false;

  const result = value as Partial<ValidationResult>;
  return (
    isBoolean(result.isValid) && isArray(result.errors) && result.errors?.every(isValidationError)
  );
};

export const isAttributes = (value: unknown): value is Attributes => {
  if (!isObject(value)) return false;

  const attributes = value as Partial<Attributes>;
  const requiredAttributes = [
    'strength',
    'dexterity',
    'constitution',
    'intelligence',
    'wisdom',
    'charisma',
  ] as const;

  return requiredAttributes.every(
    attr => isNumber(attributes[attr]) && attributes[attr] >= 3 && attributes[attr] <= 20
  );
};

// Additional String Validations
export const isUUID = (value: string): boolean => {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  return uuidRegex.test(value);
};

export const isISO8601Date = (value: string): boolean => {
  const iso8601Regex = /^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}(\.\d{1,3})?(Z|[+-]\d{2}:?\d{2})?)?$/;
  return iso8601Regex.test(value);
};

export const isStrongPassword = (value: string): boolean => {
  // At least 12 characters, 1 uppercase, 1 lowercase, 1 number, 1 special character
  const strongPasswordRegex =
    /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{12,}$/;
  return strongPasswordRegex.test(value);
};

// Array Validations
export const isArrayOf = <T>(
  value: unknown,
  predicate: (item: unknown) => item is T
): value is T[] => {
  return isArray(value) && value.every(predicate);
};

export const hasMinLength = (value: ArrayLike<unknown> | string, min: number): boolean => {
  return value.length >= min;
};

export const hasMaxLength = (value: ArrayLike<unknown> | string, max: number): boolean => {
  return value.length <= max;
};

export const isUnique = <T>(array: T[]): boolean => {
  return new Set(array).size === array.length;
};

// Object Validations
export const hasRequiredProperties = <T extends Record<string, unknown>>(
  value: T,
  requiredProps: (keyof T)[]
): boolean => {
  return requiredProps.every(prop => !isNullOrUndefined(value[prop]));
};

export const isEmptyObject = (value: Record<string, unknown>): boolean => {
  return Object.keys(value).length === 0;
};

// Numeric Validations
export const isPositiveInteger = (value: number): boolean => {
  return isInteger(value) && isPositive(value);
};

export const isNegativeInteger = (value: number): boolean => {
  return isInteger(value) && isNegative(value);
};

export const isPercentage = (value: number): boolean => {
  return isNumber(value) && value >= 0 && value <= 100;
};

// Additional Type Guards
export const isValidGold = (value: unknown): value is number => {
  return isNumber(value) && value >= 0;
};

export const isValidLevel = (value: number): boolean => {
  return isInteger(value) && value >= 1 && value <= 20;
};

export const isValidExperience = (value: number, level: number): boolean => {
  if (!isPositiveInteger(value)) return false;

  const xpThresholds = [
    0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000, 85000, 100000, 120000, 140000,
    165000, 195000, 225000, 265000, 305000, 355000,
  ];

  return value >= xpThresholds[level - 1];
};

export const validateFeatures = (
  features: Array<{ name: string; level: number; description: string }>
): ValidationError[] => {
  const errors: ValidationError[] = [];

  features.forEach((feature, index) => {
    if (!feature.name?.trim()) {
      errors.push({
        field: `features[${index}].name`,
        message: 'Feature name is required',
        severity: 'error',
      });
    }

    if (!feature.description?.trim()) {
      errors.push({
        field: `features[${index}].description`,
        message: 'Feature description is required',
        severity: 'error',
      });
    }

    if (typeof feature.level !== 'number' || feature.level < 1 || feature.level > 20) {
      errors.push({
        field: `features[${index}].level`,
        message: 'Feature level must be between 1 and 20',
        severity: 'error',
      });
    }
  });

  return errors;
};

export const validateSpells = (
  spells: { cantrips: string[]; prepared: string[]; known: string[] },
  characterLevel: number,
  characterClass?: Class
): ValidationError[] => {
  const errors: ValidationError[] = [];

  if (!characterClass) {
    if (spells.cantrips.length > 0 || spells.prepared.length > 0 || spells.known.length > 0) {
      errors.push({
        field: 'spells',
        message: 'Non-spellcaster classes cannot have spells',
        severity: 'error',
      });
    }
    return errors;
  }

  // Check if the class is a spellcaster
  const spellcasterClasses = [
    'Bard',
    'Cleric',
    'Druid',
    'Paladin',
    'Ranger',
    'Sorcerer',
    'Warlock',
    'Wizard',
  ];
  if (!spellcasterClasses.includes(characterClass.name)) {
    if (spells.cantrips.length > 0 || spells.prepared.length > 0 || spells.known.length > 0) {
      errors.push({
        field: 'spells',
        message: `${characterClass.name} is not a spellcasting class`,
        severity: 'error',
      });
    }
    return errors;
  }

  // Validate cantrips
  if (!Array.isArray(spells.cantrips)) {
    errors.push({
      field: 'spells.cantrips',
      message: 'Cantrips must be an array',
      severity: 'error',
    });
  }

  // Validate prepared spells
  if (!Array.isArray(spells.prepared)) {
    errors.push({
      field: 'spells.prepared',
      message: 'Prepared spells must be an array',
      severity: 'error',
    });
  }

  // Validate known spells
  if (!Array.isArray(spells.known)) {
    errors.push({
      field: 'spells.known',
      message: 'Known spells must be an array',
      severity: 'error',
    });
  }

  return errors;
};
