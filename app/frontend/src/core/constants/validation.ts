/**
 * Validation Constants
 * @description Defines validation patterns, constraints, and error messages used throughout the application.
 */

/**
 * Regular Expression Patterns
 */
export const VALIDATION_PATTERNS = {
  /** Email validation pattern */
  EMAIL: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,

  /** Phone number validation pattern (international format) */
  PHONE: /^\+?[1-9]\d{1,14}$/,

  /** URL validation pattern */
  URL: /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([/\w .-]*)*\/?$/,

  /** Username validation pattern (alphanumeric, underscores, 3-20 chars) */
  USERNAME: /^[a-zA-Z0-9_]{3,20}$/,

  /** Password validation pattern (min 12 chars, at least one number, one letter) */
  PASSWORD: /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{12,}$/,

  /** Date validation pattern (YYYY-MM-DD) */
  DATE: /^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$/,

  /** Time validation pattern (HH:mm:ss) */
  TIME: /^([01]\d|2[0-3]):([0-5]\d):([0-5]\d)$/,

  /** IPv4 address validation pattern */
  IPV4: /^(\d{1,3}\.){3}\d{1,3}$/,

  /** Hexadecimal color code validation pattern */
  HEX_COLOR: /^#?([a-fA-F0-9]{6}|[a-fA-F0-9]{3})$/,

  /** Credit card number validation pattern */
  CREDIT_CARD: /^\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}$/,
} as const;

/**
 * Validation Constraints
 */
export const VALIDATION_CONSTRAINTS = {
  STRING: {
    MIN_LENGTH: 1,
    MAX_LENGTH: 255,
    LONG_TEXT_MAX: 5000,
  },

  NUMBER: {
    MIN_VALUE: Number.MIN_SAFE_INTEGER,
    MAX_VALUE: Number.MAX_SAFE_INTEGER,
    DECIMAL_PLACES: 2,
  },

  ARRAY: {
    MIN_LENGTH: 0,
    MAX_LENGTH: 100,
  },

  FILE: {
    MAX_SIZE: 10 * 1024 * 1024, // 10MB
    ALLOWED_TYPES: ['image/jpeg', 'image/png', 'image/gif', 'application/pdf'],
  },

  DATE: {
    MIN_YEAR: 1900,
    MAX_YEAR: 2100,
  },
} as const;

/**
 * Validation Error Messages
 */
export const VALIDATION_MESSAGES = {
  REQUIRED: 'This field is required',
  INVALID_EMAIL: 'Please enter a valid email address',
  INVALID_PHONE: 'Please enter a valid phone number',
  INVALID_URL: 'Please enter a valid URL',
  INVALID_USERNAME:
    'Username must be 3-20 characters long and contain only letters, numbers, and underscores',
  INVALID_PASSWORD:
    'Password must be at least 12 characters long and contain at least one letter and one number',
  INVALID_DATE: 'Please enter a valid date in YYYY-MM-DD format',
  INVALID_TIME: 'Please enter a valid time in HH:mm:ss format',
  INVALID_IP: 'Please enter a valid IPv4 address',
  INVALID_COLOR: 'Please enter a valid hexadecimal color code',
  INVALID_CREDIT_CARD: 'Please enter a valid credit card number',

  STRING: {
    TOO_SHORT: (min: number) => `Must be at least ${min} characters long`,
    TOO_LONG: (max: number) => `Must be no more than ${max} characters long`,
  },

  NUMBER: {
    TOO_SMALL: (min: number) => `Must be at least ${min}`,
    TOO_LARGE: (max: number) => `Must be no more than ${max}`,
    INVALID_DECIMAL: (places: number) =>
      `Must have no more than ${places} decimal places`,
  },

  ARRAY: {
    TOO_SHORT: (min: number) => `Must have at least ${min} items`,
    TOO_LONG: (max: number) => `Must have no more than ${max} items`,
  },

  FILE: {
    TOO_LARGE: (maxSize: number) =>
      `File size must not exceed ${maxSize / (1024 * 1024)}MB`,
    INVALID_TYPE: (types: string[]) =>
      `File type must be one of: ${types.join(', ')}`,
  },

  DATE: {
    INVALID_YEAR: (min: number, max: number) =>
      `Year must be between ${min} and ${max}`,
  },
} as const;

/**
 * Common Validation Rules
 */
