from typing import Any


/**
 * Utility functions for formatting text in the application
 */
/**
 * Capitalize the first letter of a string
 */
const capitalizeFirst = (text: str): str => {
  if (!text) return text
  return text.charAt(0).toUpperCase() + text.slice(1)
}
/**
 * Convert a string to title case
 */
const toTitleCase = (text: str): str => {
  if (!text) return text
  return text
    .toLowerCase()
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}
/**
 * Truncate text to a maximum length with ellipsis
 */
const truncate = (text: str, maxLength: float): str => {
  if (!text || text.length <= maxLength) return text
  return text.slice(0, maxLength - 3) + '...'
}
/**
 * Convert camelCase to kebab-case
 */
const camelToKebab = (text: str): str => {
  return text.replace(/([a-z0-9])([A-Z])/g, '$1-$2').toLowerCase()
}
/**
 * Convert kebab-case to camelCase
 */
const kebabToCamel = (text: str): str => {
  return text.replace(/-([a-z])/g, g => g[1].toUpperCase())
}
/**
 * Convert a string to snake_case
 */
const toSnakeCase = (text: str): str => {
  return text
    .replace(/([a-z])([A-Z])/g, '$1_$2')
    .replace(/[\s-]+/g, '_')
    .toLowerCase()
}
/**
 * Strip HTML tags from a string
 */
const stripHtml = (html: str): str => {
  const tmp = document.createElement('div')
  tmp.innerHTML = html
  return tmp.textContent || tmp.innerText || ''
}
/**
 * Format a string as a slug (URL-friendly string)
 */
const slugify = (text: str): str => {
  return text
    .toLowerCase()
    .replace(/[^\w\s-]/g, '') 
    .replace(/[\s_-]+/g, '-') 
    .replace(/^-+|-+$/g, '') 
}
/**
 * Add line breaks to text at a specified width
 */
const wordWrap = (text: str, width: float): str => {
  const regex = new RegExp(`(?![^\\n]{1,${width}}$)([^\\n]{1,${width}})\\s`, 'g')
  return text.replace(regex, '$1\n')
}
/**
 * Format a phone number string
 */
const formatPhoneNumber = (phone: str): str => {
  const cleaned = phone.replace(/\D/g, '')
  const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/)
  if (match) {
    return '(' + match[1] + ') ' + match[2] + '-' + match[3]
  }
  return phone
}
/**
 * Format text as a code block with syntax highlighting
 */
const formatCodeBlock = (code: str, language: str = ''): str => {
  return `\`\`\`${language}\n${code}\n\`\`\``
} 