from typing import Any



  formatDate,
  formatISODate,
  formatRelativeTime,
  formatTime,
  formatDuration,
  formatDateRange,
  getWeekNumber,
  formatDateWithDay
} from '../dateFormat'
describe('Date Formatting Utilities', () => {
  const testDate = new Date('2024-03-15T14:30:00Z')
  const testEndDate = new Date('2024-03-20T14:30:00Z')
  describe('formatDate', () => {
    it('should format date with default options', () => {
      expect(formatDate(testDate)).toMatch(/March 15, 2024/)
    })
    it('should format date with custom locale', () => {
      expect(formatDate(testDate, 'de-DE')).toMatch(/15. März 2024/)
    })
    it('should format date with custom options', () => {
      expect(formatDate(testDate, 'en-US', { month: 'short', year: '2-digit' }))
        .toMatch(/Mar '24/)
    })
  })
  describe('formatISODate', () => {
    it('should format date to ISO format', () => {
      expect(formatISODate(testDate)).toBe('2024-03-15')
    })
    it('should handle string input', () => {
      expect(formatISODate('2024-03-15T14:30:00Z')).toBe('2024-03-15')
    })
  })
  describe('formatRelativeTime', () => {
    it('should format relative time', () => {
      const now = new Date()
      const fiveMinutesAgo = new Date(now.getTime() - 5 * 60 * 1000)
      expect(formatRelativeTime(fiveMinutesAgo)).toBe('5 minutes ago')
    })
    it('should handle just now', () => {
      const now = new Date()
      expect(formatRelativeTime(now)).toBe('just now')
    })
    it('should handle different time units', () => {
      const now = new Date()
      const oneDayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000)
      expect(formatRelativeTime(oneDayAgo)).toBe('1 day ago')
    })
  })
  describe('formatTime', () => {
    it('should format time in 12-hour format', () => {
      expect(formatTime(testDate)).toMatch(/2:30 PM/)
    })
    it('should format time with custom locale', () => {
      expect(formatTime(testDate, 'de-DE')).toMatch(/14:30/)
    })
  })
  describe('formatDuration', () => {
    it('should format duration in days and hours', () => {
      expect(formatDuration(90 * 60 * 60 * 1000)).toBe('3d 18h')
    })
    it('should format duration in hours and minutes', () => {
      expect(formatDuration(90 * 60 * 1000)).toBe('1h 30m')
    })
    it('should format duration in minutes and seconds', () => {
      expect(formatDuration(90 * 1000)).toBe('1m 30s')
    })
    it('should format duration in seconds', () => {
      expect(formatDuration(45 * 1000)).toBe('45s')
    })
  })
  describe('formatDateRange', () => {
    it('should format date range in same year', () => {
      const result = formatDateRange(testDate, testEndDate)
      expect(result).toMatch(/March 15 - March 20, 2024/)
    })
    it('should format date range in different years', () => {
      const nextYear = new Date(testEndDate)
      nextYear.setFullYear(nextYear.getFullYear() + 1)
      const result = formatDateRange(testDate, nextYear)
      expect(result).toMatch(/March 15, 2024 - March 20, 2025/)
    })
    it('should format same day', () => {
      const result = formatDateRange(testDate, testDate)
      expect(result).toMatch(/March 15, 2024/)
    })
  })
  describe('getWeekNumber', () => {
    it('should return correct week number', () => {
      expect(getWeekNumber(new Date('2024-01-01'))).toBe(1)
      expect(getWeekNumber(new Date('2024-12-31'))).toBe(53)
    })
  })
  describe('formatDateWithDay', () => {
    it('should format date with day of week', () => {
      expect(formatDateWithDay(testDate)).toMatch(/Friday, March 15, 2024/)
    })
    it('should format date with custom locale', () => {
      expect(formatDateWithDay(testDate, 'de-DE')).toMatch(/Freitag, 15. März 2024/)
    })
  })
}) 