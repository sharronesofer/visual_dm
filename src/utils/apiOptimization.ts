import { AxiosRequestConfig } from 'axios';
import { apiClient } from '../api/client';
import { Logger } from './logger';

const logger = new Logger({ prefix: 'ApiOptimization' });

// Cache configuration
interface CacheConfig {
  ttl: number; // Time to live in milliseconds
  maxSize: number; // Maximum number of items in cache
}

interface CacheEntry<T> {
  data: T;
  timestamp: number;
}

// Request batching configuration
interface BatchConfig {
  maxBatchSize: number; // Maximum number of requests to batch
  maxWaitTime: number; // Maximum time to wait before processing batch (ms)
}

// Cache implementation
class ApiCache {
  private cache: Map<string, CacheEntry<unknown>>;
  private config: CacheConfig;

  constructor(config: CacheConfig = { ttl: 5 * 60 * 1000, maxSize: 100 }) {
    this.cache = new Map();
    this.config = config;
  }

  public get<T>(key: string): T | null {
    const entry = this.cache.get(key) as CacheEntry<T> | undefined;
    
    if (!entry) return null;
    
    const isExpired = Date.now() - entry.timestamp > this.config.ttl;
    if (isExpired) {
      this.cache.delete(key);
      return null;
    }
    
    return entry.data;
  }

  public set<T>(key: string, data: T): void {
    if (this.cache.size >= this.config.maxSize) {
      // Remove oldest entry
      const oldestKey = this.cache.keys().next().value;
      this.cache.delete(oldestKey);
    }
    
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
    });
  }

  public clear(): void {
    this.cache.clear();
  }

  public invalidate(pattern: RegExp): void {
    for (const key of this.cache.keys()) {
      if (pattern.test(key)) {
        this.cache.delete(key);
      }
    }
  }
}

// Request batching implementation
class RequestBatcher {
  private batch: Map<string, Array<{
    resolve: (value: unknown) => void;
    reject: (error: unknown) => void;
    data?: unknown;
  }>> = new Map();
  
  private timeouts: Map<string, NodeJS.Timeout> = new Map();
  private config: BatchConfig;

  constructor(config: BatchConfig = { maxBatchSize: 10, maxWaitTime: 50 }) {
    this.config = config;
  }

  public async add<T>(
    endpoint: string,
    method: string,
    data?: unknown
  ): Promise<T> {
    const batchKey = `${method}:${endpoint}`;
    
    return new Promise((resolve, reject) => {
      if (!this.batch.has(batchKey)) {
        this.batch.set(batchKey, []);
        this.scheduleBatch(batchKey);
      }
      
      const requests = this.batch.get(batchKey)!;
      requests.push({ resolve, reject, data });
      
      if (requests.length >= this.config.maxBatchSize) {
        this.processBatch(batchKey);
      }
    });
  }

  private scheduleBatch(batchKey: string): void {
    const timeout = setTimeout(() => {
      this.processBatch(batchKey);
    }, this.config.maxWaitTime);
    
    this.timeouts.set(batchKey, timeout);
  }

  private async processBatch(batchKey: string): Promise<void> {
    const timeout = this.timeouts.get(batchKey);
    if (timeout) {
      clearTimeout(timeout);
      this.timeouts.delete(batchKey);
    }

    const requests = this.batch.get(batchKey) || [];
    this.batch.delete(batchKey);

    if (requests.length === 0) return;

    const [method, endpoint] = batchKey.split(':');
    
    try {
      // If it's a GET request, we can use URL parameters for batching
      if (method === 'GET') {
        const ids = requests.map((_, index) => `id${index}`).join(',');
        const response = await apiClient.get(
          `${endpoint}?ids=${ids}`,
          { headers: { 'X-Batch-Request': 'true' } }
        );
        requests.forEach(({ resolve }, index) => {
          resolve(response.data[index]);
        });
      } 
      // For POST/PUT/PATCH, we can batch in the request body
      else {
        const batchedData = requests.map(req => req.data);
        const response = await apiClient[method.toLowerCase()](
          endpoint,
          batchedData,
          { headers: { 'X-Batch-Request': 'true' } }
        );
        requests.forEach(({ resolve }, index) => {
          resolve(response.data[index]);
        });
      }
    } catch (error) {
      requests.forEach(({ reject }) => reject(error));
    }
  }
}

// Compression helper
const compressionHelper = {
  compressQueryParams(params: Record<string, unknown>): string {
    return Object.entries(params)
      .map(([key, value]) => {
        if (Array.isArray(value)) {
          return `${key}=${value.join(',')}`;
        }
        return `${key}=${value}`;
      })
      .join('&');
  },

  decompressQueryParams(compressed: string): Record<string, unknown> {
    const params: Record<string, unknown> = {};
    compressed.split('&').forEach(param => {
      const [key, value] = param.split('=');
      if (value.includes(',')) {
        params[key] = value.split(',');
      } else {
        params[key] = value;
      }
    });
    return params;
  }
};

// Create instances
export const apiCache = new ApiCache();
export const requestBatcher = new RequestBatcher();
export const compression = compressionHelper;

// Optimized request helper
export async function optimizedRequest<T>(
  method: string,
  endpoint: string,
  config: {
    useCache?: boolean;
    cacheTTL?: number;
    useBatch?: boolean;
    data?: unknown;
    axiosConfig?: AxiosRequestConfig;
  } = {}
): Promise<T> {
  const {
    useCache = true,
    cacheTTL,
    useBatch = true,
    data,
    axiosConfig
  } = config;

  // For GET requests, try cache first
  if (method === 'GET' && useCache) {
    const cacheKey = `${method}:${endpoint}${data ? ':' + JSON.stringify(data) : ''}`;
    const cachedData = apiCache.get<T>(cacheKey);
    
    if (cachedData) {
      logger.debug('Cache hit:', { endpoint });
      return cachedData;
    }
  }

  // Use batching if enabled
  if (useBatch) {
    return requestBatcher.add<T>(endpoint, method, data);
  }

  // Regular request
  try {
    let response;
    switch (method) {
      case 'GET':
        response = await apiClient.get<T>(endpoint, axiosConfig);
        break;
      case 'POST':
        response = await apiClient.post<T>(endpoint, data, axiosConfig);
        break;
      case 'PUT':
        response = await apiClient.put<T>(endpoint, data, axiosConfig);
        break;
      case 'PATCH':
        response = await apiClient.patch<T>(endpoint, data, axiosConfig);
        break;
      case 'DELETE':
        response = await apiClient.delete<T>(endpoint, axiosConfig);
        break;
      default:
        throw new Error(`Unsupported method: ${method}`);
    }

    // Cache successful GET responses
    if (method === 'GET' && useCache) {
      const cacheKey = `${method}:${endpoint}${data ? ':' + JSON.stringify(data) : ''}`;
      apiCache.set(cacheKey, response);
    }

    return response;
  } catch (error) {
    logger.error('Request failed:', { method, endpoint, error });
    throw error;
  }
} 