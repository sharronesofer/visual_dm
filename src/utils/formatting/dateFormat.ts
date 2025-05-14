/**
 * Utility functions for formatting dates in the application
 */

/**
 * Format a date to a localized string
 */
export const formatDate = (
  date: Date | string | number,
  locale: string = 'en-US',
  options: Intl.DateTimeFormatOptions = { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  }
): string => {
  const dateObj = new Date(date);
  return new Intl.DateTimeFormat(locale, options).format(dateObj);
};

/**
 * Format a date to ISO string (YYYY-MM-DD)
 */
export const formatISODate = (date: Date | string | number): string => {
  const dateObj = new Date(date);
  return dateObj.toISOString().split('T')[0];
};

/**
 * Format a date to a relative time string (e.g., "2 hours ago")
 */
export const formatRelativeTime = (date: Date | string | number): string => {
  const dateObj = new Date(date);
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - dateObj.getTime()) / 1000);

  const intervals = {
    year: 31536000,
    month: 2592000,
    week: 604800,
    day: 86400,
    hour: 3600,
    minute: 60,
    second: 1
  };

  for (const [unit, seconds] of Object.entries(intervals)) {
    const diff = Math.floor(diffInSeconds / seconds);
    if (diff >= 1) {
      return `${diff} ${unit}${diff > 1 ? 's' : ''} ago`;
    }
  }

  return 'just now';
};

/**
 * Format a date as time only (HH:MM AM/PM)
 */
export const formatTime = (
  date: Date | string | number,
  locale: string = 'en-US'
): string => {
  const dateObj = new Date(date);
  return dateObj.toLocaleTimeString(locale, {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  });
};

/**
 * Format a duration in milliseconds to a human-readable string
 */
export const formatDuration = (milliseconds: number): string => {
  const seconds = Math.floor(milliseconds / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (days > 0) {
    return `${days}d ${hours % 24}h`;
  } else if (hours > 0) {
    return `${hours}h ${minutes % 60}m`;
  } else if (minutes > 0) {
    return `${minutes}m ${seconds % 60}s`;
  } else {
    return `${seconds}s`;
  }
};

/**
 * Format a date range between two dates
 */
export const formatDateRange = (
  startDate: Date | string | number,
  endDate: Date | string | number,
  locale: string = 'en-US'
): string => {
  const start = new Date(startDate);
  const end = new Date(endDate);
  
  const sameYear = start.getFullYear() === end.getFullYear();
  const sameMonth = sameYear && start.getMonth() === end.getMonth();
  const sameDay = sameMonth && start.getDate() === end.getDate();

  if (sameDay) {
    return formatDate(start, locale);
  } else if (sameMonth) {
    return `${start.getDate()} - ${formatDate(end, locale)}`;
  } else if (sameYear) {
    return `${formatDate(start, locale, { month: 'short', day: 'numeric' })} - ${formatDate(end, locale)}`;
  } else {
    return `${formatDate(start, locale)} - ${formatDate(end, locale)}`;
  }
};

/**
 * Get the week number of a date
 */
export const getWeekNumber = (date: Date | string | number): number => {
  const dateObj = new Date(date);
  const firstDayOfYear = new Date(dateObj.getFullYear(), 0, 1);
  const pastDaysOfYear = (dateObj.getTime() - firstDayOfYear.getTime()) / 86400000;
  return Math.ceil((pastDaysOfYear + firstDayOfYear.getDay() + 1) / 7);
};

/**
 * Format a date to include day of week
 */
export const formatDateWithDay = (
  date: Date | string | number,
  locale: string = 'en-US'
): string => {
  const dateObj = new Date(date);
  return dateObj.toLocaleDateString(locale, {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
}; 