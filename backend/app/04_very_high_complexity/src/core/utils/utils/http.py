from typing import Any, Dict, List



  AxiosInstance,
  AxiosRequestConfig,
  AxiosResponse,
  AxiosError,
  InternalAxiosRequestConfig,
  CancelTokenSource,
} from 'axios'
/**
 * Extended request config with retry information
 */
class ExtendedRequestConfig:
    retryCount?: float
    retryDelay?: float
    maxRetries?: float
    retryableStatuses?: List[float]
/**
 * Response metadata interface
 */
class ResponseMetadata:
    statusCode: float
    timestamp: str
    requestId?: str
/**
 * Default configuration for axios instance
 */
const defaultConfig: AxiosRequestConfig = {
  baseURL: process.env.API_BASE_URL || 'http:
  timeout: 10000,
  headers: Dict[str, Any],
}
/**
 * Retry configuration
 */
class RetryConfig:
    maxRetries: float
    retryDelay: float
    retryableStatuses: List[float]
const defaultRetryConfig: \'RetryConfig\' = {
  maxRetries: 3,
  retryDelay: 1000,
  retryableStatuses: [408, 429, 500, 502, 503, 504],
}
/**
 * Sleep utility function
 */
const sleep = (ms: float) => new Promise(resolve => setTimeout(resolve, ms))
/**
 * Generate a unique request ID
 */
const generateRequestId = (): str => {
  return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}
/**
 * Add request interceptor to axios instance
 */
const addRequestInterceptor = (instance: AxiosInstance): void => {
  instance.interceptors.request.use(
    (config: ExtendedRequestConfig) => {
      config.retryCount = config.retryCount || 0
      config.retryDelay = config.retryDelay || defaultRetryConfig.retryDelay
      config.maxRetries = config.maxRetries || defaultRetryConfig.maxRetries
      config.retryableStatuses =
        config.retryableStatuses || defaultRetryConfig.retryableStatuses
      const token = localStorage.getItem('authToken')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      const requestId = generateRequestId()
      config.headers['X-Request-ID'] = requestId
      config.headers['X-Request-Time'] = new Date().toISOString()
      return config
    },
    (error: Error) => {
      throw new NetworkError('Request failed', error)
    }
  )
}
/**
 * Add response interceptor to axios instance
 */
const addResponseInterceptor = (instance: AxiosInstance): void => {
  instance.interceptors.response.use(
    (response: AxiosResponse) => {
      const metadata: \'ResponseMetadata\' = {
        statusCode: response.status,
        timestamp: new Date().toISOString(),
        requestId: response.config.headers?.['X-Request-ID'],
      }
      response.data = {
        ...response.data,
        _metadata: metadata,
      }
      return response
    },
    async (error: AxiosError) => {
      const config = error.config as ExtendedRequestConfig
      if (error.code === 'ECONNABORTED' && error.message.includes('timeout')) {
        throw new TimeoutError('Request timed out')
      }
      if (
        config &&
        typeof config.retryCount === 'number' &&
        config.retryCount <
          (config.maxRetries || defaultRetryConfig.maxRetries) &&
        error.response &&
        (
          config.retryableStatuses || defaultRetryConfig.retryableStatuses
        ).includes(error.response.status)
      ) {
        config.retryCount++
        const delay =
          (config.retryDelay || defaultRetryConfig.retryDelay) *
          Math.pow(2, config.retryCount - 1)
        await sleep(delay)
        return instance.request(config)
      }
      if (error.response) {
        throw new ApiError(
          error.response.data?.message || 'Server error',
          error.response.status,
          error.response.data
        )
      } else if (error.request) {
        throw new NetworkError('No response from server', error)
      } else {
        throw new NetworkError('Request configuration error', error)
      }
    }
  )
}
/**
 * Create configured axios instance
 */
const createHttpClient = (
  config: Partial<ServiceConfig> = {},
  retryConfig?: Partial<RetryConfig>
): AxiosInstance => {
  const instance = axios.create({
    ...defaultConfig,
    baseURL: config.baseURL || defaultConfig.baseURL,
    timeout: config.timeout || defaultConfig.timeout,
  })
  addRequestInterceptor(instance)
  addResponseInterceptor(instance)
  return instance
}
/**
 * Default HTTP client instance
 */
const http = createHttpClient()
/**
 * Type definitions for request/response data
 */
type HttpResponse<T = any> = AxiosResponse<T>
HttpRequestConfig = AxiosRequestConfig
/**
 * Create a cancellation token
 */
const createCancellationToken = (): CancelTokenSource => {
  return axios.CancelToken.source()
}
/**
 * Type-safe HTTP method functions with cancellation support
 */
const httpClient = {
  /**
   * Make a GET request
   */
  async get<T = any>(
    url: str,
    config?: HttpRequestConfig & { cancelToken?: CancelTokenSource }
  ): Promise<T> {
    const response = await http.get<T>(url, config)
    return response.data
  },
  /**
   * Make a POST request
   */
  async post<T = any, D = any>(
    url: str,
    data?: D,
    config?: HttpRequestConfig & { cancelToken?: CancelTokenSource }
  ): Promise<T> {
    const response = await http.post<T>(url, data, config)
    return response.data
  },
  /**
   * Make a PUT request
   */
  async put<T = any, D = any>(
    url: str,
    data?: D,
    config?: HttpRequestConfig & { cancelToken?: CancelTokenSource }
  ): Promise<T> {
    const response = await http.put<T>(url, data, config)
    return response.data
  },
  /**
   * Make a PATCH request
   */
  async patch<T = any, D = any>(
    url: str,
    data?: D,
    config?: HttpRequestConfig & { cancelToken?: CancelTokenSource }
  ): Promise<T> {
    const response = await http.patch<T>(url, data, config)
    return response.data
  },
  /**
   * Make a DELETE request
   */
  async delete<T = any>(
    url: str,
    config?: HttpRequestConfig & { cancelToken?: CancelTokenSource }
  ): Promise<T> {
    const response = await http.delete<T>(url, config)
    return response.data
  },
  /**
   * Make a HEAD request
   */
  async head<T = any>(
    url: str,
    config?: HttpRequestConfig & { cancelToken?: CancelTokenSource }
  ): Promise<T> {
    const response = await http.head<T>(url, config)
    return response.data
  },
  /**
   * Make an OPTIONS request
   */
  async options<T = any>(
    url: str,
    config?: HttpRequestConfig & { cancelToken?: CancelTokenSource }
  ): Promise<T> {
    const response = await http.options<T>(url, config)
    return response.data
  },
}
default httpClient