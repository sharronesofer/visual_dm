/**
 * Cache Constants
 * @description Defines cache-related constants, TTL values, and configuration used throughout the application.
 */

/**
 * Cache Keys
 */
export const CACHE_KEYS = {
  /** User-related cache keys */
  USER: {
    PROFILE: 'user:profile',
    PREFERENCES: 'user:preferences',
    PERMISSIONS: 'user:permissions',
    SETTINGS: 'user:settings',
    SESSIONS: 'user:sessions',
  },

  /** Authentication-related cache keys */
  AUTH: {
    TOKEN: 'auth:token',
    REFRESH_TOKEN: 'auth:refresh_token',
    SESSION: 'auth:session',
    MFA_STATE: 'auth:mfa_state',
  },

  /** Application configuration cache keys */
  CONFIG: {
    SETTINGS: 'config:settings',
    FEATURES: 'config:features',
    THEMES: 'config:themes',
    LOCALES: 'config:locales',
  },

  /** API-related cache keys */
  API: {
    RESPONSES: 'api:responses',
    SCHEMAS: 'api:schemas',
    METADATA: 'api:metadata',
  },

  /** UI-related cache keys */
  UI: {
    LAYOUT: 'ui:layout',
    THEME: 'ui:theme',
    PREFERENCES: 'ui:preferences',
    STATE: 'ui:state',
  },

  // POI cache keys
  POI: {
    LIST: 'poi_list',
    DETAILS: (id: string) => `poi_${id}`,
    CATEGORIES: 'poi_categories',
    SEARCH: (query: string) => `poi_search_${query}`,
    NEARBY: (lat: number, lng: number) => `poi_nearby_${lat}_${lng}`,
  },

  // Character cache keys
  CHARACTER: {
    LIST: 'character_list',
    DETAILS: (id: string) => `character_${id}`,
    INVENTORY: (id: string) => `character_inventory_${id}`,
    SKILLS: (id: string) => `character_skills_${id}`,
    STATS: (id: string) => `character_stats_${id}`,
  },

  // Wizard cache keys
  WIZARD: {
    TEMPLATES: 'wizard_templates',
    STATE: (id: string) => `wizard_state_${id}`,
    STEP: (id: string, step: number) => `wizard_step_${id}_${step}`,
  },
} as const;

/**
 * Cache Time-To-Live (TTL) Values
 */
export const CACHE_TTL = {
  /** Very short TTL (30 seconds) */
  VERY_SHORT: 30 * 1000,

  /** Short TTL (5 minutes) */
  SHORT: 5 * 60 * 1000,

  /** Medium TTL (30 minutes) */
  MEDIUM: 30 * 60 * 1000,

  /** Long TTL (2 hours) */
  LONG: 2 * 60 * 60 * 1000,

  /** Very long TTL (8 hours) */
  VERY_LONG: 8 * 60 * 60 * 1000,

  /** Day-long TTL (24 hours) */
  DAY: 24 * 60 * 60 * 1000,

  /** Week-long TTL (7 days) */
  WEEK: 7 * 24 * 60 * 60 * 1000,

  /** Month-long TTL (30 days) */
  MONTH: 30 * 24 * 60 * 60 * 1000,
} as const;

/**
 * Cache Storage Types
 */
export const CACHE_STORAGE = {
  /** In-memory cache storage */
  MEMORY: 'memory',

  /** Local storage cache */
  LOCAL: 'local_storage',

  /** Session storage cache */
  SESSION: 'session_storage',

  /** IndexedDB cache storage */
  INDEXED_DB: 'indexed_db',

  /** Redis cache storage */
  REDIS: 'redis',

  /** Memcached cache storage */
  MEMCACHED: 'memcached',
} as const;

/**
 * Cache Policies
 */
export const CACHE_POLICIES = {
  /** Cache-first policy (check cache before network) */
  CACHE_FIRST: 'cache_first',

  /** Network-first policy (check network before cache) */
  NETWORK_FIRST: 'network_first',

  /** Cache-only policy (never check network) */
  CACHE_ONLY: 'cache_only',

  /** Network-only policy (never check cache) */
  NETWORK_ONLY: 'network_only',

  /** Stale-while-revalidate policy */
  STALE_WHILE_REVALIDATE: 'stale_while_revalidate',
} as const;

