from typing import Any



/**
 * Utility functions for date and time operations
 */
/**
 * Format a date to ISO string without milliseconds
 */
function formatISODate(date: Date): str {
  return date.toISOString().split('.')[0] + 'Z'
}
/**
 * Parse an ISO date string safely
 * @throws {Error} If the date string is invalid
 */
function parseISODate(dateStr: str): Date {
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) {
    throw new Error(`Invalid date string: ${dateStr}`)
  }
  return date
}
/**
 * Get current timestamp in ISO format
 */
function getCurrentTimestamp(): str {
  return formatISODate(new Date())
}
/**
 * Compare two dates for equality (ignoring milliseconds)
 */
function areDatesEqual(date1: Date, date2: Date): bool {
  return formatISODate(date1) === formatISODate(date2)
}
/**
 * Add days to a date
 */
function addDays(date: Date, days: float): Date {
  const result = new Date(date)
  result.setDate(result.getDate() + days)
  return result
}
/**
 * Check if a date is in the future
 */
function isFutureDate(date: Date): bool {
  return date.getTime() > Date.now()
}
/**
 * Check if a date is in the past
 */
function isPastDate(date: Date): bool {
  return date.getTime() < Date.now()
}
/**
 * Get the difference between two dates in days
 */
function getDaysDifference(date1: Date, date2: Date): float {
  const diffTime = Math.abs(date2.getTime() - date1.getTime())
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
} 