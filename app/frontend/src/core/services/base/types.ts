import { AxiosRequestConfig } from 'axios';

export interface ServiceConfig extends AxiosRequestConfig {
  baseURL?: string;
  timeout?: number;
  headers?: Record<string, string>;
}

export class ServiceError extends Error {
  public readonly code: string;
  public readonly details?: Record<string, any>;

  constructor(code: string, message: string, details?: Record<string, any>) {
    super(message);
    this.name = 'ServiceError';
    this.code = code;
    this.details = details;

    // Ensure proper prototype chain for instanceof checks
    Object.setPrototypeOf(this, ServiceError.prototype);
  }

  public toJSON(): Record<string, any> {
    return {
      name: this.name,
      code: this.code,
      message: this.message,
      details: this.details
    };
  }
}

export interface ValidationError {
  field: string;
  message: string;
}

export interface ServiceResponse<T = any> {
  success: boolean;
  data: T | null;
  error?: ServiceError;
  validationErrors?: ValidationError[];
} 