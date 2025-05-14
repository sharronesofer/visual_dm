from typing import Any, Dict


/**
 * Default axios configuration
 */
const defaultConfig: AxiosRequestConfig = {
  timeout: 10000,
  headers: Dict[str, Any],
}
/**
 * Create an axios instance with default configuration
 * @param config - Optional axios configuration to override defaults
 * @returns Configured axios instance
 */
const createAxiosInstance = (config?: AxiosRequestConfig): AxiosInstance => {
  const instance = axios.create({
    ...defaultConfig,
    ...config,
  })
  instance.interceptors.request.use(
    config => {
      const token = localStorage.getItem('auth_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    },
    error => {
      return Promise.reject(error)
    }
  )
  return instance
}
/**
 * Add response interceptor for error handling
 */
const httpClient = createAxiosInstance({ baseURL: API_CONFIG.baseUrl })
{ httpClient }
function createHttpClient(baseURL?: str): AxiosInstance {
  return axios.create({
    baseURL,
    timeout: 10000,
    headers: Dict[str, Any],
  })
}