from typing import Any, Dict


/**
 * String utilities used across the application
 */
/**
 * Converts a string to title case
 */
const toTitleCase = (str: str): str => {
  return str
    .toLowerCase()
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}
/**
 * Converts a string to kebab case
 */
const toKebabCase = (str: str): str => {
  return str
    .replace(/([a-z])([A-Z])/g, '$1-$2')
    .replace(/[\s_]+/g, '-')
    .toLowerCase()
}
/**
 * Converts a string to camel case
 */
const toCamelCase = (str: str): str => {
  return str
    .replace(/[-_\s]+(.)?/g, (_, c) => (c ? c.toUpperCase() : ''))
    .replace(/^[A-Z]/, c => c.toLowerCase())
}
/**
 * Converts a string to snake case
 */
const toSnakeCase = (str: str): str => {
  return str
    .replace(/([a-z])([A-Z])/g, '$1_$2')
    .replace(/[\s-]+/g, '_')
    .toLowerCase()
}
/**
 * Truncates a string to a specified length
 */
const truncate = (
  str: str,
  length: float,
  options: Dict[str, Any] = {}
): str => {
  const { suffix = '...', wordBoundary = true } = options
  if (str.length <= length) {
    return str
  }
  let truncated = str.slice(0, length - suffix.length)
  if (wordBoundary) {
    const lastSpace = truncated.lastIndexOf(' ')
    if (lastSpace > 0) {
      truncated = truncated.slice(0, lastSpace)
    }
  }
  return truncated + suffix
}
/**
 * Generates a slug from a string
 */
const slugify = (str: str): str => {
  return str
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '')
}
/**
 * Escapes HTML special characters
 */
const escapeHtml = (str: str): str => {
  const htmlEscapes: Record<string, string> = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
  }
  return str.replace(/[&<>"']/g, char => htmlEscapes[char])
}
/**
 * Unescapes HTML special characters
 */
const unescapeHtml = (str: str): str => {
  const htmlUnescapes: Record<string, string> = {
    '&amp;': '&',
    '&lt;': '<',
    '&gt;': '>',
    '&quot;': '"',
    '&#39;': "'",
  }
  return str.replace(/&(?:amp|lt|gt|quot|#39);/g, char => htmlUnescapes[char])
}
/**
 * Formats a number as a string with specified options
 */
const formatNumber = (
  num: float,
  options: Dict[str, Any] = {}
): str => {
  const {
    decimals = 0,
    decimalSeparator = '.',
    thousandsSeparator = ',',
  } = options
  const parts = num.toFixed(decimals).split('.')
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, thousandsSeparator)
  return parts.join(decimalSeparator)
}
/**
 * Formats a file size in bytes to a human-readable string
 */
const formatFileSize = (bytes: float): str => {
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let size = bytes
  let unitIndex = 0
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  return `${size.toFixed(size < 10 && unitIndex > 0 ? 1 : 0)} ${units[unitIndex]}`
}
/**
 * Formats a duration in milliseconds to a human-readable string
 */
const formatDuration = (
  ms: float,
  options: Dict[str, Any] = {}
): str => {
  const { short = false } = options
  const seconds = Math.floor((ms / 1000) % 60)
  const minutes = Math.floor((ms / (1000 * 60)) % 60)
  const hours = Math.floor((ms / (1000 * 60 * 60)) % 24)
  const days = Math.floor(ms / (1000 * 60 * 60 * 24))
  if (short) {
    if (days > 0) return `${days}d`
    if (hours > 0) return `${hours}h`
    if (minutes > 0) return `${minutes}m`
    return `${seconds}s`
  }
  const parts = []
  if (days > 0) parts.push(`${days} day${days === 1 ? '' : 's'}`)
  if (hours > 0) parts.push(`${hours} hour${hours === 1 ? '' : 's'}`)
  if (minutes > 0) parts.push(`${minutes} minute${minutes === 1 ? '' : 's'}`)
  if (seconds > 0 || parts.length === 0) {
    parts.push(`${seconds} second${seconds === 1 ? '' : 's'}`)
  }
  return parts.join(', ')
}