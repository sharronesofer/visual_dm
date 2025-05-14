import axios, { AxiosInstance, AxiosError, AxiosRequestConfig } from 'axios';

export interface ApiError {
  message: string;
  code: string;
  status: number;
}

export interface ApiResponse<T> {
  data: T;
  error: ApiError | null;
}

export class ApiService {
  private static instance: ApiService;
  private client: AxiosInstance;
  private retryCount: number = 3;
  private retryDelay: number = 1000;

  private constructor() {
    this.client = axios.create({
      baseURL: process.env.REACT_APP_API_URL || '/api',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  public static getInstance(): ApiService {
    if (!ApiService.instance) {
      ApiService.instance = new ApiService();
    }
    return ApiService.instance;
  }

  private setupInterceptors(): void {
    // Request interceptor
    this.client.interceptors.request.use(
      config => {
        // Add auth token if available
        const token = localStorage.getItem('authToken');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      error => {
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      response => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as AxiosRequestConfig & {
          _retry?: boolean;
        };

        // Handle unauthorized errors (401)
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          try {
            // Attempt to refresh token
            const newToken = await this.refreshToken();
            if (newToken && originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${newToken}`;
              return this.client(originalRequest);
            }
          } catch (refreshError) {
            // Handle refresh token failure
            this.handleAuthError();
            return Promise.reject(refreshError);
          }
        }

        // Handle retry for server errors (5xx)
        if (error.response?.status && error.response.status >= 500 && this.retryCount > 0) {
          return this.retryRequest(originalRequest);
        }

        return Promise.reject(this.normalizeError(error));
      }
    );
  }

  private async retryRequest(config: AxiosRequestConfig): Promise<any> {
    const retryCount = (config as any)._retryCount || 0;

    if (retryCount >= this.retryCount) {
      return Promise.reject(new Error('Max retry attempts reached'));
    }

    // Exponential backoff
    const delay = this.retryDelay * Math.pow(2, retryCount);
    await new Promise(resolve => setTimeout(resolve, delay));

    const newConfig = {
      ...config,
      _retryCount: retryCount + 1,
    };

    return this.client(newConfig);
  }

  private async refreshToken(): Promise<string | null> {
    try {
      const refreshToken = localStorage.getItem('refreshToken');
      if (!refreshToken) {
        return null;
      }

      const response = await this.client.post('/auth/refresh', {
        refreshToken,
      });
      const newToken = response.data.token;
      localStorage.setItem('authToken', newToken);
      return newToken;
    } catch (error) {
      return null;
    }
  }

  private handleAuthError(): void {
    localStorage.removeItem('authToken');
    localStorage.removeItem('refreshToken');
    // Redirect to login or dispatch logout action
    window.location.href = '/login';
  }

  private normalizeError(error: AxiosError): ApiError {
    return {
      message: error.response?.data?.message || error.message || 'An unexpected error occurred',
      code: error.response?.data?.code || 'UNKNOWN_ERROR',
      status: error.response?.status || 500,
    };
  }

  public async get<T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await this.client.get<T>(url, config);
      return { data: response.data, error: null };
    } catch (error) {
      const apiError = this.normalizeError(error as AxiosError);
      return { data: {} as T, error: apiError };
    }
  }

  public async post<T>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    try {
      const response = await this.client.post<T>(url, data, config);
      return { data: response.data, error: null };
    } catch (error) {
      const apiError = this.normalizeError(error as AxiosError);
      return { data: {} as T, error: apiError };
    }
  }

  public async put<T>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    try {
      const response = await this.client.put<T>(url, data, config);
      return { data: response.data, error: null };
    } catch (error) {
      const apiError = this.normalizeError(error as AxiosError);
      return { data: {} as T, error: apiError };
    }
  }

  public async delete<T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await this.client.delete<T>(url, config);
      return { data: response.data, error: null };
    } catch (error) {
      const apiError = this.normalizeError(error as AxiosError);
      return { data: {} as T, error: apiError };
    }
  }
}
