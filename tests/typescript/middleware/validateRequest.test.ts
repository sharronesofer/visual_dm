import { Request, Response, NextFunction } from 'express';
import { z } from 'zod';
import { validateRequest } from '../../../src/middleware/validateRequest';
import { ValidationError } from '../../../src/utils/errors';

describe('validateRequest Middleware', () => {
  let mockRequest: Partial<Request>;
  let mockResponse: Partial<Response>;
  let nextFunction: NextFunction;

  beforeEach(() => {
    mockRequest = {
      body: {},
      query: {},
      params: {}
    };
    mockResponse = {};
    nextFunction = jest.fn();
  });

  describe('Body Validation', () => {
    const schema = z.object({
      body: z.object({
        email: z.string().email(),
        password: z.string().min(6)
      })
    });

    it('should pass validation with valid data', async () => {
      mockRequest.body = {
        email: 'test@example.com',
        password: 'password123'
      };

      const middleware = validateRequest(schema);
      await middleware(
        mockRequest as Request,
        mockResponse as Response,
        nextFunction
      );

      expect(nextFunction).toHaveBeenCalledWith();
      expect(mockRequest.body).toEqual({
        email: 'test@example.com',
        password: 'password123'
      });
    });

    it('should fail validation with invalid email', async () => {
      mockRequest.body = {
        email: 'invalid-email',
        password: 'password123'
      };

      const middleware = validateRequest(schema);
      await middleware(
        mockRequest as Request,
        mockResponse as Response,
        nextFunction
      );

      expect(nextFunction).toHaveBeenCalledWith(
        expect.objectContaining({
          message: 'Validation failed',
          errors: expect.arrayContaining([
            expect.objectContaining({
              path: 'body.email',
              message: expect.stringContaining('Invalid email')
            })
          ])
        })
      );
    });

    it('should fail validation with short password', async () => {
      mockRequest.body = {
        email: 'test@example.com',
        password: '12345'
      };

      const middleware = validateRequest(schema);
      await middleware(
        mockRequest as Request,
        mockResponse as Response,
        nextFunction
      );

      expect(nextFunction).toHaveBeenCalledWith(
        expect.objectContaining({
          message: 'Validation failed',
          errors: expect.arrayContaining([
            expect.objectContaining({
              path: 'body.password',
              message: expect.stringContaining('too short')
            })
          ])
        })
      );
    });
  });

  describe('Query Validation', () => {
    const schema = z.object({
      query: z.object({
        page: z.string().regex(/^\d+$/).transform(Number),
        limit: z.string().regex(/^\d+$/).transform(Number)
      })
    });

    it('should pass validation with valid query parameters', async () => {
      mockRequest.query = {
        page: '1',
        limit: '10'
      };

      const middleware = validateRequest(schema, { query: true });
      await middleware(
        mockRequest as Request,
        mockResponse as Response,
        nextFunction
      );

      expect(nextFunction).toHaveBeenCalledWith();
      expect(mockRequest.query).toEqual({
        page: 1,
        limit: 10
      });
    });

    it('should fail validation with invalid query parameters', async () => {
      mockRequest.query = {
        page: 'invalid',
        limit: '10'
      };

      const middleware = validateRequest(schema, { query: true });
      await middleware(
        mockRequest as Request,
        mockResponse as Response,
        nextFunction
      );

      expect(nextFunction).toHaveBeenCalledWith(
        expect.objectContaining({
          message: 'Validation failed',
          errors: expect.arrayContaining([
            expect.objectContaining({
              path: 'query.page',
              message: expect.any(String)
            })
          ])
        })
      );
    });
  });

  describe('Multiple Target Validation', () => {
    const schema = z.object({
      params: z.object({
        id: z.string().uuid()
      }),
      body: z.object({
        name: z.string().min(1)
      })
    });

    it('should validate multiple targets successfully', async () => {
      mockRequest.params = {
        id: '123e4567-e89b-12d3-a456-426614174000'
      };
      mockRequest.body = {
        name: 'Test Name'
      };

      const middleware = validateRequest(schema, { params: true, body: true });
      await middleware(
        mockRequest as Request,
        mockResponse as Response,
        nextFunction
      );

      expect(nextFunction).toHaveBeenCalledWith();
    });

    it('should fail if any target is invalid', async () => {
      mockRequest.params = {
        id: 'invalid-uuid'
      };
      mockRequest.body = {
        name: 'Test Name'
      };

      const middleware = validateRequest(schema, { params: true, body: true });
      await middleware(
        mockRequest as Request,
        mockResponse as Response,
        nextFunction
      );

      expect(nextFunction).toHaveBeenCalledWith(
        expect.objectContaining({
          message: 'Validation failed',
          errors: expect.arrayContaining([
            expect.objectContaining({
              path: 'params.id',
              message: expect.stringContaining('Invalid uuid')
            })
          ])
        })
      );
    });
  });
}); 