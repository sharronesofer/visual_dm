from typing import Any



describe('Error Handling Middleware', () => {
  let mockRequest: Partial<Request>
  let mockResponse: Partial<Response>
  let nextFunction: NextFunction
  beforeEach(() => {
    mockRequest = {
      originalUrl: '/test-url'
    }
    mockResponse = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    }
    nextFunction = jest.fn()
  })
  describe('notFoundHandler', () => {
    it('should create a 404 error and pass it to next', () => {
      notFoundHandler(
        mockRequest as Request,
        mockResponse as Response,
        nextFunction
      )
      expect(nextFunction).toHaveBeenCalledWith(
        expect.objectContaining({
          message: 'Route not found: /test-url',
          statusCode: 404
        })
      )
    })
  })
  describe('errorHandler', () => {
    beforeEach(() => {
      process.env.NODE_ENV = 'production'
    })
    it('should handle operational errors with correct status code', () => {
      const validationError = new ValidationError('Invalid input data')
      errorHandler(
        validationError,
        mockRequest as Request,
        mockResponse as Response,
        nextFunction
      )
      expect(mockResponse.status).toHaveBeenCalledWith(400)
      expect(mockResponse.json).toHaveBeenCalledWith({
        status: 'error',
        message: 'Invalid input data'
      })
    })
    it('should handle non-operational errors with 500 status code', () => {
      const error = new Error('Some unexpected error')
      errorHandler(
        error,
        mockRequest as Request,
        mockResponse as Response,
        nextFunction
      )
      expect(mockResponse.status).toHaveBeenCalledWith(500)
      expect(mockResponse.json).toHaveBeenCalledWith({
        status: 'error',
        message: 'An unexpected error occurred'
      })
    })
    it('should include stack trace in development environment', () => {
      process.env.NODE_ENV = 'development'
      const error = new Error('Test error')
      error.stack = 'Test stack trace'
      errorHandler(
        error,
        mockRequest as Request,
        mockResponse as Response,
        nextFunction
      )
      expect(mockResponse.json).toHaveBeenCalledWith({
        status: 'error',
        message: 'An unexpected error occurred',
        stack: 'Test stack trace'
      })
    })
    it('should handle NotFoundError with 404 status code', () => {
      const notFoundError = new NotFoundError('Resource not found')
      errorHandler(
        notFoundError,
        mockRequest as Request,
        mockResponse as Response,
        nextFunction
      )
      expect(mockResponse.status).toHaveBeenCalledWith(404)
      expect(mockResponse.json).toHaveBeenCalledWith({
        status: 'error',
        message: 'Resource not found'
      })
    })
  })
}) 