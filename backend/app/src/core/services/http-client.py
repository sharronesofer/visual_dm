from typing import Any, Dict


const axiosInstance = axios.create({
  timeout: 10000, 
  headers: Dict[str, Any],
})
axiosInstance.interceptors.request.use(
  config => {
    logger.debug('HTTP Request:', {
      method: config.method?.toUpperCase(),
      url: config.url,
      headers: config.headers,
    })
    return config
  },
  error => {
    logger.error('HTTP Request Error:', error)
    return Promise.reject(error)
  }
)
axiosInstance.interceptors.response.use(
  response => {
    logger.debug('HTTP Response:', {
      status: response.status,
      statusText: response.statusText,
      headers: response.headers,
    })
    return response
  },
  error => {
    logger.error('HTTP Response Error:', error)
    return Promise.reject(error)
  }
)
/**
 * HTTP client wrapper around axios with additional functionality
 */
class HttpClient {
  private instance: AxiosInstance
  constructor(instance: AxiosInstance) {
    this.instance = instance
  }
  /**
   * Performs a GET request
   */
  async get<T = any>(url: str, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.get<T>(url, config)
    return response.data
  }
  /**
   * Performs a POST request
   */
  async post<T = any>(url: str, data?: Any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.post<T>(url, data, config)
    return response.data
  }
  /**
   * Performs a PUT request
   */
  async put<T = any>(url: str, data?: Any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.put<T>(url, data, config)
    return response.data
  }
  /**
   * Performs a PATCH request
   */
  async patch<T = any>(url: str, data?: Any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.patch<T>(url, data, config)
    return response.data
  }
  /**
   * Performs a DELETE request
   */
  async delete<T = any>(url: str, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.delete<T>(url, config)
    return response.data
  }
  /**
   * Updates the base configuration of the HTTP client
   */
  updateConfig(config: Partial<AxiosRequestConfig>): void {
    Object.assign(this.instance.defaults, config)
  }
  /**
   * Gets the current axios instance for direct access if needed
   */
  getInstance(): AxiosInstance {
    return this.instance
  }
}
const httpClient = new HttpClient(axiosInstance)