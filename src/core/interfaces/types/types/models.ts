import {
  Identifiable,
  Timestamped,
  SoftDeletable,
  Auditable,
  Versionable,
} from './common';

/**
 * Base entity interface that combines common entity properties
 */
export interface BaseEntity extends Identifiable, Timestamped {
  isActive: boolean;
}

/**
 * Extended base entity with soft delete and audit capabilities
 */
export interface FullEntity
  extends BaseEntity,
    SoftDeletable,
    Auditable,
    Versionable {}

/**
 * Generic model interface that can be used to create specific entity types
 */
export interface Model<T extends BaseEntity> {
  data: T;
  isDirty: boolean;
  isNew: boolean;
  changes: Partial<T>;
}

/**
 * Generic interface for one-to-one relationships
 */
export interface HasOne<T extends BaseEntity> {
  get(): Promise<T | null>;
  set(value: T | null): Promise<void>;
}

/**
 * Generic interface for one-to-many relationships
 */
export interface HasMany<T extends BaseEntity> {
  get(): Promise<T[]>;
  add(item: T): Promise<void>;
  remove(item: T): Promise<void>;
  set(items: T[]): Promise<void>;
}

/**
 * Generic interface for many-to-one relationships
 */
export interface BelongsTo<T extends BaseEntity> {
  get(): Promise<T | null>;
  set(value: T | null): Promise<void>;
}

/**
 * Generic interface for many-to-many relationships
 */
export interface BelongsToMany<T extends BaseEntity> {
  get(): Promise<T[]>;
  add(item: T): Promise<void>;
  remove(item: T): Promise<void>;
  set(items: T[]): Promise<void>;
}

/**
 * Interface for model metadata
 */
export interface ModelMetadata {
  tableName: string;
  primaryKey: string;
  timestamps: boolean;
  softDeletes: boolean;
  relations: {
    [key: string]: {
      type: 'hasOne' | 'hasMany' | 'belongsTo' | 'belongsToMany';
      model: string;
      foreignKey: string;
      localKey?: string;
    };
  };
}

/**
 * Type for model hooks
 */
export interface ModelHooks<T extends BaseEntity> {
  beforeCreate?: (data: Partial<T>) => Promise<void>;
  afterCreate?: (model: Model<T>) => Promise<void>;
  beforeUpdate?: (model: Model<T>) => Promise<void>;
  afterUpdate?: (model: Model<T>) => Promise<void>;
  beforeDelete?: (model: Model<T>) => Promise<void>;
  afterDelete?: (model: Model<T>) => Promise<void>;
}

/**
 * Interface for model validation rules
 */
export interface ValidationRules {
  [key: string]: {
    type: string;
    required?: boolean;
    min?: number;
    max?: number;
    pattern?: RegExp;
    custom?: (value: any) => boolean | Promise<boolean>;
  };
}

/**
 * Type for model query builders
 */
export interface QueryBuilder<T extends BaseEntity> {
  where(field: keyof T, value: any): QueryBuilder<T>;
  whereIn(field: keyof T, values: any[]): QueryBuilder<T>;
  whereBetween(field: keyof T, range: [any, any]): QueryBuilder<T>;
  orderBy(field: keyof T, direction?: 'asc' | 'desc'): QueryBuilder<T>;
  limit(count: number): QueryBuilder<T>;
  offset(count: number): QueryBuilder<T>;
  include(relation: string): QueryBuilder<T>;
  get(): Promise<T[]>;
  first(): Promise<T | null>;
  count(): Promise<number>;
}

/**
 * User entity type
 */
export interface User extends BaseEntity {
  username: string;
  email: string;
  passwordHash: string;
  roles: string[];
  isVerified: boolean;
  profile?: UserProfile;
}

/**
 * User profile entity type
 */
export interface UserProfile extends BaseEntity {
  userId: string;
  firstName: string;
  lastName: string;
  avatarUrl?: string;
  bio?: string;
}

/**
 * Product entity type
 */
export interface Product extends BaseEntity {
  name: string;
  description: string;
  price: number;
  currency: string;
  inStock: boolean;
  categories: string[];
  images: string[];
}

/**
 * Order entity type
 */
export interface Order extends BaseEntity {
  userId: string;
  items: OrderItem[];
  total: number;
  status: 'pending' | 'paid' | 'shipped' | 'delivered' | 'cancelled';
  placedAt: Date;
  shippedAt?: Date;
  deliveredAt?: Date;
}

/**
 * Order item entity type
 */
export interface OrderItem {
  productId: string;
  quantity: number;
  price: number;
}
