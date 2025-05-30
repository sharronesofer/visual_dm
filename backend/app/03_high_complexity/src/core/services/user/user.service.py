from typing import Any, Dict



  ServiceResponse,
  ServiceConfig,
  PaginatedResponse,
  ValidationResult,
  QueryParams
} from '../../core/base/types/common'
  ValidatableService
} from '../../core/base/services'
const userValidationSchema = z.object({
  email: z.string().regex(EMAIL_REGEX, 'Invalid email format'),
  username: z.string().regex(USERNAME_REGEX, 'Invalid username format'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  firstName: z.string().optional(),
  lastName: z.string().optional(),
  role: z.enum(['user', 'admin']).optional().default('user'),
  isActive: z.boolean().optional().default(true),
})
UserValidationSchema = z.infer<typeof userValidationSchema>
/**
 * User service implementation with validation capabilities
 */
class UserService extends ValidatableService<User & BaseEntity> {
  protected validationRules: Map<keyof (User & BaseEntity), Record<string, any>> = new Map()
  constructor(config?: Partial<ServiceConfig>) {
    super(config)
    this.initializeValidationRules()
  }
  /**
   * Initialize validation rules based on Zod schema
   */
  private initializeValidationRules(): void {
    const shape = userValidationSchema.shape
    for (const [field, validator] of Object.entries(shape)) {
      this.validationRules.set(field as keyof (User & BaseEntity), {
        type: validator._def.typeName,
        ...validator._def
      })
    }
  }
  /**
   * Find user by email
   */
  async findByEmail(email: str): Promise<ServiceResponse<User & BaseEntity>> {
    try {
      const users = await this.findAll({ filter: Dict[str, Any] })
      const items = users.success && users.data ? users.data.items : []
      if (items.length > 0) {
        return {
          success: true,
          data: items[0]
        }
      }
      return {
        success: false,
        error: new Error('User not found')
      }
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error : new Error('Unknown error')
      }
    }
  }
  /**
   * Find user by username
   */
  async findByUsername(username: str): Promise<ServiceResponse<User & BaseEntity>> {
    try {
      const users = await this.findAll({ filter: Dict[str, Any] })
      const items = users.success && users.data ? users.data.items : []
      if (items.length > 0) {
        return {
          success: true,
          data: items[0]
        }
      }
      return {
        success: false,
        error: new Error('User not found')
      }
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error : new Error('Unknown error')
      }
    }
  }
  /**
   * Execute create operation
   */
  protected async executeCreate(data: Omit<User & BaseEntity, keyof BaseEntity>): Promise<User & BaseEntity> {
    throw new Error('Method not implemented.')
  }
  /**
   * Execute update operation
   */
  protected async executeUpdate(id: str, data: Partial<User & BaseEntity>): Promise<User & BaseEntity> {
    throw new Error('Method not implemented.')
  }
  /**
   * Execute delete operation
   */
  protected async executeDelete(id: str): Promise<void> {
    throw new Error('Method not implemented.')
  }
  /**
   * Execute find by ID operation
   */
  protected async executeFindById(id: str): Promise<User & BaseEntity | null> {
    throw new Error('Method not implemented.')
  }
  /**
   * Execute find one operation
   */
  protected async executeFindOne(params: QueryParams<User & BaseEntity>): Promise<User & BaseEntity | null> {
    throw new Error('Method not implemented.')
  }
  /**
   * Execute find all operation
   */
  protected async executeFindAll(params?: QueryParams<User & BaseEntity>): Promise<PaginatedResponse<User & BaseEntity>> {
    throw new Error('Method not implemented.')
  }
  /**
   * Execute validate operation
   */
  protected async executeValidate(data: Partial<User & BaseEntity>): Promise<ValidationResult> {
    try {
      await userValidationSchema.parseAsync(data)
      return { isValid: true, errors: [] }
    } catch (error) {
      if (error instanceof z.ZodError) {
        return {
          isValid: false,
          errors: error.errors.map(err => ({
            field: err.path.join('.'),
            message: err.message,
            code: 'VALIDATION_ERROR'
          }))
        }
      }
      return {
        isValid: false,
        errors: [{
          field: '*',
          message: 'Validation failed unexpectedly',
          code: 'VALIDATION_ERROR'
        }]
      }
    }
  }
  /**
   * Execute validate field operation
   */
  protected async executeValidateField(field: keyof (User & BaseEntity), value: Any): Promise<ValidationResult> {
    try {
      const fieldSchema = userValidationSchema.shape[field as keyof UserValidationSchema]
      if (!fieldSchema) {
        return {
          isValid: false,
          errors: [{
            field: String(field),
            message: 'Field does not exist in validation schema',
            code: 'VALIDATION_ERROR'
          }]
        }
      }
      await fieldSchema.parseAsync(value)
      return { isValid: true, errors: [] }
    } catch (error) {
      if (error instanceof z.ZodError) {
        return {
          isValid: false,
          errors: error.errors.map(err => ({
            field: String(field),
            message: err.message,
            code: 'VALIDATION_ERROR'
          }))
        }
      }
      return {
        isValid: false,
        errors: [{
          field: String(field),
          message: 'Field validation failed unexpectedly',
          code: 'VALIDATION_ERROR'
        }]
      }
    }
  }
  /**
   * Get default filterable fields
   */
  protected getDefaultFilterableFields(): Array<keyof (User & BaseEntity)> {
    return ['role', 'isActive', 'createdAt', 'updatedAt']
  }
  /**
   * Get default sortable fields
   */
  protected getDefaultSortableFields(): Array<keyof (User & BaseEntity)> {
    return ['email', 'username', 'createdAt', 'updatedAt']
  }
  /**
   * Apply validation rule
   */
  protected async applyValidationRule(
    field: keyof (User & BaseEntity),
    value: Any,
    ruleName: str,
    ruleConfig: Any
  ): Promise<boolean> {
    try {
      const result = await userValidationSchema.parseAsync({ [field]: value } as UserValidationSchema)
      return true
    } catch (error) {
      return false
    }
  }
  /**
   * Get validation error message
   */
  protected getValidationMessage(
    field: keyof (User & BaseEntity),
    ruleName: str,
    ruleConfig: Any
  ): str {
    const fieldSchema = userValidationSchema.shape[field as keyof UserValidationSchema]
    const errorMessage = (fieldSchema as any)?._def?.message
    if (errorMessage) {
      return errorMessage
    }
    return `Invalid value for field ${String(field)}`
  }
} 