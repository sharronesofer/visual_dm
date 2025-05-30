from typing import Any, Dict, List


/**
 * Validation Constants
 * @description Defines validation patterns, constraints, and error messages used throughout the application.
 */
/**
 * Regular Expression Patterns
 */
const VALIDATION_PATTERNS = {
  /** Email validation pattern */
  EMAIL: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
  /** Phone number validation pattern (international format) */
  PHONE: /^\+?[1-9]\d{1,14}$/,
  /** URL validation pattern */
  URL: /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([/\w .-]*)*\/?$/,
  /** Username validation pattern (alphanumeric, underscores, 3-20 chars) */
  USERNAME: /^[a-zA-Z0-9_]{3,20}$/,
  /** Password validation pattern (min 8 chars, at least one number, one letter) */
  PASSWORD: /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$/,
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
} as const
/**
 * Validation Constraints
 */
const VALIDATION_CONSTRAINTS = {
  STRING: Dict[str, Any],
  NUMBER: Dict[str, Any],
  ARRAY: Dict[str, Any],
  FILE: Dict[str, Any],
  DATE: Dict[str, Any],
} as const
/**
 * Validation Error Messages
 */
const VALIDATION_MESSAGES = {
  REQUIRED: 'This field is required',
  INVALID_EMAIL: 'Please enter a valid email address',
  INVALID_PHONE: 'Please enter a valid phone number',
  INVALID_URL: 'Please enter a valid URL',
  INVALID_USERNAME:
    'Username must be 3-20 characters long and contain only letters, numbers, and underscores',
  INVALID_PASSWORD:
    'Password must be at least 8 characters long and contain at least one letter and one number',
  INVALID_DATE: 'Please enter a valid date in YYYY-MM-DD format',
  INVALID_TIME: 'Please enter a valid time in HH:mm:ss format',
  INVALID_IP: 'Please enter a valid IPv4 address',
  INVALID_COLOR: 'Please enter a valid hexadecimal color code',
  INVALID_CREDIT_CARD: 'Please enter a valid credit card number',
  STRING: Dict[str, Any] characters long`,
    TOO_LONG: (max: float) => `Must be no more than ${max} characters long`,
  },
  NUMBER: Dict[str, Any]`,
    TOO_LARGE: (max: float) => `Must be no more than ${max}`,
    INVALID_DECIMAL: (places: float) =>
      `Must have no more than ${places} decimal places`,
  },
  ARRAY: Dict[str, Any] items`,
    TOO_LONG: (max: float) => `Must have no more than ${max} items`,
  },
  FILE: Dict[str, Any]MB`,
    INVALID_TYPE: (types: List[string]) =>
      `File type must be one of: ${types.join(', ')}`,
  },
  DATE: Dict[str, Any] and ${max}`,
  },
} as const
/**
 * Common Validation Rules
 */
const VALIDATION_RULES = {
  REQUIRED: Dict[str, Any],
  EMAIL: Dict[str, Any],
  PHONE: Dict[str, Any],
  URL: Dict[str, Any],
  USERNAME: Dict[str, Any],
  PASSWORD: Dict[str, Any],
  DATE: Dict[str, Any],
  TIME: Dict[str, Any],
  IPV4: Dict[str, Any],
  HEX_COLOR: Dict[str, Any],
  CREDIT_CARD: Dict[str, Any],
} as const
/**
 * Common Field Length Constraints
 */
const LENGTH_CONSTRAINTS = {
  USERNAME: Dict[str, Any],
  PASSWORD: Dict[str, Any],
  NAME: Dict[str, Any],
  TITLE: Dict[str, Any],
  DESCRIPTION: Dict[str, Any],
  COMMENT: Dict[str, Any],
  URL: Dict[str, Any],
  EMAIL: Dict[str, Any],
  PHONE: Dict[str, Any],
} as const
/**
 * Common Numeric Constraints
 */
const NUMERIC_CONSTRAINTS = {
  AGE: Dict[str, Any],
  RATING: Dict[str, Any],
  PERCENTAGE: Dict[str, Any],
  QUANTITY: Dict[str, Any],
  PRICE: Dict[str, Any],
} as const
/**
 * Common File Constraints
 */
const FILE_CONSTRAINTS = {
  IMAGE: Dict[str, Any],
  DOCUMENT: Dict[str, Any],
  AVATAR: Dict[str, Any],
} as const
/**
 * Common Date Constraints
 */
const DATE_CONSTRAINTS = {
  MIN_DATE: '1900-01-01',
  MAX_DATE: '2100-12-31',
  MIN_AGE: 13, 
  MAX_AGE: 120,
} as const
/**
 * Common Character Constraints
 */
const CHARACTER_CONSTRAINTS = {
  ALLOWED_SPECIAL_CHARS: '!@#$%^&*()_+-=[]{}|;:,.<>?',
  FORBIDDEN_CHARS: '<>{}[]\\',
  MAX_CONSECUTIVE_CHARS: 3,
} as const