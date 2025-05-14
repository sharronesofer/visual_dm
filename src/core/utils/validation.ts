import { ValidationError } from './errors';

export function validateRequired<T>(value: T | undefined | null, fieldName: string): T {
  if (value === undefined || value === null) {
    throw new ValidationError(`${fieldName} is required`);
  }
  return value;
}

export function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    throw new ValidationError('Invalid email format');
  }
  return true;
}

export function validateLength(value: string, fieldName: string, min: number, max: number): boolean {
  if (value.length < min || value.length > max) {
    throw new ValidationError(`${fieldName} must be between ${min} and ${max} characters`);
  }
  return true;
}

export function validateNumber(value: number, fieldName: string, min?: number, max?: number): boolean {
  if (min !== undefined && value < min) {
    throw new ValidationError(`${fieldName} must be greater than or equal to ${min}`);
  }
  if (max !== undefined && value > max) {
    throw new ValidationError(`${fieldName} must be less than or equal to ${max}`);
  }
  return true;
}

export function validateArray<T>(array: T[], fieldName: string, minLength?: number, maxLength?: number): boolean {
  if (minLength !== undefined && array.length < minLength) {
    throw new ValidationError(`${fieldName} must contain at least ${minLength} items`);
  }
  if (maxLength !== undefined && array.length > maxLength) {
    throw new ValidationError(`${fieldName} must contain at most ${maxLength} items`);
  }
  return true;
} 