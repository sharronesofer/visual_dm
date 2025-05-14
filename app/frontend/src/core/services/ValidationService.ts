import { CharacterData } from '../types/character';

export interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  incompleteFields: string[];
}

export interface ValidationService {
  validateCharacter(character: CharacterData): ValidationResult;
  validateField(fieldName: string, value: any): ValidationResult;
  getFieldValidationRules(): Record<string, any>;
  formatErrorMessage(error: string): string;
  handleApiError(error: Error): ValidationResult;
}

export class ValidationServiceImpl implements ValidationService {
  private static instance: ValidationServiceImpl;

  private constructor() {}

  public static getInstance(): ValidationServiceImpl {
    if (!ValidationServiceImpl.instance) {
      ValidationServiceImpl.instance = new ValidationServiceImpl();
    }
    return ValidationServiceImpl.instance;
  }

  public validateCharacter(character: CharacterData): ValidationResult {
    const errors: string[] = [];
    const incompleteFields: string[] = [];

    if (!character.name) {
      errors.push('Name is required');
      incompleteFields.push('name');
    }

    if (!character.race) {
      errors.push('Race is required');
      incompleteFields.push('race');
    }

    if (!character.class) {
      errors.push('Class is required');
      incompleteFields.push('class');
    }

    // Validate attributes
    Object.entries(character.attributes).forEach(([attr, value]) => {
      if (value < 3) {
        errors.push(`${attr} cannot be less than 3`);
        incompleteFields.push(`attributes.${attr}`);
      }
      if (value > 20) {
        errors.push(`${attr} cannot be greater than 20`);
        incompleteFields.push(`attributes.${attr}`);
      }
    });

    return {
      isValid: errors.length === 0,
      errors,
      warnings: [],
      incompleteFields,
    };
  }

  public validateField(fieldName: string, value: any): ValidationResult {
    return {
      isValid: Boolean(value),
      errors: value ? [] : [`${fieldName} is required`],
      warnings: [],
      incompleteFields: value ? [] : [fieldName],
    };
  }

  public getFieldValidationRules(): Record<string, any> {
    return {};
  }

  public formatErrorMessage(error: string): string {
    return error;
  }

  public handleApiError(error: Error): ValidationResult {
    return {
      isValid: false,
      errors: [error.message],
      warnings: [],
      incompleteFields: [],
    };
  }
}

export const ValidationService = ValidationServiceImpl;
