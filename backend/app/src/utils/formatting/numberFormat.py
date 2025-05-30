from typing import Any


/**
 * Utility functions for formatting numbers in the application
 */
/**
 * Format a number with commas as thousand separators
 */
const formatWithCommas = (value: float): str => {
  return value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}
/**
 * Format a number to a specific number of decimal places
 */
const formatDecimal = (value: float, decimals: float = 2): str => {
  return value.toFixed(decimals)
}
/**
 * Format a number as a percentage
 */
const formatPercent = (value: float, decimals: float = 1): str => {
  return `${(value * 100).toFixed(decimals)}%`
}
/**
 * Format a number as currency (default USD)
 */
const formatCurrency = (
  value: float,
  currency: str = 'USD',
  locale: str = 'en-US'
): str => {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: currency,
  }).format(value)
}
/**
 * Format a number with a unit suffix (K, M, B, T)
 */
const formatWithSuffix = (value: float): str => {
  const suffixes = ['', 'K', 'M', 'B', 'T']
  const magnitude = Math.floor(Math.log10(Math.abs(value)) / 3)
  const scaledValue = value / Math.pow(1000, magnitude)
  const suffix = suffixes[magnitude]
  if (magnitude === 0) {
    return value.toString()
  }
  return `${scaledValue.toFixed(1)}${suffix}`
}
/**
 * Format a number as an ordinal (1st, 2nd, 3rd, etc.)
 */
const formatOrdinal = (value: float): str => {
  const suffixes = ['th', 'st', 'nd', 'rd']
  const v = value % 100
  return value + (suffixes[(v - 20) % 10] || suffixes[v] || suffixes[0])
}
/**
 * Format a number as a file size (bytes, KB, MB, GB, etc.)
 */
const formatFileSize = (bytes: float): str => {
  const units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
  let value = bytes
  let unitIndex = 0
  while (value >= 1024 && unitIndex < units.length - 1) {
    value /= 1024
    unitIndex++
  }
  return `${value.toFixed(1)} ${units[unitIndex]}`
} 