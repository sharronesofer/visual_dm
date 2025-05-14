const swaggerConfig = {
  openapi: '3.0.0',
  info: {
    title: 'Visual DM API Documentation',
    version: '1.0.0',
    description: 'API documentation for Visual DM application',
    license: {
      name: 'MIT',
      url: 'https://opensource.org/licenses/MIT',
    },
  },
  servers: [
    {
      url: 'http://localhost:3002',
      description: 'Development server',
    },
  ],
  basePath: '/api',
  components: {
    securitySchemes: {
      bearerAuth: {
        type: 'http',
        scheme: 'bearer',
        bearerFormat: 'JWT',
      },
    },
    schemas: {
      Error: {
        type: 'object',
        properties: {
          code: {
            type: 'string',
            description: 'Error code',
          },
          message: {
            type: 'string',
            description: 'Error message',
          },
        },
        required: ['code', 'message'],
      },
      SuccessResponse: {
        type: 'object',
        properties: {
          success: {
            type: 'boolean',
            description: 'Indicates if the operation was successful',
            example: true,
          },
          data: {
            type: 'object',
            description: 'Response data',
          },
        },
        required: ['success'],
      },
    },
    responses: {
      UnauthorizedError: {
        description: 'Authentication information is missing or invalid',
        content: {
          'application/json': {
            schema: {
              $ref: '#/components/schemas/Error',
            },
            example: {
              code: 'UNAUTHORIZED',
              message: 'Invalid or missing authentication token',
            },
          },
        },
      },
      NotFoundError: {
        description: 'The requested resource was not found',
        content: {
          'application/json': {
            schema: {
              $ref: '#/components/schemas/Error',
            },
            example: {
              code: 'NOT_FOUND',
              message: 'Resource not found',
            },
          },
        },
      },
    },
  },
  security: [
    {
      bearerAuth: [],
    },
  ],
  tags: [
    {
      name: 'auth',
      description: 'Authentication endpoints',
    },
    {
      name: 'users',
      description: 'User management endpoints',
    },
    {
      name: 'campaigns',
      description: 'Campaign management endpoints',
    },
  ],
};

module.exports = swaggerConfig; 