/**
 * Cache Configuration
 */
export const CACHE_CONFIG = {
  /** Default cache storage type */
  DEFAULT_STORAGE: CACHE_STORAGE.MEMORY,

  /** Default cache policy */
  DEFAULT_POLICY: CACHE_POLICIES.NETWORK_FIRST,

  /** Maximum cache size (in bytes) */
  MAX_SIZE: 50 * 1024 * 1024, // 50MB

  /** Maximum number of entries */
  MAX_ENTRIES: 1000,

  /** Cache version for migrations */
  VERSION: 1,

  /** Whether to enable debug logging */
  DEBUG: false,

  /** Whether to enable cache analytics */
  ANALYTICS: true,

  /** Cache compression settings */
  COMPRESSION: {
    ENABLED: true,
    MIN_SIZE: 1024, // Only compress items larger than 1KB
    LEVEL: 6, // Compression level (1-9)
  },

  /** Cache encryption settings */
  ENCRYPTION: {
    ENABLED: false,
    ALGORITHM: 'AES-256-GCM',
    KEY_SIZE: 256,
  },
} as const;

/**
 * Cache Events
 */
export const CACHE_EVENTS = {
  /** Item added to cache */
  ITEM_ADDED: 'cache:item_added',

  /** Item removed from cache */
  ITEM_REMOVED: 'cache:item_removed',

  /** Item updated in cache */
  ITEM_UPDATED: 'cache:item_updated',

  /** Item expired in cache */
  ITEM_EXPIRED: 'cache:item_expired',

  /** Cache cleared */
  CACHE_CLEARED: 'cache:cleared',

  /** Cache error occurred */
  ERROR: 'cache:error',
} as const;

/**
 * Cache Error Types
 */
export const CACHE_ERRORS = {
  /** Item not found in cache */
  NOT_FOUND: 'cache_not_found',

  /** Item expired in cache */
  EXPIRED: 'cache_expired',

  /** Cache storage full */
  STORAGE_FULL: 'cache_storage_full',

  /** Invalid cache key */
  INVALID_KEY: 'cache_invalid_key',

  /** Cache operation failed */
  OPERATION_FAILED: 'cache_operation_failed',

  /** Cache quota exceeded */
  QUOTA_EXCEEDED: 'cache_quota_exceeded',

  /** Cache version mismatch */
  VERSION_MISMATCH: 'cache_version_mismatch',
} as const;

/**
 * Cache Prefixes
 */
export const CACHE_PREFIXES = {
  API: 'api',
  UI: 'ui',
  USER: 'user',
  SYSTEM: 'system',
} as const;

/**
 * Cache Groups
 */
export const CACHE_GROUPS = {
  AUTH: 'auth',
  USER: 'user',
  POI: 'poi',
  CHARACTER: 'character',
  WIZARD: 'wizard',
  SYSTEM: 'system',
} as const;

/**
 * Cache Strategies
 */
export const CACHE_STRATEGIES = {
  // Cache first, then network
  CACHE_FIRST: 'cache-first',

  // Network first, then cache
  NETWORK_FIRST: 'network-first',

  // Cache only
  CACHE_ONLY: 'cache-only',

  // Network only
  NETWORK_ONLY: 'network-only',

  // Stale while revalidate
  STALE_WHILE_REVALIDATE: 'stale-while-revalidate',
} as const;

/**
 * Cache Size Limits
 */
export const CACHE_SIZE_LIMITS = {
  // Maximum number of items in memory cache
  MAX_ITEMS: 1000,

  // Maximum size of cached value (in bytes)
  MAX_VALUE_SIZE: 1024 * 1024, // 1MB

  // Maximum total cache size (in bytes)
  MAX_TOTAL_SIZE: 10 * 1024 * 1024, // 10MB
} as const;
