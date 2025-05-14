import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { API_CONFIG } from '../constants';

/**
 * Default axios configuration
 */
const defaultConfig: AxiosRequestConfig = {
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
};

/**
 * Create an axios instance with default configuration
 * @param config - Optional axios configuration to override defaults
 * @returns Configured axios instance
 */
export const createAxiosInstance = (config?: AxiosRequestConfig): AxiosInstance => {
  const instance = axios.create({
    ...defaultConfig,
    ...config,
  });

  // Add request interceptor for authentication
  instance.interceptors.request.use(
    config => {
      const token = localStorage.getItem('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    error => {
      return Promise.reject(error);
    }
  );

  return instance;
};

/**
 * Add response interceptor for error handling
 */
const httpClient = createAxiosInstance({ baseURL: API_CONFIG.baseUrl });
export { httpClient };

export function createHttpClient(baseURL?: string): AxiosInstance {
  return axios.create({
    baseURL,
    timeout: 10000,
    headers: {
      'Content-Type': 'application/json',
    },
  });
}