export const VALIDATION_RULES = {
  REQUIRED: {
    required: true,
    message: VALIDATION_MESSAGES.REQUIRED,
  },

  EMAIL: {
    pattern: VALIDATION_PATTERNS.EMAIL,
    message: VALIDATION_MESSAGES.INVALID_EMAIL,
  },

  PHONE: {
    pattern: VALIDATION_PATTERNS.PHONE,
    message: VALIDATION_MESSAGES.INVALID_PHONE,
  },

  URL: {
    pattern: VALIDATION_PATTERNS.URL,
    message: VALIDATION_MESSAGES.INVALID_URL,
  },

  USERNAME: {
    pattern: VALIDATION_PATTERNS.USERNAME,
    message: VALIDATION_MESSAGES.INVALID_USERNAME,
  },

  PASSWORD: {
    pattern: VALIDATION_PATTERNS.PASSWORD,
    message: VALIDATION_MESSAGES.INVALID_PASSWORD,
  },

  DATE: {
    pattern: VALIDATION_PATTERNS.DATE,
    message: VALIDATION_MESSAGES.INVALID_DATE,
  },

  TIME: {
    pattern: VALIDATION_PATTERNS.TIME,
    message: VALIDATION_MESSAGES.INVALID_TIME,
  },

  IPV4: {
    pattern: VALIDATION_PATTERNS.IPV4,
    message: VALIDATION_MESSAGES.INVALID_IP,
  },

  HEX_COLOR: {
    pattern: VALIDATION_PATTERNS.HEX_COLOR,
    message: VALIDATION_MESSAGES.INVALID_COLOR,
  },

  CREDIT_CARD: {
    pattern: VALIDATION_PATTERNS.CREDIT_CARD,
    message: VALIDATION_MESSAGES.INVALID_CREDIT_CARD,
  },
} as const;

/**
 * Common Field Length Constraints
 */
export const LENGTH_CONSTRAINTS = {
  USERNAME: {
    MIN: 3,
    MAX: 20,
  },
  PASSWORD: {
    MIN: 8,
    MAX: 128,
  },
  NAME: {
    MIN: 2,
    MAX: 50,
  },
  TITLE: {
    MIN: 3,
    MAX: 100,
  },
  DESCRIPTION: {
    MIN: 10,
    MAX: 500,
  },
  COMMENT: {
    MIN: 1,
    MAX: 1000,
  },
  URL: {
    MAX: 2048,
  },
  EMAIL: {
    MAX: 254,
  },
  PHONE: {
    MIN: 10,
    MAX: 15,
  },
} as const;

/**
 * Common Numeric Constraints
 */
export const NUMERIC_CONSTRAINTS = {
  AGE: {
    MIN: 0,
    MAX: 150,
  },
  RATING: {
    MIN: 0,
    MAX: 5,
  },
  PERCENTAGE: {
    MIN: 0,
    MAX: 100,
  },
  QUANTITY: {
    MIN: 0,
    MAX: 9999,
  },
  PRICE: {
    MIN: 0,
    MAX: 999999.99,
  },
} as const;

/**
 * Common File Constraints
 */
export const FILE_CONSTRAINTS = {
  IMAGE: {
    MAX_SIZE: 5 * 1024 * 1024, // 5MB
    ALLOWED_TYPES: ['image/jpeg', 'image/png', 'image/gif'],
    MAX_WIDTH: 4096,
    MAX_HEIGHT: 4096,
  },
  DOCUMENT: {
    MAX_SIZE: 10 * 1024 * 1024, // 10MB
    ALLOWED_TYPES: [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    ],
  },
  AVATAR: {
    MAX_SIZE: 1 * 1024 * 1024, // 1MB
    ALLOWED_TYPES: ['image/jpeg', 'image/png'],
    MAX_WIDTH: 512,
    MAX_HEIGHT: 512,
  },
} as const;

/**
 * Common Date Constraints
 */
export const DATE_CONSTRAINTS = {
  MIN_DATE: '1900-01-01',
  MAX_DATE: '2100-12-31',
  MIN_AGE: 13, // For user registration
  MAX_AGE: 120,
} as const;

/**
 * Common Character Constraints
 */
export const CHARACTER_CONSTRAINTS = {
  ALLOWED_SPECIAL_CHARS: '!@#$%^&*()_+-=[]{}|;:,.<>?',
  FORBIDDEN_CHARS: '<>{}[]\\',
  MAX_CONSECUTIVE_CHARS: 3,
} as const;
