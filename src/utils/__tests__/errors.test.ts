import {
  AppError,
  NotFoundError,
  ValidationError,
  UnauthorizedError,
  ForbiddenError,
  ConflictError,
  InternalServerError,
  FormattedValidationError
} from '../errors';

describe('Error Classes', () => {
  describe('AppError', () => {
    it('should create an AppError with default operational status', () => {
      const error = new AppError('Test error', 400);
      expect(error).toBeInstanceOf(Error);
      expect(error).toBeInstanceOf(AppError);
      expect(error.message).toBe('Test error');
      expect(error.statusCode).toBe(400);
      expect(error.isOperational).toBe(true);
      expect(error.stack).toBeDefined();
    });

    it('should create an AppError with custom operational status', () => {
      const error = new AppError('Test error', 500, false);
      expect(error.isOperational).toBe(false);
    });
  });

  describe('NotFoundError', () => {
    it('should create a NotFoundError with default message', () => {
      const error = new NotFoundError();
      expect(error).toBeInstanceOf(AppError);
      expect(error.message).toBe('Resource not found');
      expect(error.statusCode).toBe(404);
      expect(error.isOperational).toBe(true);
    });

    it('should create a NotFoundError with custom message', () => {
      const error = new NotFoundError('Custom not found message');
      expect(error.message).toBe('Custom not found message');
      expect(error.statusCode).toBe(404);
    });
  });

  describe('ValidationError', () => {
    it('should create a ValidationError with default values', () => {
      const error = new ValidationError();
      expect(error).toBeInstanceOf(AppError);
      expect(error.message).toBe('Validation failed');
      expect(error.statusCode).toBe(400);
      expect(error.errors).toEqual([]);
    });

    it('should create a ValidationError with custom message and errors', () => {
      const validationErrors: FormattedValidationError[] = [
        { path: 'email', message: 'Invalid email format' },
        { path: 'password', message: 'Password too short' }
      ];
      const error = new ValidationError('Custom validation error', validationErrors);
      expect(error.message).toBe('Custom validation error');
      expect(error.statusCode).toBe(400);
      expect(error.errors).toEqual(validationErrors);
    });
  });

  describe('UnauthorizedError', () => {
    it('should create an UnauthorizedError with default message', () => {
      const error = new UnauthorizedError();
      expect(error).toBeInstanceOf(AppError);
      expect(error.message).toBe('Unauthorized');
      expect(error.statusCode).toBe(401);
      expect(error.isOperational).toBe(true);
    });

    it('should create an UnauthorizedError with custom message', () => {
      const error = new UnauthorizedError('Custom unauthorized message');
      expect(error.message).toBe('Custom unauthorized message');
      expect(error.statusCode).toBe(401);
    });
  });

  describe('ForbiddenError', () => {
    it('should create a ForbiddenError with default message', () => {
      const error = new ForbiddenError();
      expect(error).toBeInstanceOf(AppError);
      expect(error.message).toBe('Forbidden');
      expect(error.statusCode).toBe(403);
      expect(error.isOperational).toBe(true);
    });

    it('should create a ForbiddenError with custom message', () => {
      const error = new ForbiddenError('Custom forbidden message');
      expect(error.message).toBe('Custom forbidden message');
      expect(error.statusCode).toBe(403);
    });
  });

  describe('ConflictError', () => {
    it('should create a ConflictError with default message', () => {
      const error = new ConflictError();
      expect(error).toBeInstanceOf(AppError);
      expect(error.message).toBe('Resource conflict');
      expect(error.statusCode).toBe(409);
      expect(error.isOperational).toBe(true);
    });

    it('should create a ConflictError with custom message', () => {
      const error = new ConflictError('Custom conflict message');
      expect(error.message).toBe('Custom conflict message');
      expect(error.statusCode).toBe(409);
    });
  });

  describe('InternalServerError', () => {
    it('should create an InternalServerError with default message', () => {
      const error = new InternalServerError();
      expect(error).toBeInstanceOf(AppError);
      expect(error.message).toBe('Internal server error');
      expect(error.statusCode).toBe(500);
      expect(error.isOperational).toBe(false);
    });

    it('should create an InternalServerError with custom message', () => {
      const error = new InternalServerError('Custom server error');
      expect(error.message).toBe('Custom server error');
      expect(error.statusCode).toBe(500);
      expect(error.isOperational).toBe(false);
    });
  });

  describe('Error inheritance', () => {
    it('should maintain proper instanceof relationships', () => {
      const errors = [
        new NotFoundError(),
        new ValidationError(),
        new UnauthorizedError(),
        new ForbiddenError(),
        new ConflictError(),
        new InternalServerError()
      ];

      errors.forEach(error => {
        expect(error).toBeInstanceOf(Error);
        expect(error).toBeInstanceOf(AppError);
      });
    });

    it('should capture stack traces', () => {
      const errors = [
        new NotFoundError(),
        new ValidationError(),
        new UnauthorizedError(),
        new ForbiddenError(),
        new ConflictError(),
        new InternalServerError()
      ];

      errors.forEach(error => {
        expect(error.stack).toBeDefined();
        expect(error.stack).toContain('Error');
      });
    });
  });
}); 