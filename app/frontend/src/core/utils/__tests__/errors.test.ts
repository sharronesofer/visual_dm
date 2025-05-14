import {
  AppError,
  NotFoundError,
  ValidationError,
  AuthorizationError,
  AuthenticationError,
} from '../errors';

describe('error utilities', () => {
  describe('AppError', () => {
    it('should create error with default status code', () => {
      const error = new AppError('TEST_ERROR', 'Test error message');
      expect(error).toBeInstanceOf(Error);
      expect(error.name).toBe('AppError');
      expect(error.code).toBe('TEST_ERROR');
      expect(error.message).toBe('Test error message');
      expect(error.statusCode).toBe(500);
    });

    it('should create error with custom status code', () => {
      const error = new AppError('TEST_ERROR', 'Test error message', 400);
      expect(error.statusCode).toBe(400);
    });
  });

  describe('NotFoundError', () => {
    it('should create error with formatted message', () => {
      const error = new NotFoundError('User', 123);
      expect(error).toBeInstanceOf(AppError);
      expect(error.name).toBe('NotFoundError');
      expect(error.code).toBe('NOT_FOUND');
      expect(error.message).toBe('User with id 123 not found');
      expect(error.statusCode).toBe(404);
    });
  });

  describe('ValidationError', () => {
    it('should create error with provided message', () => {
      const error = new ValidationError('Invalid input');
      expect(error).toBeInstanceOf(AppError);
      expect(error.name).toBe('ValidationError');
      expect(error.code).toBe('VALIDATION_ERROR');
      expect(error.message).toBe('Invalid input');
      expect(error.statusCode).toBe(400);
    });
  });

  describe('AuthorizationError', () => {
    it('should create error with provided message', () => {
      const error = new AuthorizationError('Insufficient permissions');
      expect(error).toBeInstanceOf(AppError);
      expect(error.name).toBe('AuthorizationError');
      expect(error.code).toBe('AUTHORIZATION_ERROR');
      expect(error.message).toBe('Insufficient permissions');
      expect(error.statusCode).toBe(403);
    });
  });

  describe('AuthenticationError', () => {
    it('should create error with provided message', () => {
      const error = new AuthenticationError('Invalid credentials');
      expect(error).toBeInstanceOf(AppError);
      expect(error.name).toBe('AuthenticationError');
      expect(error.code).toBe('AUTHENTICATION_ERROR');
      expect(error.message).toBe('Invalid credentials');
      expect(error.statusCode).toBe(401);
    });
  });

  describe('error inheritance', () => {
    it('should maintain proper instanceof chain', () => {
      const notFoundError = new NotFoundError('User', 123);
      const validationError = new ValidationError('Invalid input');
      const authorizationError = new AuthorizationError('Insufficient permissions');
      const authenticationError = new AuthenticationError('Invalid credentials');

      expect(notFoundError).toBeInstanceOf(AppError);
      expect(notFoundError).toBeInstanceOf(Error);

      expect(validationError).toBeInstanceOf(AppError);
      expect(validationError).toBeInstanceOf(Error);

      expect(authorizationError).toBeInstanceOf(AppError);
      expect(authorizationError).toBeInstanceOf(Error);

      expect(authenticationError).toBeInstanceOf(AppError);
      expect(authenticationError).toBeInstanceOf(Error);
    });
  });

  describe('error stack traces', () => {
    it('should capture stack traces', () => {
      const error = new AppError('TEST_ERROR', 'Test error message');
      expect(error.stack).toBeDefined();
      expect(error.stack).toContain('TEST_ERROR');
    });

    it('should preserve stack traces in derived errors', () => {
      const notFoundError = new NotFoundError('User', 123);
      const validationError = new ValidationError('Invalid input');
      const authorizationError = new AuthorizationError('Insufficient permissions');
      const authenticationError = new AuthenticationError('Invalid credentials');

      expect(notFoundError.stack).toBeDefined();
      expect(validationError.stack).toBeDefined();
      expect(authorizationError.stack).toBeDefined();
      expect(authenticationError.stack).toBeDefined();
    });
  });
}); 