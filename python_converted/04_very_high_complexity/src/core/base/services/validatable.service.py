from typing import Any



/**
 * Validatable service implementation
 * @module core/base/services/validatable
 */
/**
 * Abstract validatable service class that extends BaseService and implements IValidatableService
 */
abstract class ValidatableService<T extends BaseEntity> extends BaseService<T> implements IValidatableService<T> {
  protected validationRules: Map<keyof T, Record<string, any>> = new Map()
  /**
   * Validate entity data before creation
   */
  async validateCreate(data: Omit<T, keyof BaseEntity>): Promise<ValidationResult> {
    try {
      const rules = this.getAllValidationRules()
      const errors = []
      for (const [field, fieldRules] of Object.entries(rules)) {
        const value = data[field as keyof typeof data]
        const fieldValidation = await this.validateField(field as keyof T, value)
        if (!fieldValidation.isValid) {
          errors.push(...fieldValidation.errors)
        }
      }
      return {
        isValid: errors.length === 0,
        errors
      }
    } catch (error) {
      console.error('Validation error:', error)
      return {
        isValid: false,
        errors: [{
          field: '*',
          message: 'Validation failed unexpectedly',
          code: 'VALIDATION_ERROR'
        }]
      }
    }
  }
  /**
   * Validate entity data before update
   */
  async validateUpdate(id: T['id'], data: Partial<T>): Promise<ValidationResult> {
    try {
      const errors = []
      for (const [field, value] of Object.entries(data)) {
        const fieldValidation = await this.validateField(field as keyof T, value)
        if (!fieldValidation.isValid) {
          errors.push(...fieldValidation.errors)
        }
      }
      return {
        isValid: errors.length === 0,
        errors
      }
    } catch (error) {
      console.error('Validation error:', error)
      return {
        isValid: false,
        errors: [{
          field: '*',
          message: 'Validation failed unexpectedly',
          code: 'VALIDATION_ERROR'
        }]
      }
    }
  }
  /**
   * Validate a specific field
   */
  async validateField(field: keyof T, value: Any): Promise<ValidationResult> {
    try {
      const rules = this.getValidationRules(field)
      const errors = []
      if (!rules || Object.keys(rules).length === 0) {
        return { isValid: true, errors: [] }
      }
      for (const [ruleName, ruleConfig] of Object.entries(rules)) {
        const isValid = await this.applyValidationRule(field, value, ruleName, ruleConfig)
        if (!isValid) {
          errors.push({
            field: String(field),
            message: this.getValidationMessage(field, ruleName, ruleConfig),
            code: `${String(field).toUpperCase()}_${ruleName.toUpperCase()}`,
            value
          })
        }
      }
      return {
        isValid: errors.length === 0,
        errors
      }
    } catch (error) {
      console.error('Field validation error:', error)
      return {
        isValid: false,
        errors: [{
          field: String(field),
          message: 'Field validation failed unexpectedly',
          code: 'FIELD_VALIDATION_ERROR',
          value
        }]
      }
    }
  }
  /**
   * Get validation rules for a field
   */
  getValidationRules(field: keyof T): Record<string, any> {
    return this.validationRules.get(field) || {}
  }
  /**
   * Get all validation rules
   */
  getAllValidationRules(): Record<keyof T, Record<string, any>> {
    const rules: Partial<Record<keyof T, Record<string, any>>> = {}
    this.validationRules.forEach((value, key) => {
      rules[key] = value
    })
    return rules as Record<keyof T, Record<string, any>>
  }
  /**
   * Add a custom validation rule
   */
  addValidationRule(field: keyof T, rule: Record<string, any>): void {
    const existingRules = this.validationRules.get(field) || {}
    this.validationRules.set(field, { ...existingRules, ...rule })
  }
  /**
   * Remove a validation rule
   */
  removeValidationRule(field: keyof T, ruleName: str): void {
    const rules = this.validationRules.get(field)
    if (rules) {
      const { [ruleName]: removed, ...remaining } = rules
      this.validationRules.set(field, remaining)
    }
  }
  /**
   * Helper method to apply a validation rule
   */
  protected abstract applyValidationRule(
    field: keyof T,
    value: Any,
    ruleName: str,
    ruleConfig: Any
  ): Promise<boolean>
  /**
   * Helper method to get validation error message
   */
  protected abstract getValidationMessage(
    field: keyof T,
    ruleName: str,
    ruleConfig: Any
  ): str
} 