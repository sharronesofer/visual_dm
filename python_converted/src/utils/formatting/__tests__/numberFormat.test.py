from typing import Any


  formatWithCommas,
  formatDecimal,
  formatPercent,
  formatCurrency,
  formatWithSuffix,
  formatOrdinal,
  formatFileSize
} from '../numberFormat'
describe('Number Formatting Utilities', () => {
  describe('formatWithCommas', () => {
    it('should format numbers with commas', () => {
      expect(formatWithCommas(1000)).toBe('1,000')
      expect(formatWithCommas(1000000)).toBe('1,000,000')
      expect(formatWithCommas(1234567.89)).toBe('1,234,567.89')
    })
    it('should handle small numbers', () => {
      expect(formatWithCommas(100)).toBe('100')
      expect(formatWithCommas(0)).toBe('0')
    })
  })
  describe('formatDecimal', () => {
    it('should format to specified decimal places', () => {
      expect(formatDecimal(123.456, 2)).toBe('123.46')
      expect(formatDecimal(123.456, 1)).toBe('123.5')
      expect(formatDecimal(123.456, 0)).toBe('123')
    })
    it('should use default of 2 decimal places', () => {
      expect(formatDecimal(123.456)).toBe('123.46')
    })
  })
  describe('formatPercent', () => {
    it('should format numbers as percentages', () => {
      expect(formatPercent(0.1234)).toBe('12.3%')
      expect(formatPercent(0.1)).toBe('10.0%')
      expect(formatPercent(1)).toBe('100.0%')
    })
    it('should handle custom decimal places', () => {
      expect(formatPercent(0.1234, 2)).toBe('12.34%')
      expect(formatPercent(0.1, 0)).toBe('10%')
    })
  })
  describe('formatCurrency', () => {
    it('should format numbers as currency', () => {
      expect(formatCurrency(1234.56)).toMatch(/\$1,234.56/)
      expect(formatCurrency(1234.56, 'EUR', 'de-DE')).toMatch(/1.234,56/)
    })
    it('should handle negative numbers', () => {
      expect(formatCurrency(-1234.56)).toMatch(/-\$1,234.56/)
    })
  })
  describe('formatWithSuffix', () => {
    it('should format numbers with appropriate suffixes', () => {
      expect(formatWithSuffix(1234)).toBe('1.2K')
      expect(formatWithSuffix(1234567)).toBe('1.2M')
      expect(formatWithSuffix(1234567890)).toBe('1.2B')
    })
    it('should handle small numbers', () => {
      expect(formatWithSuffix(123)).toBe('123')
      expect(formatWithSuffix(12)).toBe('12')
    })
  })
  describe('formatOrdinal', () => {
    it('should format numbers with correct ordinal suffixes', () => {
      expect(formatOrdinal(1)).toBe('1st')
      expect(formatOrdinal(2)).toBe('2nd')
      expect(formatOrdinal(3)).toBe('3rd')
      expect(formatOrdinal(4)).toBe('4th')
    })
    it('should handle special cases', () => {
      expect(formatOrdinal(11)).toBe('11th')
      expect(formatOrdinal(12)).toBe('12th')
      expect(formatOrdinal(13)).toBe('13th')
    })
  })
  describe('formatFileSize', () => {
    it('should format file sizes with appropriate units', () => {
      expect(formatFileSize(1024)).toBe('1.0 KB')
      expect(formatFileSize(1024 * 1024)).toBe('1.0 MB')
      expect(formatFileSize(1024 * 1024 * 1024)).toBe('1.0 GB')
    })
    it('should handle small sizes', () => {
      expect(formatFileSize(100)).toBe('100.0 B')
      expect(formatFileSize(0)).toBe('0.0 B')
    })
    it('should format partial units', () => {
      expect(formatFileSize(1536)).toBe('1.5 KB')
      expect(formatFileSize(1.5 * 1024 * 1024)).toBe('1.5 MB')
    })
  })
}) 