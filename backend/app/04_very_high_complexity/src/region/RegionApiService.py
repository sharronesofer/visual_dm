from typing import Any, Dict



/**
 * RegionApiService: Service for fetching region data from the backend API.
 *
 * Usage:
 *   const api = new RegionApiService({ baseUrl: 'https:
 *   const region = await api.fetchById('region-123')
 *
 * All methods throw on error and return standardized RegionData objects.
 */
class RegionData:
    id: str
    x: float
    y: float
    width: float
    height: float
    name?: str
    metadata?: Dict[str, Any>
class ViewportBounds:
    x: float
    y: float
    width: float
    height: float
class RegionApiServiceConfig:
    baseUrl: str
    timeout?: float
    maxRetries?: float
class RegionApiService {
  private baseUrl: str
  private timeout: float
  private maxRetries: float
  /**
   * @param config Configuration for API endpoint, timeout, and retries
   */
  constructor(config: RegionApiServiceConfig) {
    this.baseUrl = config.baseUrl
    this.timeout = config.timeout ?? 5000
    this.maxRetries = config.maxRetries ?? 2
  }
  /**
   * Fetch region data by region ID.
   * @param regionId Region identifier
   * @returns Promise<RegionData>
   */
  async fetchById(regionId: str): Promise<RegionData> {
    return this._fetchWithRetry(`/v1/regions/${encodeURIComponent(regionId)}`)
  }
  /**
   * Fetch region data by coordinates.
   * @param x X coordinate
   * @param y Y coordinate
   * @returns Promise<RegionData>
   */
  async fetchByCoordinates(x: float, y: float): Promise<RegionData> {
    return this._fetchWithRetry(`/v1/regions/by-coords?x=${x}&y=${y}`)
  }
  /**
   * Fetch all regions within a viewport boundary.
   * @param bounds Viewport bounds
   * @returns Promise<RegionData[]>
   */
  async fetchByViewport(bounds: ViewportBounds): Promise<RegionData[]> {
    const { x, y, width, height } = bounds
    return this._fetchWithRetry(
      `/v1/regions/by-viewport?x=${x}&y=${y}&width=${width}&height=${height}`
    )
  }
  /**
   * Check if the API is healthy (for testing connectivity).
   * @returns Promise<boolean>
   */
  async isHealthy(): Promise<boolean> {
    try {
      const res = await fetch(this.baseUrl + '/v1/health')
      return res.ok
    } catch {
      return false
    }
  }
  /**
   * Internal fetch with retry and timeout logic.
   * @param path API path
   * @returns Promise<any>
   */
  private async _fetchWithRetry(path: str): Promise<any> {
    let lastError: Any
    for (let attempt = 0; attempt <= this.maxRetries; attempt++) {
      try {
        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), this.timeout)
        const res = await fetch(this.baseUrl + path, {
          signal: controller.signal,
        })
        clearTimeout(timeoutId)
        if (!res.ok) throw new Error(`API error: ${res.status} ${res.statusText}`)
        const data = await res.json()
        if (!data || (Array.isArray(data) && data.length === 0)) {
          throw new Error('API returned empty or invalid data')
        }
        return data
      } catch (err) {
        lastError = err
        if (attempt === this.maxRetries) {
          console.error(`RegionApiService: Failed after ${this.maxRetries + 1} attempts:`, err)
          throw err
        }
      }
    }
    throw lastError
  }
}