import axios from 'axios';
import { createHttpClient, http, httpClient } from '../http';
import { ApiError, NetworkError } from '../types/errors';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('HTTP Utilities', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  describe('createHttpClient', () => {
    it('should create axios instance with default config', () => {
      const instance = createHttpClient();
      expect(mockedAxios.create).toHaveBeenCalledWith({
        baseURL: 'http://localhost:3000/api',
        timeout: 10000,
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
      });
      expect(instance).toBeDefined();
    });

    it('should override default config with provided config', () => {
      const customConfig = {
        baseURL: 'https://api.example.com',
        timeout: 5000,
      };
      const instance = createHttpClient(customConfig);
      expect(mockedAxios.create).toHaveBeenCalledWith({
        baseURL: 'https://api.example.com',
        timeout: 5000,
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
      });
      expect(instance).toBeDefined();
    });

    it('should accept custom retry configuration', () => {
      const retryConfig = {
        maxRetries: 5,
        retryDelay: 2000,
        retryableStatuses: [500, 503],
      };
      createHttpClient({}, retryConfig);
      expect(mockedAxios.create).toHaveBeenCalled();
    });
  });

  describe('request interceptor', () => {
    let instance: ReturnType<typeof createHttpClient>;
    let requestInterceptor: any;

    beforeEach(() => {
      instance = createHttpClient();
      requestInterceptor = instance.interceptors.request.use.mock.calls[0][0];
    });

    it('should initialize retry count', () => {
      const config = {
        headers: {},
      };

      const result = requestInterceptor(config);
      expect(result.retryCount).toBe(0);
    });

    it('should add auth token to headers if available', () => {
      const token = 'test-token';
      localStorage.setItem('authToken', token);

      const config = {
        headers: {},
      };

      const result = requestInterceptor(config);
      expect(result.headers.Authorization).toBe(`Bearer ${token}`);
    });

    it('should add request timestamp to headers', () => {
      const config = {
        headers: {},
      };

      const result = requestInterceptor(config);
      expect(result.headers['X-Request-Time']).toBeDefined();
      expect(
        new Date(result.headers['X-Request-Time']).getTime()
      ).toBeLessThanOrEqual(Date.now());
    });
  });

  describe('response interceptor', () => {
    let instance: ReturnType<typeof createHttpClient>;
    let responseInterceptor: any;
    let errorHandler: any;

    beforeEach(() => {
      instance = createHttpClient();
      responseInterceptor = instance.interceptors.response.use.mock.calls[0][0];
      errorHandler = instance.interceptors.response.use.mock.calls[0][1];
    });

    it('should add metadata to successful responses', () => {
      const response = {
        data: { message: 'Success' },
        status: 200,
      };

      const result = responseInterceptor(response);
      expect(result.data._metadata).toBeDefined();
      expect(result.data._metadata.statusCode).toBe(200);
      expect(result.data._metadata.timestamp).toBeDefined();
    });

    describe('retry logic', () => {
      it('should retry on retryable status codes', async () => {
        const error = {
          config: {
            retryCount: 0,
            headers: {},
          },
          response: {
            status: 503,
            data: { message: 'Service Unavailable' },
          },
        };

        const mockRequest = jest
          .fn()
          .mockResolvedValueOnce({ data: 'success' });
        instance.request = mockRequest;

        await expect(errorHandler(error)).resolves.toEqual({ data: 'success' });
        expect(mockRequest).toHaveBeenCalledWith(
          expect.objectContaining({
            retryCount: 1,
          })
        );
      });

      it('should use exponential backoff for retries', async () => {
        const error = {
          config: {
            retryCount: 0,
            headers: {},
          },
          response: {
            status: 503,
            data: { message: 'Service Unavailable' },
          },
        };

        const mockRequest = jest
          .fn()
          .mockResolvedValueOnce({ data: 'success' });
        instance.request = mockRequest;

        const promise = errorHandler(error);
        jest.advanceTimersByTime(1000); // First retry delay
        await promise;

        expect(mockRequest).toHaveBeenCalled();
      });

      it('should stop retrying after max retries', async () => {
        const error = {
          config: {
            retryCount: 3, // Already at max retries
            headers: {},
          },
          response: {
            status: 503,
            data: { message: 'Service Unavailable' },
          },
        };

        await expect(errorHandler(error)).rejects.toThrow(ApiError);
      });

      it('should not retry on non-retryable status codes', async () => {
        const error = {
          config: {
            retryCount: 0,
            headers: {},
          },
          response: {
            status: 400,
            data: { message: 'Bad Request' },
          },
        };

        await expect(errorHandler(error)).rejects.toThrow(ApiError);
      });
    });

    describe('error handling', () => {
      it('should throw ApiError for server errors', async () => {
        const error = {
          response: {
            status: 500,
            data: { message: 'Server Error' },
          },
        };

        await expect(errorHandler(error)).rejects.toThrow(ApiError);
      });

      it('should throw NetworkError for request errors', async () => {
        const error = {
          request: {},
        };

        await expect(errorHandler(error)).rejects.toThrow(NetworkError);
      });

      it('should throw NetworkError for configuration errors', async () => {
        const error = new Error('Config error');

        await expect(errorHandler(error)).rejects.toThrow(NetworkError);
      });
    });
  });

  describe('httpClient', () => {
    const mockResponse = { data: { message: 'Success' } };

    beforeEach(() => {
      mockedAxios.create.mockReturnValue({
        get: jest.fn().mockResolvedValue(mockResponse),
        post: jest.fn().mockResolvedValue(mockResponse),
        put: jest.fn().mockResolvedValue(mockResponse),
        patch: jest.fn().mockResolvedValue(mockResponse),
        delete: jest.fn().mockResolvedValue(mockResponse),
        head: jest.fn().mockResolvedValue(mockResponse),
        options: jest.fn().mockResolvedValue(mockResponse),
      } as any);
    });

    it('should make GET request', async () => {
      const result = await httpClient.get('/test');
      expect(result).toEqual(mockResponse.data);
    });

    it('should make POST request', async () => {
      const data = { test: true };
      const result = await httpClient.post('/test', data);
      expect(result).toEqual(mockResponse.data);
    });

    it('should make PUT request', async () => {
      const data = { test: true };
      const result = await httpClient.put('/test', data);
      expect(result).toEqual(mockResponse.data);
    });

    it('should make PATCH request', async () => {
      const data = { test: true };
      const result = await httpClient.patch('/test', data);
      expect(result).toEqual(mockResponse.data);
    });

    it('should make DELETE request', async () => {
      const result = await httpClient.delete('/test');
      expect(result).toEqual(mockResponse.data);
    });

    it('should make HEAD request', async () => {
      const result = await httpClient.head('/test');
      expect(result).toEqual(mockResponse.data);
    });

    it('should make OPTIONS request', async () => {
      const result = await httpClient.options('/test');
      expect(result).toEqual(mockResponse.data);
    });

    it('should handle request config', async () => {
      const config = { params: { page: 1 } };
      await httpClient.get('/test', config);
      const instance = mockedAxios.create.mock.results[0].value;
      expect(instance.get).toHaveBeenCalledWith('/test', config);
    });
  });

  describe('default http instance', () => {
    it('should export default http instance', () => {
      expect(http).toBeDefined();
      expect(mockedAxios.create).toHaveBeenCalled();
    });
  });
});
