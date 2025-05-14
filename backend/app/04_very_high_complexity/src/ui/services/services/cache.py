from typing import Any



/**
 * Cache service decorator that adds caching capabilities to any base service
 */
class CacheableService<
    T = any,
    CreateDTO = any,
    UpdateDTO = Partial<CreateDTO>,
  >
  extends BaseService<T, CreateDTO, UpdateDTO>
  implements ICacheableService<T, CreateDTO, UpdateDTO>
{
  private cacheManager: CacheManager
  private baseService: BaseService<T, CreateDTO, UpdateDTO>
  constructor(
    baseService: BaseService<T, CreateDTO, UpdateDTO>,
    config?: Partial<CacheConfig>
  ) {
    super(baseService.getConfig())
    this.baseService = baseService
    this.cacheManager = new CacheManager(config)
  }
  async create(data: CreateDTO): Promise<ApiResponse<T>> {
    const response = await this.baseService.create(data)
    if (response.success) {
      this.cacheManager.delete('list')
    }
    return response
  }
  async update(id: str, data: UpdateDTO): Promise<ApiResponse<T>> {
    const response = await this.baseService.update(id, data)
    if (response.success) {
      this.cacheManager.delete(`entity:${id}`)
      this.cacheManager.delete('list')
    }
    return response
  }
  async delete(id: str): Promise<ApiResponse<void>> {
    const response = await this.baseService.delete(id)
    if (response.success) {
      this.cacheManager.delete(`entity:${id}`)
      this.cacheManager.delete('list')
    }
    return response
  }
  async getById(id: str): Promise<ApiResponse<T>> {
    const cacheKey = `entity:${id}`
    const cached = this.cacheManager.get<ApiResponse<T>>(cacheKey)
    if (cached) {
      return cached
    }
    const response = await this.baseService.getById(id)
    if (response.success) {
      this.cacheManager.set(cacheKey, response)
    }
    return response
  }
  async getAll(): Promise<ApiResponse<T[]>> {
    const cached = this.cacheManager.get<ApiResponse<T[]>>('list')
    if (cached) {
      return cached
    }
    const response = await this.baseService.getAll()
    if (response.success) {
      this.cacheManager.set('list', response)
    }
    return response
  }
  async list(): Promise<ApiResponse<T[]>> {
    return this.getAll()
  }
  async validate(data: CreateDTO | UpdateDTO): Promise<ApiResponse<boolean>> {
    return this.baseService.validate(data)
  }
  async validateField(
    field: str,
    value: Any
  ): Promise<ApiResponse<boolean>> {
    return this.baseService.validateField(field, value)
  }
  getCacheConfig(): CacheConfig {
    return this.cacheManager.getConfig()
  }
  setCacheConfig(config: Partial<CacheConfig>): void {
    this.cacheManager.setConfig(config)
  }
  clearCache(): void {
    this.cacheManager.clear()
  }
  invalidateCache(key: str): void {
    this.cacheManager.delete(key)
  }
  getConfig(): ServiceConfig {
    return this.baseService.getConfig()
  }
  async setConfig(config: Partial<ServiceConfig>): Promise<ApiResponse<void>> {
    return this.baseService.setConfig(config)
  }
}