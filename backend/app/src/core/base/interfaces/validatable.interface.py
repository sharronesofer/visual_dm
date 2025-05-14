from typing import Any


/**
 * Validatable interface
 * @module core/base/interfaces/validatable
 */
/**
 * Interface for services that support validation
 */
interface IValidatableService<T extends BaseEntity> {
  /**
   * Validate entity data before creation
   * @param data The entity data to validate
   */
  validateCreate(data: Omit<T, keyof BaseEntity>): Promise<ValidationResult>
  /**
   * Validate entity data before update
   * @param id The entity ID
   * @param data The update data to validate
   */
  validateUpdate(id: T['id'], data: Partial<T>): Promise<ValidationResult>
  /**
   * Validate a specific field
   * @param field The field to validate
   * @param value The value to validate
   */
  validateField(field: keyof T, value: Any): Promise<ValidationResult>
  /**
   * Get validation rules for a field
   * @param field The field to get rules for
   */
  getValidationRules(field: keyof T): Record<string, any>
  /**
   * Get all validation rules
   */
  getAllValidationRules(): Record<keyof T, Record<string, any>>
  /**
   * Add a custom validation rule
   * @param field The field to add the rule for
   * @param rule The validation rule to add
   */
  addValidationRule(field: keyof T, rule: Record<string, any>): void
  /**
   * Remove a validation rule
   * @param field The field to remove the rule from
   * @param ruleName The name of the rule to remove
   */
  removeValidationRule(field: keyof T, ruleName: str): void
} 