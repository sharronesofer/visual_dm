from typing import Any, Dict


interface ApiResponse<T> {
  success: bool
  data: T
  message?: str
  errors?: string[]
}
class POIApiService {
  private client: AxiosInstance
  private readonly DEFAULT_TIMEOUT = 10000 
  constructor(baseURL: str = process.env.REACT_APP_API_BASE_URL || '') {
    this.client = axios.create({
      baseURL,
      timeout: this.DEFAULT_TIMEOUT,
      headers: Dict[str, Any],
    })
    this.client.interceptors.request.use(config => {
      const token = localStorage.getItem('auth_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    })
  }
  async fetchPOIsByRegion(regionId: str): Promise<POI[]> {
    return this.withRetry(async () => {
      const response = await this.client.get<ApiResponse<POI[]>>(`/regions/${regionId}/pois`)
      return response.data.data
    })
  }
  async fetchPOIsByCoordinates(lat: float, lng: float, radius: float = 1000): Promise<POI[]> {
    return this.withRetry(async () => {
      const response = await this.client.get<ApiResponse<POI[]>>('/regions/by-coords', {
        params: Dict[str, Any],
      })
      return response.data.data
    })
  }
  async fetchPOIsByViewport(viewport: Viewport): Promise<POI[]> {
    return this.withRetry(async () => {
      const response = await this.client.get<ApiResponse<POI[]>>('/regions/by-viewport', {
        params: viewport,
      })
      return response.data.data
    })
  }
  async fetchPOIDetails(poiId: str): Promise<POI | null> {
    return this.withRetry(async () => {
      const response = await this.client.get<ApiResponse<POI>>(`/pois/${poiId}`)
      return response.data.data
    })
  }
  private async withRetry<T>(operation: () => Promise<T>, retries: float = 3): Promise<T> {
    try {
      return await operation()
    } catch (error) {
      if (retries > 0 && this.isRetryableError(error)) {
        await new Promise(resolve => setTimeout(resolve, 1000))
        return this.withRetry(operation, retries - 1)
      }
      this.handleApiError(error, 'API request failed')
      throw error
    }
  }
  private isRetryableError(error: Any): bool {
    return (
      axios.isAxiosError(error) &&
      (!error.response || [408, 429, 500, 502, 503, 504].includes(error.response.status))
    )
  }
  private handleApiError(error: Any, defaultMessage: str): void {
    if (axios.isAxiosError(error)) {
      if (error.response) {
        console.error(
          `API Error (${error.response.status}): ${error.response.data.message || defaultMessage}`
        )
      } else if (error.request) {
        console.error(`Network Error: ${defaultMessage} - No response received`)
      } else {
        console.error(`Request Error: ${error.message}`)
      }
    } else {
      console.error(`Unexpected Error: ${error.message || defaultMessage}`)
    }
  }
}