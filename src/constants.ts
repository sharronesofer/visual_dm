export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  REQUEST_TIMEOUT: 408,
  TOO_MANY_REQUESTS: 429,
  INTERNAL_SERVER_ERROR: 500,
  BAD_GATEWAY: 502,
  SERVICE_UNAVAILABLE: 503,
  GATEWAY_TIMEOUT: 504,
  UNPROCESSABLE_ENTITY: 422
} as const;

// API Configuration
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
export const AUTH_HEADER = 'Authorization';
export const TOKEN_KEY = 'auth_token';

// API Cache Configuration
export const DEFAULT_CACHE_TTL = 5 * 60 * 1000; // 5 minutes
export const MAX_CACHE_SIZE = 100;

// Request Batching Configuration
export const MAX_BATCH_SIZE = 10;
export const MAX_BATCH_WAIT_TIME = 50; // milliseconds

// API Response Compression
export const COMPRESSION_THRESHOLD = 1024; // bytes

export const CACHE_CONFIG = {
  ttl: DEFAULT_CACHE_TTL,
  maxSize: MAX_CACHE_SIZE,
  MAX_ITEMS: 1000,
  CHECK_PERIOD: 600,
  PRUNE_THRESHOLD: 0.8,
  NAMESPACE: 'visual-dm'
};

export const API_CONFIG = {
  baseUrl: API_BASE_URL,
  TIMEOUT: 30000,
  MAX_RETRIES: 3,
  MAX_PAYLOAD_SIZE: 5 * 1024 * 1024,
  SUPPORTED_CONTENT_TYPES: ['application/json']
};

export const API_VERSION = 'v1';
export const API_PREFIX = '/api';
export const ENDPOINTS = {
  AUTH: { LOGIN: '/api/v1/auth/login' },
  USER: { PROFILE: '/api/v1/user/profile' },
  MESSAGES: { SEND: '/api/v1/messages/send' },
  CONVERSATIONS: { CREATE: '/api/v1/conversations/create' }
};

export const VALIDATION_PATTERNS = {
  EMAIL: /^[^@\s]+@[^@\s]+\.[^@\s]+$/,
  PASSWORD: /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{12,}$/,
  USERNAME: /^[a-zA-Z0-9_]{3,}$/
};

export const VALIDATION_CONSTRAINTS = {
  USERNAME: { MIN_LENGTH: 3 },
  PASSWORD: { MIN_SPECIAL_CHARS: 1 },
  MESSAGE: { MAX_LENGTH: 5000 }
};

export const VALIDATION_MESSAGES = {
  REQUIRED: 'This field is required',
  INVALID_EMAIL: 'Please enter a valid email address'
};

export const ERROR_CODES = {
  INVALID_CREDENTIALS: 1001,
  TOKEN_EXPIRED: 1002,
  INSUFFICIENT_PERMISSIONS: 2001,
  INVALID_INPUT: 3001
};

export const ERROR_MESSAGES = {
  [ERROR_CODES.INVALID_CREDENTIALS]: 'Invalid username or password',
  [ERROR_CODES.TOKEN_EXPIRED]: 'Authentication token has expired',
  [ERROR_CODES.INSUFFICIENT_PERMISSIONS]: 'Insufficient permissions',
  [ERROR_CODES.INVALID_INPUT]: 'Invalid input provided'
};

export const CACHE_KEYS = {
  USER: { PROFILE: 'user:profile:' },
  MESSAGE: { THREAD: 'message:thread:' },
  CONVERSATION: { DETAILS: 'conversation:details:' }
};

export const CACHE_TTL = {
  SHORT: 60,
  MEDIUM: 300,
  LONG: 3600,
  VERY_LONG: 86400
}; 