/**
 * Utility functions for date and time operations
 */

/**
 * Format a date to ISO string without milliseconds
 */
export function formatISODate(date: Date): string {
  return date.toISOString().split('.')[0] + 'Z';
}

/**
 * Parse an ISO date string safely
 * @throws {Error} If the date string is invalid
 */
export function parseISODate(dateStr: string): Date {
  const date = new Date(dateStr);
  if (isNaN(date.getTime())) {
    throw new Error(`Invalid date string: ${dateStr}`);
  }
  return date;
}

/**
 * Get current timestamp in ISO format
 */
export function getCurrentTimestamp(): string {
  return formatISODate(new Date());
}

/**
 * Compare two dates for equality (ignoring milliseconds)
 */
export function areDatesEqual(date1: Date, date2: Date): boolean {
  return formatISODate(date1) === formatISODate(date2);
}

/**
 * Add days to a date
 */
export function addDays(date: Date, days: number): Date {
  const result = new Date(date);
  result.setDate(result.getDate() + days);
  return result;
}

/**
 * Check if a date is in the future
 */
export function isFutureDate(date: Date): boolean {
  return date.getTime() > Date.now();
}

/**
 * Check if a date is in the past
 */
export function isPastDate(date: Date): boolean {
  return date.getTime() < Date.now();
}

/**
 * Get the difference between two dates in days
 */
export function getDaysDifference(date1: Date, date2: Date): number {
  const diffTime = Math.abs(date2.getTime() - date1.getTime());
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
} 