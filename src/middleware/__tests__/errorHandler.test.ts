import { Request, Response, NextFunction } from 'express';
import {
  AppError,
  ValidationError,
  NotFoundError
} from '../../errors';
import {
  notFoundHandler,
  errorHandler,
  asyncErrorBoundary,
  validateRequest
} from '../errorHandler';
import { logger } from '../../utils/logger';

// Mock logger
jest.mock('../../utils/logger', () => ({
  logger: {
    error: jest.fn(),
    warn: jest.fn()
  }
}));

describe('Error Handling Middleware', () => {
  let mockRequest: Partial<Request>;
  let mockResponse: Partial<Response>;
  let nextFunction: jest.Mock;

  beforeEach(() => {
    mockRequest = {
      originalUrl: '/test-url',
      path: '/test-url',
      method: 'GET',
      query: {},
      body: {},
      user: undefined
    };
    mockResponse = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };
    nextFunction = jest.fn();

    // Clear logger mocks
    jest.clearAllMocks();
  });

  describe('notFoundHandler', () => {
    it('should create a 404 error and pass it to next', () => {
      notFoundHandler(
        mockRequest as Request,
        mockResponse as Response,
        nextFunction
      );

      expect(nextFunction).toHaveBeenCalledWith(
        expect.objectContaining({
          message: 'Route not found: /test-url',
          statusCode: 404,
          code: 'NOT_FOUND'
        })
      );
    });
  });

  describe('errorHandler', () => {
    beforeEach(() => {
      process.env.NODE_ENV = 'production';
    });

    it('should handle operational errors with correct status code', () => {
      const validationError = new ValidationError('Invalid input data', {
        email: ['Invalid email format']
      });

      errorHandler(
        validationError,
        mockRequest as Request,
        mockResponse as Response,
        nextFunction
      );

      expect(mockResponse.status).toHaveBeenCalledWith(400);
      expect(mockResponse.json).toHaveBeenCalledWith({
        status: 'error',
        code: 'VALIDATION_ERROR',
        message: 'Invalid input data',
        statusCode: 400,
        details: {
          email: ['Invalid email format']
        }
      });
      expect(logger.warn).toHaveBeenCalled();
      expect(logger.error).not.toHaveBeenCalled();
    });

    it('should handle non-operational errors with 500 status code', () => {
      const error = new Error('Some unexpected error');

      errorHandler(
        error,
        mockRequest as Request,
        mockResponse as Response,
        nextFunction
      );

      expect(mockResponse.status).toHaveBeenCalledWith(500);
      expect(mockResponse.json).toHaveBeenCalledWith({
        status: 'error',
        code: 'INTERNAL_ERROR',
        message: 'Some unexpected error',
        statusCode: 500,
        details: {
          name: 'Error',
          stack: error.stack
        }
      });
      expect(logger.error).toHaveBeenCalled();
      expect(logger.warn).not.toHaveBeenCalled();
    });

    it('should include stack trace in development environment', () => {
      process.env.NODE_ENV = 'development';
      const error = new Error('Test error');
      error.stack = 'Test stack trace';

      errorHandler(
        error,
        mockRequest as Request,
        mockResponse as Response,
        nextFunction
      );

      expect(mockResponse.json).toHaveBeenCalledWith(
        expect.objectContaining({
          details: expect.objectContaining({
            stack: 'Test stack trace'
          })
        })
      );
    });

    it('should handle errors without stack trace', () => {
      const error = new Error('Test error');
      error.stack = undefined;

      errorHandler(
        error,
        mockRequest as Request,
        mockResponse as Response,
        nextFunction
      );

      expect(mockResponse.json).toHaveBeenCalledWith({
        status: 'error',
        code: 'INTERNAL_ERROR',
        message: 'Test error',
        statusCode: 500,
        details: {
          name: 'Error',
          stack: undefined
        }
      });
    });
  });

  describe('asyncErrorBoundary', () => {
    it('should pass through successful handler execution', async () => {
      const handler = jest.fn().mockResolvedValue('success');
      const boundHandler = asyncErrorBoundary(handler);

      await boundHandler(
        mockRequest as Request,
        mockResponse as Response,
        nextFunction
      );

      expect(handler).toHaveBeenCalled();
      expect(nextFunction).not.toHaveBeenCalled();
    });

    it('should catch errors and pass them to next', async () => {
      const error = new Error('Test error');
      const handler = jest.fn().mockRejectedValue(error);
      const boundHandler = asyncErrorBoundary(handler);

      await boundHandler(
        mockRequest as Request,
        mockResponse as Response,
        nextFunction
      );

      expect(handler).toHaveBeenCalled();
      expect(nextFunction).toHaveBeenCalledWith(error);
    });
  });

  describe('validateRequest', () => {
    const mockSchema = {
      validate: jest.fn()
    };

    it('should pass validation if schema validates', () => {
      mockSchema.validate.mockReturnValue({ error: null });
      const middleware = validateRequest(mockSchema);

      middleware(mockRequest as Request, mockResponse as Response, nextFunction);

      expect(nextFunction).toHaveBeenCalledWith();
      expect(nextFunction).not.toHaveBeenCalledWith(expect.any(Error));
    });

    it('should handle validation errors', () => {
      const validationError = {
        details: [
          { path: ['email'], message: 'Invalid email' },
          { path: ['password'], message: 'Password too short' }
        ]
      };
      mockSchema.validate.mockReturnValue({ error: validationError });
      const middleware = validateRequest(mockSchema);

      middleware(mockRequest as Request, mockResponse as Response, nextFunction);

      expect(nextFunction).toHaveBeenCalledWith(
        expect.objectContaining({
          code: 'VALIDATION_ERROR',
          statusCode: 400,
          details: {
            email: ['Invalid email'],
            password: ['Password too short']
          }
        })
      );
    });

    it('should handle schema validation errors', () => {
      const error = new Error('Schema validation failed');
      mockSchema.validate.mockImplementation(() => {
        throw error;
      });
      const middleware = validateRequest(mockSchema);

      middleware(mockRequest as Request, mockResponse as Response, nextFunction);

      expect(nextFunction).toHaveBeenCalledWith(error);
    });
  });
}); 