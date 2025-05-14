import { BaseService, BaseEntity, ServiceResponse } from '../../../src/services/base.service';
import { httpClient } from '../../../src/utils/http';
import { CacheService } from '../../../src/utils/cache';
import { AppError } from '../../../src/utils/errors';
import { HTTP_STATUS, ERROR_CODES, ERROR_MESSAGES } from '../../../src/constants';

// Mock axios and cache
jest.mock('../../../src/utils/http');
jest.mock('../../../src/utils/cache', () => {
  return {
    CacheService: jest.fn().mockImplementation(() => ({
      get: jest.fn(),
      set: jest.fn(),
      delete: jest.fn(),
      clear: jest.fn(),
    })),
  };
});

// Test entity interface
interface TestEntity extends BaseEntity {
  name: string;
  value: number;
}

// Test service class
class TestService extends BaseService<TestEntity> {
  constructor() {
    super('/test');
  }
}

describe('BaseService', () => {
  let service: TestService;
  let mockHttpClient: jest.Mocked<typeof httpClient>;
  let mockCache: jest.Mocked<CacheService>;

  beforeEach(() => {
    jest.clearAllMocks();
    mockHttpClient = httpClient as jest.Mocked<typeof httpClient>;
    service = new TestService();
    mockCache = (service as any).cache;
  });

  describe('list', () => {
    const mockResponse: ServiceResponse<TestEntity[]> = {
      data: [
        { id: '1', name: 'Test 1', value: 100 },
        { id: '2', name: 'Test 2', value: 200 },
      ],
      meta: {
        page: 1,
        limit: 10,
        total: 2,
      },
    };

    it('should return cached data if available', async () => {
      mockCache.get.mockResolvedValueOnce(mockResponse);
      const result = await service.list();
      expect(result).toEqual(mockResponse);
      expect(mockHttpClient.get).not.toHaveBeenCalled();
    });

    it('should fetch and cache data if not in cache', async () => {
      mockCache.get.mockResolvedValueOnce(null);
      mockHttpClient.get.mockResolvedValueOnce({ data: mockResponse });

      const result = await service.list();

      expect(result).toEqual(mockResponse);
      expect(mockHttpClient.get).toHaveBeenCalledWith('/test', { params: undefined });
      expect(mockCache.set).toHaveBeenCalled();
    });

    it('should handle query parameters correctly', async () => {
      const params = { page: 1, limit: 10, sort: 'name' };
      mockCache.get.mockResolvedValueOnce(null);
      mockHttpClient.get.mockResolvedValueOnce({ data: mockResponse });

      await service.list(params);

      expect(mockHttpClient.get).toHaveBeenCalledWith('/test', { params });
    });
  });

  describe('get', () => {
    const mockEntity: TestEntity = {
      id: '1',
      name: 'Test',
      value: 100,
    };

    it('should return cached entity if available', async () => {
      mockCache.get.mockResolvedValueOnce(mockEntity);
      const result = await service.get('1');
      expect(result).toEqual(mockEntity);
      expect(mockHttpClient.get).not.toHaveBeenCalled();
    });

    it('should fetch and cache entity if not in cache', async () => {
      mockCache.get.mockResolvedValueOnce(null);
      mockHttpClient.get.mockResolvedValueOnce({ data: mockEntity });

      const result = await service.get('1');

      expect(result).toEqual(mockEntity);
      expect(mockHttpClient.get).toHaveBeenCalledWith('/test/1');
      expect(mockCache.set).toHaveBeenCalled();
    });
  });

  describe('create', () => {
    const newEntity: Partial<TestEntity> = {
      name: 'New Test',
      value: 300,
    };

    const createdEntity: TestEntity = {
      id: '3',
      name: newEntity.name!,
      value: newEntity.value!,
    };

    it('should create entity and invalidate list cache', async () => {
      mockHttpClient.post.mockResolvedValueOnce({ data: createdEntity });

      const result = await service.create(newEntity);

      expect(result).toEqual(createdEntity);
      expect(mockHttpClient.post).toHaveBeenCalledWith('/test', newEntity);
      expect(mockCache.delete).toHaveBeenCalled();
    });
  });

  describe('update', () => {
    const updatedEntity: Partial<TestEntity> = {
      name: 'Updated Test',
      value: 400,
    };

    const savedEntity: TestEntity = {
      id: '1',
      name: updatedEntity.name!,
      value: updatedEntity.value!,
    };

    it('should update entity and invalidate caches', async () => {
      mockHttpClient.put.mockResolvedValueOnce({ data: savedEntity });

      const result = await service.update('1', updatedEntity);

      expect(result).toEqual(savedEntity);
      expect(mockHttpClient.put).toHaveBeenCalledWith('/test/1', updatedEntity);
      expect(mockCache.delete).toHaveBeenCalledTimes(2);
    });
  });

  describe('delete', () => {
    it('should delete entity and invalidate caches', async () => {
      mockHttpClient.delete.mockResolvedValueOnce({});

      await service.delete('1');

      expect(mockHttpClient.delete).toHaveBeenCalledWith('/test/1');
      expect(mockCache.delete).toHaveBeenCalledTimes(2);
    });
  });

  describe('error handling', () => {
    it('should handle not found error', async () => {
      const error = {
        response: {
          status: HTTP_STATUS.NOT_FOUND,
          data: { message: 'Resource not found' },
        },
      };

      mockHttpClient.get.mockRejectedValueOnce(error);

      await expect(service.get('999')).rejects.toThrow(AppError);
      await expect(service.get('999')).rejects.toMatchObject({
        message: 'Resource not found',
        status: HTTP_STATUS.NOT_FOUND,
        isOperational: true,
      });
    });

    it('should handle validation error', async () => {
      const error = {
        response: {
          status: HTTP_STATUS.BAD_REQUEST,
          data: { message: 'Invalid input' },
        },
      };

      mockHttpClient.post.mockRejectedValueOnce(error);

      await expect(service.create({})).rejects.toThrow(AppError);
      await expect(service.create({})).rejects.toMatchObject({
        message: 'Invalid input',
        status: HTTP_STATUS.BAD_REQUEST,
        isOperational: true,
      });
    });

    it('should handle unauthorized error', async () => {
      const error = {
        response: {
          status: HTTP_STATUS.UNAUTHORIZED,
          data: { message: 'Invalid credentials' },
        },
      };

      mockHttpClient.get.mockRejectedValueOnce(error);

      await expect(service.list()).rejects.toThrow(AppError);
      await expect(service.list()).rejects.toMatchObject({
        message: 'Invalid credentials',
        status: HTTP_STATUS.UNAUTHORIZED,
        isOperational: true,
      });
    });

    it('should handle forbidden error', async () => {
      const error = {
        response: {
          status: HTTP_STATUS.FORBIDDEN,
          data: { message: 'Access denied' },
        },
      };

      mockHttpClient.get.mockRejectedValueOnce(error);

      await expect(service.list()).rejects.toThrow(AppError);
      await expect(service.list()).rejects.toMatchObject({
        message: 'Access denied',
        status: HTTP_STATUS.FORBIDDEN,
        isOperational: true,
      });
    });

    it('should handle internal server error', async () => {
      const error = {
        response: {
          status: HTTP_STATUS.INTERNAL_SERVER_ERROR,
          data: { message: 'Internal server error' },
        },
      };

      mockHttpClient.get.mockRejectedValueOnce(error);

      await expect(service.list()).rejects.toThrow(AppError);
      await expect(service.list()).rejects.toMatchObject({
        message: 'Internal server error',
        status: HTTP_STATUS.INTERNAL_SERVER_ERROR,
        isOperational: false,
      });
    });
  });
}); 