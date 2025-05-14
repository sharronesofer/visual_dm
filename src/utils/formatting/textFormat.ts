/**
 * Utility functions for formatting text in the application
 */

/**
 * Capitalize the first letter of a string
 */
export const capitalizeFirst = (text: string): string => {
  if (!text) return text;
  return text.charAt(0).toUpperCase() + text.slice(1);
};

/**
 * Convert a string to title case
 */
export const toTitleCase = (text: string): string => {
  if (!text) return text;
  return text
    .toLowerCase()
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

/**
 * Truncate text to a maximum length with ellipsis
 */
export const truncate = (text: string, maxLength: number): string => {
  if (!text || text.length <= maxLength) return text;
  return text.slice(0, maxLength - 3) + '...';
};

/**
 * Convert camelCase to kebab-case
 */
export const camelToKebab = (text: string): string => {
  return text.replace(/([a-z0-9])([A-Z])/g, '$1-$2').toLowerCase();
};

/**
 * Convert kebab-case to camelCase
 */
export const kebabToCamel = (text: string): string => {
  return text.replace(/-([a-z])/g, g => g[1].toUpperCase());
};

/**
 * Convert a string to snake_case
 */
export const toSnakeCase = (text: string): string => {
  return text
    .replace(/([a-z])([A-Z])/g, '$1_$2')
    .replace(/[\s-]+/g, '_')
    .toLowerCase();
};

/**
 * Strip HTML tags from a string
 */
export const stripHtml = (html: string): string => {
  const tmp = document.createElement('div');
  tmp.innerHTML = html;
  return tmp.textContent || tmp.innerText || '';
};

/**
 * Format a string as a slug (URL-friendly string)
 */
export const slugify = (text: string): string => {
  return text
    .toLowerCase()
    .replace(/[^\w\s-]/g, '') // Remove special characters
    .replace(/[\s_-]+/g, '-') // Replace spaces and underscores with hyphens
    .replace(/^-+|-+$/g, ''); // Remove leading/trailing hyphens
};

/**
 * Add line breaks to text at a specified width
 */
export const wordWrap = (text: string, width: number): string => {
  const regex = new RegExp(`(?![^\\n]{1,${width}}$)([^\\n]{1,${width}})\\s`, 'g');
  return text.replace(regex, '$1\n');
};

/**
 * Format a phone number string
 */
export const formatPhoneNumber = (phone: string): string => {
  const cleaned = phone.replace(/\D/g, '');
  const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/);
  if (match) {
    return '(' + match[1] + ') ' + match[2] + '-' + match[3];
  }
  return phone;
};

/**
 * Format text as a code block with syntax highlighting
 */
export const formatCodeBlock = (code: string, language: string = ''): string => {
  return `\`\`\`${language}\n${code}\n\`\`\``;
}; 