/**
 * Base interface for all entities
 */
export interface BaseEntity {
  id: string | number;
  createdAt?: Date;
  updatedAt?: Date;
  deletedAt?: Date | null;
}

/**
 * Base query parameters interface with enhanced filtering and sorting
 */
export interface BaseQueryParams {
  page?: number;
  limit?: number;
  sort?: string | string[];
  order?: 'asc' | 'desc' | ('asc' | 'desc')[];
  filter?: Record<string, any>;
  search?: string;
  include?: string[];
  fields?: string[];
}

/**
 * Service response interface with enhanced metadata
 */
export interface ServiceResponse<T> {
  success: boolean;
  data?: T;
  error?: Error;
  meta?: {
    total?: number;
    page?: number;
    limit?: number;
    [key: string]: any;
  };
}

/**
 * Bulk operation response interface
 */
export interface BulkOperationResponse<T> {
  successful: T[];
  failed: Array<{
    item: Partial<T>;
    error: Error;
  }>;
  totalProcessed: number;
  totalSuccessful: number;
  totalFailed: number;
}

// API types
export interface ApiResponse<T> {
  data: T;
  status: number;
  message?: string;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  total: number;
  page: number;
  limit: number;
}

// Error types
export interface ErrorResponse {
  message: string;
  code: string;
  details?: Record<string, unknown>;
}

// Config types
export interface AppConfig {
  apiUrl: string;
  wsUrl: string;
  environment: 'development' | 'staging' | 'production';
  version: string;
}

// Auth types
export interface User {
  id: string;
  email: string;
  username: string;
  role: 'admin' | 'user';
  createdAt: string;
  updatedAt: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface MediaAsset {
  id: string;
  filename: string;
  size: number;
  type: string;
  mimeType: string;
  thumbnailUrl: string | null;
  url: string;
  createdAt: string;
  updatedAt: string;
}

export type Theme = 'light' | 'dark';
