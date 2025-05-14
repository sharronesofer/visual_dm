/**
 * Common type definitions used across the application
 */

/**
 * Generic ID type that can be either string or number
 */
export type ID = string | number;

/**
 * Generic type for pagination parameters
 */
export interface PaginationParams {
  page?: number;
  limit?: number;
  offset?: number;
}

/**
 * Generic type for sort parameters
 */
export interface SortParams {
  field: string;
  order: 'asc' | 'desc';
}

/**
 * Generic type for query filters
 */
export interface QueryFilters {
  [key: string]: string | number | boolean | Array<string | number> | null;
}

/**
 * Generic type for API response
 */
export interface ApiResponse<T> {
  data: T;
  meta?: {
    page?: number;
    limit?: number;
    total?: number;
    [key: string]: any;
  };
}

/**
 * Generic type for error response
 */
export interface ErrorResponse {
  code: string;
  message: string;
  details?: Record<string, any>;
}

/**
 * Type for file upload metadata
 */
export interface FileUploadMetadata {
  originalName: string;
  size: number;
  mimeType: string;
  encoding: string;
  [key: string]: any;
}

/**
 * Type for audit information
 */
export interface AuditInfo {
  createdBy?: string;
  createdAt: Date;
  updatedBy?: string;
  updatedAt: Date;
  version?: number;
}

/**
 * Type for geolocation coordinates
 */
export interface GeoCoordinates {
  latitude: number;
  longitude: number;
}

/**
 * Type for search parameters
 */
export interface SearchParams {
  query: string;
  filters?: QueryFilters;
  sort?: SortParams;
  pagination?: PaginationParams;
}

/**
 * Type for configuration options
 */
export interface ConfigOptions {
  [key: string]: string | number | boolean | null | ConfigOptions;
} 