from typing import Any



  formatISODate,
  parseISODate,
  getCurrentTimestamp,
  areDatesEqual,
  addDays,
  isFutureDate,
  isPastDate,
  getDaysDifference,
} from '../datetime'
describe('datetime utilities', () => {
  describe('formatISODate', () => {
    it('should format date to ISO string without milliseconds', () => {
      const date = new Date('2024-03-15T10:30:45.123Z')
      expect(formatISODate(date)).toBe('2024-03-15T10:30:45Z')
    })
  })
  describe('parseISODate', () => {
    it('should parse valid ISO date string', () => {
      const dateStr = '2024-03-15T10:30:45Z'
      const date = parseISODate(dateStr)
      expect(date).toBeInstanceOf(Date)
      expect(date.toISOString()).toMatch(/^2024-03-15T10:30:45/)
    })
    it('should throw error for invalid date string', () => {
      expect(() => parseISODate('invalid-date')).toThrow('Invalid date string')
    })
  })
  describe('getCurrentTimestamp', () => {
    it('should return current timestamp in ISO format', () => {
      const timestamp = getCurrentTimestamp()
      expect(timestamp).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/)
    })
  })
  describe('areDatesEqual', () => {
    it('should return true for equal dates', () => {
      const date1 = new Date('2024-03-15T10:30:45.123Z')
      const date2 = new Date('2024-03-15T10:30:45.456Z')
      expect(areDatesEqual(date1, date2)).toBe(true)
    })
    it('should return false for different dates', () => {
      const date1 = new Date('2024-03-15T10:30:45Z')
      const date2 = new Date('2024-03-15T10:30:46Z')
      expect(areDatesEqual(date1, date2)).toBe(false)
    })
  })
  describe('addDays', () => {
    it('should add days to date', () => {
      const date = new Date('2024-03-15T10:30:45Z')
      const result = addDays(date, 5)
      expect(result.toISOString()).toMatch(/^2024-03-20/)
    })
    it('should handle negative days', () => {
      const date = new Date('2024-03-15T10:30:45Z')
      const result = addDays(date, -5)
      expect(result.toISOString()).toMatch(/^2024-03-10/)
    })
  })
  describe('isFutureDate', () => {
    it('should return true for future date', () => {
      const futureDate = addDays(new Date(), 1)
      expect(isFutureDate(futureDate)).toBe(true)
    })
    it('should return false for past date', () => {
      const pastDate = addDays(new Date(), -1)
      expect(isFutureDate(pastDate)).toBe(false)
    })
  })
  describe('isPastDate', () => {
    it('should return true for past date', () => {
      const pastDate = addDays(new Date(), -1)
      expect(isPastDate(pastDate)).toBe(true)
    })
    it('should return false for future date', () => {
      const futureDate = addDays(new Date(), 1)
      expect(isPastDate(futureDate)).toBe(false)
    })
  })
  describe('getDaysDifference', () => {
    it('should calculate days between dates', () => {
      const date1 = new Date('2024-03-15T10:30:45Z')
      const date2 = new Date('2024-03-20T10:30:45Z')
      expect(getDaysDifference(date1, date2)).toBe(5)
    })
    it('should handle negative differences', () => {
      const date1 = new Date('2024-03-20T10:30:45Z')
      const date2 = new Date('2024-03-15T10:30:45Z')
      expect(getDaysDifference(date1, date2)).toBe(5)
    })
  })
}) 