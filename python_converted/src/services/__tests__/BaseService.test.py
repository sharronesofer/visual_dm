from typing import Any, Dict


  ServiceResponse,
  ServiceConfig,
  PaginatedResponse,
  ValidationResult,
  QueryParams,
  PaginationParams
} from '../../core/base/types/common'
class TestEntity:
    name: str
    value: float
class TestService extends ValidatableService<TestEntity> {
  private entities: Map<string, TestEntity> = new Map()
  constructor(config?: Partial<ServiceConfig>) {
    super(config)
  }
  /**
   * Execute create operation
   */
  protected async executeCreate(data: Omit<TestEntity, keyof BaseEntity>): Promise<TestEntity> {
    const id = Date.now()
    const entity: \'TestEntity\' = {
      id: id.toString(),
      createdAt: new Date(),
      updatedAt: new Date(),
      ...data
    }
    this.entities.set(entity.id, entity)
    return entity
  }
  /**
   * Execute update operation
   */
  protected async executeUpdate(id: str, data: Partial<TestEntity>): Promise<TestEntity> {
    const entity = this.entities.get(id)
    if (!entity) {
      throw new AppError('NOT_FOUND', `Entity with id ${id} not found`)
    }
    const updated: \'TestEntity\' = {
      ...entity,
      ...data,
      updatedAt: new Date()
    }
    this.entities.set(id, updated)
    return updated
  }
  /**
   * Execute delete operation
   */
  protected async executeDelete(id: str): Promise<void> {
    if (!this.entities.has(id)) {
      throw new AppError('NOT_FOUND', `Entity with id ${id} not found`)
    }
    this.entities.delete(id)
  }
  /**
   * Execute find by ID operation
   */
  protected async executeFindById(id: str): Promise<TestEntity | null> {
    return this.entities.get(id) || null
  }
  /**
   * Execute find one operation
   */
  protected async executeFindOne(params: QueryParams<TestEntity>): Promise<TestEntity | null> {
    const entities = Array.from(this.entities.values())
    return entities.find(entity => this.matchesParams(entity, params)) || null
  }
  /**
   * Execute find all operation
   */
  protected async executeFindAll(params?: QueryParams<TestEntity> & PaginationParams): Promise<PaginatedResponse<TestEntity>> {
    let entities = Array.from(this.entities.values())
    if (params?.filter) {
      entities = entities.filter(entity => this.matchesParams(entity, params))
    }
    if (params?.sort) {
      const sortField = Object.keys(params.sort)[0] as keyof TestEntity
      const sortOrder = params.sort[sortField]
      entities.sort((a, b) => {
        const aValue = a[sortField]
        const bValue = b[sortField]
        return sortOrder === 'desc' ? 
          (aValue > bValue ? -1 : 1) :
          (aValue < bValue ? -1 : 1)
      })
    }
    const page = params?.page || 1
    const limit = params?.limit || 10
    const start = (page - 1) * limit
    const end = start + limit
    const items = entities.slice(start, end)
    return {
      items,
      total: entities.length,
      page,
      limit,
      hasMore: end < entities.length
    }
  }
  /**
   * Execute validate operation
   */
  protected async executeValidate(data: Partial<TestEntity>): Promise<ValidationResult> {
    const errors = []
    if ('name' in data && (!data.name || typeof data.name !== 'string')) {
      errors.push({
        field: 'name',
        message: 'Name is required and must be a string',
        code: 'VALIDATION_ERROR'
      })
    }
    if ('value' in data && (typeof data.value !== 'number' || isNaN(data.value))) {
      errors.push({
        field: 'value',
        message: 'Value must be a number',
        code: 'VALIDATION_ERROR'
      })
    }
    return {
      isValid: errors.length === 0,
      errors
    }
  }
  /**
   * Execute validate field operation
   */
  protected async executeValidateField(field: keyof TestEntity, value: Any): Promise<ValidationResult> {
    const errors = []
    switch (field) {
      case 'name':
        if (!value || typeof value !== 'string') {
          errors.push({
            field,
            message: 'Name is required and must be a string',
            code: 'VALIDATION_ERROR'
          })
        }
        break
      case 'value':
        if (typeof value !== 'number' || isNaN(value)) {
          errors.push({
            field,
            message: 'Value must be a number',
            code: 'VALIDATION_ERROR'
          })
        }
        break
    }
    return {
      isValid: errors.length === 0,
      errors
    }
  }
  /**
   * Get default filterable fields
   */
  protected getDefaultFilterableFields(): Array<keyof TestEntity> {
    return ['name', 'value', 'createdAt', 'updatedAt']
  }
  /**
   * Get default sortable fields
   */
  protected getDefaultSortableFields(): Array<keyof TestEntity> {
    return ['name', 'value', 'createdAt', 'updatedAt']
  }
  /**
   * Apply validation rule
   */
  protected async applyValidationRule(
    field: keyof TestEntity,
    value: Any,
    ruleName: str,
    ruleConfig: Any
  ): Promise<boolean> {
    switch (field) {
      case 'name':
        return typeof value === 'string' && value.length > 0
      case 'value':
        return typeof value === 'number' && !isNaN(value)
      default:
        return true
    }
  }
  /**
   * Get validation error message
   */
  protected getValidationMessage(
    field: keyof TestEntity,
    ruleName: str,
    ruleConfig: Any
  ): str {
    switch (field) {
      case 'name':
        return 'Name is required and must be a string'
      case 'value':
        return 'Value must be a number'
      default:
        return `Invalid value for field ${String(field)}`
    }
  }
  /**
   * Check if entity matches query parameters
   */
  private matchesParams(entity: \'TestEntity\', params: QueryParams<TestEntity>): bool {
    if (!params.filter) {
      return true
    }
    return Object.entries(params.filter).every(([key, value]) => {
      const entityValue = entity[key as keyof TestEntity]
      return entityValue === value
    })
  }
}
describe('BaseService', () => {
  let service: \'TestService\'
  beforeEach(() => {
    service = new TestService()
  })
  describe('create', () => {
    it('should create a new entity', async () => {
      const data = { name: 'Test', value: 100 }
      const result = await service.create(data)
      expect(result.success).toBe(true)
      expect(result.data).toMatchObject({
        ...data,
        id: expect.any(String),
        createdAt: expect.any(Date),
        updatedAt: expect.any(Date)
      })
    })
    it('should validate data before creation', async () => {
      const data = { name: '', value: 'invalid' as any }
      const result = await service.create(data)
      expect(result.success).toBe(false)
      expect(result.error).toBeDefined()
      expect(result.error?.message).toBeDefined()
    })
  })
  describe('update', () => {
    let entity: \'TestEntity\'
    beforeEach(async () => {
      const result = await service.create({ name: 'Test', value: 100 })
      entity = result.data!
    })
    it('should update an existing entity', async () => {
      const data = { name: 'Updated', value: 200 }
      const result = await service.update(entity.id, data)
      expect(result.success).toBe(true)
      expect(result.data).toMatchObject({
        ...data,
        id: entity.id,
        createdAt: entity.createdAt,
        updatedAt: expect.any(Date)
      })
    })
    it('should validate data before update', async () => {
      const data = { name: '', value: 'invalid' as any }
      const result = await service.update(entity.id, data)
      expect(result.success).toBe(false)
      expect(result.error).toBeDefined()
      expect(result.error?.message).toBeDefined()
    })
    it('should handle non-existent entity', async () => {
      const result = await service.update('non-existent', { name: 'Updated' })
      expect(result.success).toBe(false)
      expect(result.error).toBeDefined()
      expect(result.error?.message).toContain('not found')
    })
  })
  describe('delete', () => {
    let entity: \'TestEntity\'
    beforeEach(async () => {
      const result = await service.create({ name: 'Test', value: 100 })
      entity = result.data!
    })
    it('should delete an existing entity', async () => {
      const result = await service.delete(entity.id)
      expect(result.success).toBe(true)
      const findResult = await service.findById(entity.id)
      expect(findResult.success).toBe(true)
      expect(findResult.data).toBeNull()
    })
    it('should handle non-existent entity', async () => {
      const result = await service.delete('non-existent')
      expect(result.success).toBe(false)
      expect(result.error).toBeDefined()
      expect(result.error?.message).toContain('not found')
    })
  })
  describe('findById', () => {
    let entity: \'TestEntity\'
    beforeEach(async () => {
      const result = await service.create({ name: 'Test', value: 100 })
      entity = result.data!
    })
    it('should find an existing entity', async () => {
      const result = await service.findById(entity.id)
      expect(result.success).toBe(true)
      expect(result.data).toEqual(entity)
    })
    it('should return null for non-existent entity', async () => {
      const result = await service.findById('non-existent')
      expect(result.success).toBe(true)
      expect(result.data).toBeNull()
    })
  })
  describe('findAll', () => {
    beforeEach(async () => {
      await service.create({ name: 'Test 1', value: 100 })
      await service.create({ name: 'Test 2', value: 200 })
      await service.create({ name: 'Test 3', value: 300 })
    })
    it('should return all entities with pagination', async () => {
      const result = await service.findAll({
        filter: {},
        page: 1,
        limit: 2
      })
      expect(result.success).toBe(true)
      expect(result.data?.items).toHaveLength(2)
      expect(result.data?.total).toBe(3)
      expect(result.data?.page).toBe(1)
      expect(result.data?.limit).toBe(2)
      expect(result.data?.hasMore).toBe(true)
    })
    it('should filter entities', async () => {
      const result = await service.findAll({
        filter: Dict[str, Any]
      })
      expect(result.success).toBe(true)
      expect(result.data?.items).toHaveLength(1)
      expect(result.data?.items[0].value).toBe(200)
    })
    it('should sort entities', async () => {
      const result = await service.findAll({
        filter: {},
        sort: Dict[str, Any]
      })
      expect(result.success).toBe(true)
      expect(result.data?.items[0].value).toBe(300)
      expect(result.data?.items[2].value).toBe(100)
    })
  })
  describe('validate', () => {
    it('should validate valid data', async () => {
      const data = { name: 'Test', value: 100 }
      const result = await service.validate(data)
      expect(result.isValid).toBe(true)
      expect(result.errors).toHaveLength(0)
    })
    it('should validate invalid data', async () => {
      const data = { name: '', value: 'invalid' as any }
      const result = await service.validate(data)
      expect(result.isValid).toBe(false)
      expect(result.errors).toHaveLength(2)
    })
  })
  describe('validateField', () => {
    it('should validate valid field value', async () => {
      const result = await service.validateField('name', 'Test')
      expect(result.isValid).toBe(true)
      expect(result.errors).toHaveLength(0)
    })
    it('should validate invalid field value', async () => {
      const result = await service.validateField('value', 'invalid')
      expect(result.isValid).toBe(false)
      expect(result.errors).toHaveLength(1)
    })
  })
})