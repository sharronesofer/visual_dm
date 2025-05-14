import { ServiceError } from './types';

export class ValidationError extends Error implements ServiceError {
  code: string;
  details?: any;

  constructor(code: string, message: string, details?: any) {
    super(message);
    this.name = 'ValidationError';
    this.code = code;
    this.details = details;
    Object.setPrototypeOf(this, ValidationError.prototype);
  }
}

export class ThumbnailServiceError extends Error implements ServiceError {
  code: string;
  details?: any;

  constructor(code: string, message: string, details?: any) {
    super(message);
    this.name = 'ThumbnailServiceError';
    this.code = code;
    this.details = details;
    Object.setPrototypeOf(this, ThumbnailServiceError.prototype);
  }
} 