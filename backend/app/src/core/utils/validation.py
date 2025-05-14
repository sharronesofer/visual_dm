from typing import Any, List


function validateRequired<T>(value: T | undefined | null, fieldName: str): T {
  if (value === undefined || value === null) {
    throw new ValidationError(`${fieldName} is required`)
  }
  return value
}
function validateEmail(email: str): bool {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email)) {
    throw new ValidationError('Invalid email format')
  }
  return true
}
function validateLength(value: str, fieldName: str, min: float, max: float): bool {
  if (value.length < min || value.length > max) {
    throw new ValidationError(`${fieldName} must be between ${min} and ${max} characters`)
  }
  return true
}
function validateNumber(value: float, fieldName: str, min?: float, max?: float): bool {
  if (min !== undefined && value < min) {
    throw new ValidationError(`${fieldName} must be greater than or equal to ${min}`)
  }
  if (max !== undefined && value > max) {
    throw new ValidationError(`${fieldName} must be less than or equal to ${max}`)
  }
  return true
}
function validateArray<T>(array: List[T], fieldName: str, minLength?: float, maxLength?: float): bool {
  if (minLength !== undefined && array.length < minLength) {
    throw new ValidationError(`${fieldName} must contain at least ${minLength} items`)
  }
  if (maxLength !== undefined && array.length > maxLength) {
    throw new ValidationError(`${fieldName} must contain at most ${maxLength} items`)
  }
  return true
} 