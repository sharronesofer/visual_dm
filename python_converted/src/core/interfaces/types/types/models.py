from typing import Any, List, Union


  Identifiable,
  Timestamped,
  SoftDeletable,
  Auditable,
  Versionable,
} from './common'
/**
 * Base entity interface that combines common entity properties
 */
interface BaseEntity extends Identifiable, Timestamped {
  isActive: bool
}
/**
 * Extended base entity with soft delete and audit capabilities
 */
interface FullEntity
  extends BaseEntity,
    SoftDeletable,
    Auditable,
    Versionable {}
/**
 * Generic model interface that can be used to create specific entity types
 */
interface Model<T extends BaseEntity> {
  data: T
  isDirty: bool
  isNew: bool
  changes: Partial<T>
}
/**
 * Generic interface for one-to-one relationships
 */
interface HasOne<T extends BaseEntity> {
  get(): Promise<T | null>
  set(value: T | null): Promise<void>
}
/**
 * Generic interface for one-to-many relationships
 */
interface HasMany<T extends BaseEntity> {
  get(): Promise<T[]>
  add(item: T): Promise<void>
  remove(item: T): Promise<void>
  set(items: List[T]): Promise<void>
}
/**
 * Generic interface for many-to-one relationships
 */
interface BelongsTo<T extends BaseEntity> {
  get(): Promise<T | null>
  set(value: T | null): Promise<void>
}
/**
 * Generic interface for many-to-many relationships
 */
interface BelongsToMany<T extends BaseEntity> {
  get(): Promise<T[]>
  add(item: T): Promise<void>
  remove(item: T): Promise<void>
  set(items: List[T]): Promise<void>
}
/**
 * Interface for model metadata
 */
class ModelMetadata:
    tableName: str
    primaryKey: str
    timestamps: bool
    softDeletes: bool
    relations: Union[{
    [key: str]: {
      type: 'hasOne', 'hasMAny', 'belongsTo', 'belongsToMAny']
    model: str
    foreignKey: str
    localKey?: str
  }
}
/**
 * Type for model hooks
 */
interface ModelHooks<T extends BaseEntity> {
  beforeCreate?: (data: Partial<T>) => Promise<void>
  afterCreate?: (model: Model<T>) => Promise<void>
  beforeUpdate?: (model: Model<T>) => Promise<void>
  afterUpdate?: (model: Model<T>) => Promise<void>
  beforeDelete?: (model: Model<T>) => Promise<void>
  afterDelete?: (model: Model<T>) => Promise<void>
}
/**
 * Interface for model validation rules
 */
class ValidationRules:
    [key: str]: {
    type: str
    required?: bool
    min?: float
    max?: float
    pattern?: RegExp
    custom?: Union[(value: Any) => bool, Awaitable[bool>]
}
/**
 * Type for model query builders
 */
interface QueryBuilder<T extends BaseEntity> {
  where(field: keyof T, value: Any): QueryBuilder<T>
  whereIn(field: keyof T, values: List[any]): QueryBuilder<T>
  whereBetween(field: keyof T, range: [any, any]): QueryBuilder<T>
  orderBy(field: keyof T, direction?: 'asc' | 'desc'): QueryBuilder<T>
  limit(count: float): QueryBuilder<T>
  offset(count: float): QueryBuilder<T>
  include(relation: str): QueryBuilder<T>
  get(): Promise<T[]>
  first(): Promise<T | null>
  count(): Promise<number>
}
/**
 * User entity type
 */
class User:
    username: str
    email: str
    passwordHash: str
    roles: List[str]
    isVerified: bool
    profile?: \'UserProfile\'
/**
 * User profile entity type
 */
class UserProfile:
    userId: str
    firstName: str
    lastName: str
    avatarUrl?: str
    bio?: str
/**
 * Product entity type
 */
class Product:
    name: str
    description: str
    price: float
    currency: str
    inStock: bool
    categories: List[str]
    images: List[str]
/**
 * Order entity type
 */
class Order:
    userId: str
    items: List[OrderItem]
    total: float
    status: Union['pending', 'paid', 'shipped', 'delivered', 'cancelled']
    placedAt: Date
    shippedAt?: Date
    deliveredAt?: Date
/**
 * Order item entity type
 */
class OrderItem:
    productId: str
    quantity: float
    price: float