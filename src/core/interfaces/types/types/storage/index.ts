/**
 * Storage types used across the application
 */

/** Configuration for autosave functionality */
export interface AutosaveConfig {
  key: string;
  debounceMs?: number;
  maxAge?: number; // Maximum age in milliseconds
  version?: string; // For handling data structure changes
}

/** Generic interface for stored data with metadata */
export interface StoredData<T> {
  data: T;
  timestamp: number;
  version: string;
}

/** Storage operation result */
export interface StorageResult<T> {
  success: boolean;
  data?: T;
  error?: string;
}

/** Storage provider interface */
export interface StorageProvider {
  get<T>(key: string): Promise<StorageResult<T>>;
  set<T>(key: string, value: T): Promise<StorageResult<void>>;
  remove(key: string): Promise<StorageResult<void>>;
  clear(): Promise<StorageResult<void>>;
}

/** Cache configuration */
export interface CacheConfig {
  maxSize?: number;
  maxAge?: number;
  version?: string;
}

/** Cache entry */
export interface CacheEntry<T> {
  value: T;
  timestamp: number;
  version: string;
}

/** Helper function to create an autosave configuration */
export const createAutosaveConfig = (
  key: string,
  options: Partial<Omit<AutosaveConfig, 'key'>> = {}
): AutosaveConfig => ({
  key,
  debounceMs: 1000,
  maxAge: 24 * 60 * 60 * 1000, // 24 hours
  version: '1.0',
  ...options,
});

/** Helper function to create stored data */
export const createStoredData = <T>(
  data: T,
  version: string = '1.0'
): StoredData<T> => ({
  data,
  timestamp: Date.now(),
  version,
});

/** Helper function to create a storage result */
export const createStorageResult = <T>(
  success: boolean,
  data?: T,
  error?: string
): StorageResult<T> => ({
  success,
  data,
  error,
});

/** Helper function to create a cache configuration */
export const createCacheConfig = (
  options: Partial<CacheConfig> = {}
): CacheConfig => ({
  maxSize: 100,
  maxAge: 60 * 60 * 1000, // 1 hour
  version: '1.0',
  ...options,
});

/** Helper function to create a cache entry */
export const createCacheEntry = <T>(
  value: T,
  version: string = '1.0'
): CacheEntry<T> => ({
  value,
  timestamp: Date.now(),
  version,
});
