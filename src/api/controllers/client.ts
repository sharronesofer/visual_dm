import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { API_BASE_URL, AUTH_HEADER, TOKEN_KEY } from '../constants';
import { AppError, ValidationError, FormattedValidationError } from '../utils/errors';
import { Logger } from '../utils/logger';
import { ApiResponse, ErrorResponse } from '../types';
import { optimizedRequest } from '../utils/apiOptimization';

const logger = new Logger({ prefix: 'ApiClient' });

class ApiClient {
  private instance: AxiosInstance;

  constructor() {
    this.instance = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br',
      },
      // Enable response compression
      decompress: true,
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    // Request interceptor
    this.instance.interceptors.request.use(
      config => {
        const token = localStorage.getItem(TOKEN_KEY);
        if (token) {
          config.headers[AUTH_HEADER] = `Bearer ${token}`;
        }

        // Add support for request batching
        if (config.headers['X-Batch-Request']) {
          config.headers['Content-Type'] = 'application/json+batch';
        }

        return config;
      },
      error => {
        logger.error('Request error:', { error });
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.instance.interceptors.response.use(
      response => {
        // Store ETag for caching if present
        const etag = response.headers['etag'];
        if (etag) {
          const cacheKey = `${response.config.method}:${response.config.url}`;
          localStorage.setItem(`etag:${cacheKey}`, etag);
        }
        return response;
      },
      error => {
        if (error.response) {
          const { data, status } = error.response;
          const errorResponse = data as ErrorResponse;

          switch (status) {
            case 304:
              // Not Modified - return cached response
              return Promise.resolve(error.response);
            case 400:
              if (errorResponse.code === 'VALIDATION_ERROR') {
                const validationErrors = Array.isArray(errorResponse.details)
                  ? errorResponse.details.map(
                      (detail: Record<string, unknown>): FormattedValidationError => ({
                        path: String(detail.path || ''),
                        message: String(detail.message || ''),
                      })
                    )
                  : [];
                throw new ValidationError(errorResponse.message, validationErrors);
              }
              throw new AppError(errorResponse.message, status);
            case 401:
              // Handle unauthorized (e.g., redirect to login)
              window.location.href = '/login';
              throw new AppError(errorResponse.message, status);
            case 403:
              throw new AppError(errorResponse.message, status);
            case 404:
              throw new AppError(errorResponse.message, status);
            case 409:
              throw new AppError(errorResponse.message, status);
            default:
              throw new AppError(errorResponse.message || 'An unexpected error occurred', status);
          }
        }

        logger.error('Network error:', { error });
        throw new AppError('Network error', 500);
      }
    );
  }

  public async get<T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    // Add ETag support for conditional requests
    const cacheKey = `GET:${url}`;
    const etag = localStorage.getItem(`etag:${cacheKey}`);
    
    const headers = {
      ...config?.headers,
      ...(etag && { 'If-None-Match': etag }),
    };

    return optimizedRequest<ApiResponse<T>>('GET', url, {
      useCache: true,
      useBatch: true,
      axiosConfig: { ...config, headers },
    });
  }

  public async post<T>(
    url: string,
    data?: unknown,
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    return optimizedRequest<ApiResponse<T>>('POST', url, {
      data,
      useBatch: true,
      axiosConfig: config,
    });
  }

  public async put<T>(
    url: string,
    data?: unknown,
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    return optimizedRequest<ApiResponse<T>>('PUT', url, {
      data,
      useBatch: true,
      axiosConfig: config,
    });
  }

  public async patch<T>(
    url: string,
    data?: unknown,
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    return optimizedRequest<ApiResponse<T>>('PATCH', url, {
      data,
      useBatch: true,
      axiosConfig: config,
    });
  }

  public async delete<T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return optimizedRequest<ApiResponse<T>>('DELETE', url, {
      useBatch: false, // Don't batch DELETE requests
      axiosConfig: config,
    });
  }
}

export const apiClient = new ApiClient();
