import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';

export const createAxiosInstance = (config: AxiosRequestConfig): AxiosInstance => {
  const instance = axios.create({
    timeout: 30000, // Default timeout of 30 seconds
    headers: {
      'Content-Type': 'application/json',
    },
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
