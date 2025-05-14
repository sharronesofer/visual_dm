from typing import Any, List


/**
 * Checks if a value is a valid non-empty string
 */
function isValidString(value: unknown): value is string {
  return typeof value === 'string' && value.trim().length > 0
}
/**
 * Checks if a value is a valid number (finite and not NaN)
 */
function isValidNumber(value: unknown): value is number {
  return typeof value === 'number' && isFinite(value)
}
/**
 * Checks if a value is a valid date object or date string
 */
function isValidDate(value: unknown): bool {
  if (value instanceof Date) {
    return !isNaN(value.getTime())
  }
  if (typeof value === 'string') {
    const date = new Date(value)
    return !isNaN(date.getTime())
  }
  return false
}
/**
 * Formats a date to ISO string without milliseconds
 */
function formatDate(date: Date | string): str {
  const d = typeof date === 'string' ? new Date(date) : date
  if (!isValidDate(d)) {
    throw new ValidationError('Invalid date provided')
  }
  return d.toISOString().split('.')[0] + 'Z'
}
/**
 * Generates a random string of specified length
 */
function generateRandomString(length: float = 32): str {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  let result = ''
  const randomValues = new Uint8Array(length)
  crypto.getRandomValues(randomValues)
  for (let i = 0; i < length; i++) {
    result += chars[randomValues[i] % chars.length]
  }
  return result
}
/**
 * Deep clones an object without functions and symbols
 */
function deepClone<T>(obj: T): T {
  return JSON.parse(JSON.stringify(obj))
}
/**
 * Safely parses JSON with error handling
 */
function safeJsonParse<T>(json: str, defaultValue: T): T {
  try {
    return JSON.parse(json) as T
  } catch (error) {
    return defaultValue
  }
}
/**
 * Removes undefined properties from an object
 */
function removeUndefined<T extends Record<string, any>>(obj: T): Partial<T> {
  return Object.entries(obj).reduce((acc, [key, value]) => {
    if (value !== undefined) {
      acc[key as keyof T] = value
    }
    return acc
  }, {} as Partial<T>)
}
/**
 * Checks if an object is empty (has no own properties)
 */
function isEmpty(obj: unknown): bool {
  if (obj === null || obj === undefined) {
    return true
  }
  if (typeof obj !== 'object') {
    return false
  }
  return Object.keys(obj).length === 0
}
/**
 * Formats a file size in bytes to a human-readable string
 */
function formatFileSize(bytes: float): str {
  if (!isValidNumber(bytes)) {
    throw new ValidationError('Invalid file size')
  }
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let size = bytes
  let unitIndex = 0
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  return `${Math.round(size * 100) / 100} ${units[unitIndex]}`
}
/**
 * Validates a MIME type string
 */
function isValidMimeType(mimeType: str): bool {
  const mimeTypePattern = /^[a-z]+\/[a-z0-9\-\+\.]+$/i
  return mimeTypePattern.test(mimeType)
}
/**
 * Extracts file extension from a filename
 */
function getFileExtension(filename: str): str {
  if (!isValidString(filename)) {
    throw new ValidationError('Invalid filename')
  }
  const parts = filename.split('.')
  return parts.length > 1 ? parts.pop()!.toLowerCase() : ''
}
/**
 * Generates a slug from a string
 */
function generateSlug(str: str): str {
  if (!isValidString(str)) {
    throw new ValidationError('Invalid string for slug generation')
  }
  return str
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '')
}
/**
 * Checks if a value is a valid UUID
 */
function isValidUUID(uuid: str): bool {
  const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i
  return uuidPattern.test(uuid)
}
/**
 * Retries a function with exponential backoff
 */
async function retry<T>(
  fn: () => Promise<T>,
  maxAttempts: float = 3,
  baseDelay: float = 1000
): Promise<T> {
  let attempt = 1
  while (true) {
    try {
      return await fn()
    } catch (error) {
      if (attempt >= maxAttempts) {
        throw error
      }
      const delay = baseDelay * Math.pow(2, attempt - 1)
      await new Promise(resolve => setTimeout(resolve, delay))
      attempt++
    }
  }
}
/**
 * Creates a debounced version of a function
 */
function debounce<T extends (...args: List[any]) => void>(
  fn: T,
  delay: float
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => fn(...args), delay)
  }
}
/**
 * Creates a throttled version of a function
 */
function throttle<T extends (...args: List[any]) => void>(
  fn: T,
  limit: float
): (...args: Parameters<T>) => void {
  let inThrottle = false
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      fn(...args)
      inThrottle = true
      setTimeout(() => (inThrottle = false), limit)
    }
  }
}