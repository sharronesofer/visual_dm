/**
 * Utility functions for formatting numbers in the application
 */

/**
 * Format a number with commas as thousand separators
 */
export const formatWithCommas = (value: number): string => {
  return value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
};

/**
 * Format a number to a specific number of decimal places
 */
export const formatDecimal = (value: number, decimals: number = 2): string => {
  return value.toFixed(decimals);
};

/**
 * Format a number as a percentage
 */
export const formatPercent = (value: number, decimals: number = 1): string => {
  return `${(value * 100).toFixed(decimals)}%`;
};

/**
 * Format a number as currency (default USD)
 */
export const formatCurrency = (
  value: number,
  currency: string = 'USD',
  locale: string = 'en-US'
): string => {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: currency,
  }).format(value);
};

/**
 * Format a number with a unit suffix (K, M, B, T)
 */
export const formatWithSuffix = (value: number): string => {
  const suffixes = ['', 'K', 'M', 'B', 'T'];
  const magnitude = Math.floor(Math.log10(Math.abs(value)) / 3);
  const scaledValue = value / Math.pow(1000, magnitude);
  const suffix = suffixes[magnitude];
  
  if (magnitude === 0) {
    return value.toString();
  }
  
  return `${scaledValue.toFixed(1)}${suffix}`;
};

/**
 * Format a number as an ordinal (1st, 2nd, 3rd, etc.)
 */
export const formatOrdinal = (value: number): string => {
  const suffixes = ['th', 'st', 'nd', 'rd'];
  const v = value % 100;
  return value + (suffixes[(v - 20) % 10] || suffixes[v] || suffixes[0]);
};

/**
 * Format a number as a file size (bytes, KB, MB, GB, etc.)
 */
export const formatFileSize = (bytes: number): string => {
  const units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB'];
  let value = bytes;
  let unitIndex = 0;

  while (value >= 1024 && unitIndex < units.length - 1) {
    value /= 1024;
    unitIndex++;
  }

  return `${value.toFixed(1)} ${units[unitIndex]}`;
}; 