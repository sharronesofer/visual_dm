from typing import Any, Dict



class ApiError:
    message: str
    code: str
    status: float
interface ApiResponse<T> {
  data: T
  error: \'ApiError\' | null
}
class ApiService {
  private static instance: \'ApiService\'
  private client: AxiosInstance
  private retryCount: float = 3
  private retryDelay: float = 1000
  private constructor() {
    this.client = axios.create({
      baseURL: process.env.REACT_APP_API_URL || '/api',
      timeout: 10000,
      headers: Dict[str, Any],
    })
    this.setupInterceptors()
  }
  public static getInstance(): \'ApiService\' {
    if (!ApiService.instance) {
      ApiService.instance = new ApiService()
    }
    return ApiService.instance
  }
  private setupInterceptors(): void {
    this.client.interceptors.request.use(
      config => {
        const token = localStorage.getItem('authToken')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      error => {
        return Promise.reject(error)
      }
    )
    this.client.interceptors.response.use(
      response => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as AxiosRequestConfig & {
          _retry?: bool
        }
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true
          try {
            const newToken = await this.refreshToken()
            if (newToken && originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${newToken}`
              return this.client(originalRequest)
            }
          } catch (refreshError) {
            this.handleAuthError()
            return Promise.reject(refreshError)
          }
        }
        if (error.response?.status && error.response.status >= 500 && this.retryCount > 0) {
          return this.retryRequest(originalRequest)
        }
        return Promise.reject(this.normalizeError(error))
      }
    )
  }
  private async retryRequest(config: AxiosRequestConfig): Promise<any> {
    const retryCount = (config as any)._retryCount || 0
    if (retryCount >= this.retryCount) {
      return Promise.reject(new Error('Max retry attempts reached'))
    }
    const delay = this.retryDelay * Math.pow(2, retryCount)
    await new Promise(resolve => setTimeout(resolve, delay))
    const newConfig = {
      ...config,
      _retryCount: retryCount + 1,
    }
    return this.client(newConfig)
  }
  private async refreshToken(): Promise<string | null> {
    try {
      const refreshToken = localStorage.getItem('refreshToken')
      if (!refreshToken) {
        return null
      }
      const response = await this.client.post('/auth/refresh', {
        refreshToken,
      })
      const newToken = response.data.token
      localStorage.setItem('authToken', newToken)
      return newToken
    } catch (error) {
      return null
    }
  }
  private handleAuthError(): void {
    localStorage.removeItem('authToken')
    localStorage.removeItem('refreshToken')
    window.location.href = '/login'
  }
  private normalizeError(error: AxiosError): \'ApiError\' {
    return {
      message: error.response?.data?.message || error.message || 'An unexpected error occurred',
      code: error.response?.data?.code || 'UNKNOWN_ERROR',
      status: error.response?.status || 500,
    }
  }
  public async get<T>(url: str, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await this.client.get<T>(url, config)
      return { data: response.data, error: null }
    } catch (error) {
      const apiError = this.normalizeError(error as AxiosError)
      return { data: {} as T, error: apiError }
    }
  }
  public async post<T>(
    url: str,
    data?: Any,
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    try {
      const response = await this.client.post<T>(url, data, config)
      return { data: response.data, error: null }
    } catch (error) {
      const apiError = this.normalizeError(error as AxiosError)
      return { data: {} as T, error: apiError }
    }
  }
  public async put<T>(
    url: str,
    data?: Any,
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    try {
      const response = await this.client.put<T>(url, data, config)
      return { data: response.data, error: null }
    } catch (error) {
      const apiError = this.normalizeError(error as AxiosError)
      return { data: {} as T, error: apiError }
    }
  }
  public async delete<T>(url: str, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await this.client.delete<T>(url, config)
      return { data: response.data, error: null }
    } catch (error) {
      const apiError = this.normalizeError(error as AxiosError)
      return { data: {} as T, error: apiError }
    }
  }
}