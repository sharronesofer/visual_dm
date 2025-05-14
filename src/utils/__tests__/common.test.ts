import {
  isValidString,
  isValidNumber,
  isValidDate,
  formatDate,
  generateRandomString,
  deepClone,
  safeJsonParse,
  removeUndefined,
  isEmpty,
  formatFileSize,
  isValidMimeType,
  getFileExtension,
  generateSlug,
  isValidUUID,
  retry,
  debounce,
  throttle
} from '../common';
import { ValidationError } from '../../errors';

describe('Common Utilities', () => {
  describe('isValidString', () => {
    it('should return true for valid strings', () => {
      expect(isValidString('test')).toBe(true);
      expect(isValidString(' test ')).toBe(true);
    });

    it('should return false for invalid strings', () => {
      expect(isValidString('')).toBe(false);
      expect(isValidString(' ')).toBe(false);
      expect(isValidString(null)).toBe(false);
      expect(isValidString(undefined)).toBe(false);
      expect(isValidString(123)).toBe(false);
    });
  });

  describe('isValidNumber', () => {
    it('should return true for valid numbers', () => {
      expect(isValidNumber(123)).toBe(true);
      expect(isValidNumber(0)).toBe(true);
      expect(isValidNumber(-123)).toBe(true);
      expect(isValidNumber(1.23)).toBe(true);
    });

    it('should return false for invalid numbers', () => {
      expect(isValidNumber(NaN)).toBe(false);
      expect(isValidNumber(Infinity)).toBe(false);
      expect(isValidNumber(-Infinity)).toBe(false);
      expect(isValidNumber('123')).toBe(false);
      expect(isValidNumber(null)).toBe(false);
    });
  });

  describe('isValidDate', () => {
    it('should return true for valid dates', () => {
      expect(isValidDate(new Date())).toBe(true);
      expect(isValidDate('2024-03-15')).toBe(true);
      expect(isValidDate('2024-03-15T12:00:00Z')).toBe(true);
    });

    it('should return false for invalid dates', () => {
      expect(isValidDate('invalid')).toBe(false);
      expect(isValidDate(null)).toBe(false);
      expect(isValidDate(undefined)).toBe(false);
      expect(isValidDate(123)).toBe(false);
      expect(isValidDate(new Date('invalid'))).toBe(false);
    });
  });

  describe('formatDate', () => {
    it('should format dates correctly', () => {
      const date = new Date('2024-03-15T12:34:56.789Z');
      expect(formatDate(date)).toBe('2024-03-15T12:34:56Z');
    });

    it('should format date strings correctly', () => {
      expect(formatDate('2024-03-15T12:34:56.789Z')).toBe('2024-03-15T12:34:56Z');
    });

    it('should throw ValidationError for invalid dates', () => {
      expect(() => formatDate('invalid')).toThrow(ValidationError);
      expect(() => formatDate(new Date('invalid'))).toThrow(ValidationError);
    });
  });

  describe('generateRandomString', () => {
    it('should generate string of specified length', () => {
      expect(generateRandomString(10)).toHaveLength(10);
      expect(generateRandomString(20)).toHaveLength(20);
    });

    it('should generate different strings', () => {
      const str1 = generateRandomString();
      const str2 = generateRandomString();
      expect(str1).not.toBe(str2);
    });

    it('should use default length if not specified', () => {
      expect(generateRandomString()).toHaveLength(32);
    });
  });

  describe('deepClone', () => {
    it('should create a deep copy of an object', () => {
      const original = { a: 1, b: { c: 2 }, d: [1, 2, 3] };
      const clone = deepClone(original);
      expect(clone).toEqual(original);
      expect(clone).not.toBe(original);
      expect(clone.b).not.toBe(original.b);
      expect(clone.d).not.toBe(original.d);
    });
  });

  describe('safeJsonParse', () => {
    it('should parse valid JSON', () => {
      const json = '{"a":1,"b":2}';
      expect(safeJsonParse(json, null)).toEqual({ a: 1, b: 2 });
    });

    it('should return default value for invalid JSON', () => {
      const defaultValue = { default: true };
      expect(safeJsonParse('invalid', defaultValue)).toBe(defaultValue);
    });
  });

  describe('removeUndefined', () => {
    it('should remove undefined properties', () => {
      const obj = { a: 1, b: undefined, c: null, d: 0 };
      expect(removeUndefined(obj)).toEqual({ a: 1, c: null, d: 0 });
    });
  });

  describe('isEmpty', () => {
    it('should return true for empty objects', () => {
      expect(isEmpty({})).toBe(true);
      expect(isEmpty(null)).toBe(true);
      expect(isEmpty(undefined)).toBe(true);
    });

    it('should return false for non-empty objects', () => {
      expect(isEmpty({ a: 1 })).toBe(false);
      expect(isEmpty([1, 2, 3])).toBe(false);
      expect(isEmpty('test')).toBe(false);
      expect(isEmpty(123)).toBe(false);
    });
  });

  describe('formatFileSize', () => {
    it('should format file sizes correctly', () => {
      expect(formatFileSize(500)).toBe('500 B');
      expect(formatFileSize(1024)).toBe('1 KB');
      expect(formatFileSize(1024 * 1024)).toBe('1 MB');
      expect(formatFileSize(1024 * 1024 * 1024)).toBe('1 GB');
    });

    it('should throw ValidationError for invalid sizes', () => {
      expect(() => formatFileSize(NaN)).toThrow(ValidationError);
      expect(() => formatFileSize(-1)).not.toThrow(ValidationError);
    });
  });

  describe('isValidMimeType', () => {
    it('should validate MIME types correctly', () => {
      expect(isValidMimeType('image/jpeg')).toBe(true);
      expect(isValidMimeType('application/json')).toBe(true);
      expect(isValidMimeType('text/plain')).toBe(true);
      expect(isValidMimeType('video/mp4')).toBe(true);
    });

    it('should reject invalid MIME types', () => {
      expect(isValidMimeType('invalid')).toBe(false);
      expect(isValidMimeType('image/')).toBe(false);
      expect(isValidMimeType('/jpeg')).toBe(false);
      expect(isValidMimeType('image//jpeg')).toBe(false);
    });
  });

  describe('getFileExtension', () => {
    it('should extract file extensions correctly', () => {
      expect(getFileExtension('test.jpg')).toBe('jpg');
      expect(getFileExtension('test.JPG')).toBe('jpg');
      expect(getFileExtension('test')).toBe('');
      expect(getFileExtension('test.file.txt')).toBe('txt');
    });

    it('should throw ValidationError for invalid filenames', () => {
      expect(() => getFileExtension('')).toThrow(ValidationError);
      expect(() => getFileExtension(' ')).toThrow(ValidationError);
    });
  });

  describe('generateSlug', () => {
    it('should generate valid slugs', () => {
      expect(generateSlug('Hello World')).toBe('hello-world');
      expect(generateSlug('This is a test!')).toBe('this-is-a-test');
      expect(generateSlug('Multiple   Spaces')).toBe('multiple-spaces');
      expect(generateSlug('-Trim-Dashes-')).toBe('trim-dashes');
    });

    it('should throw ValidationError for invalid input', () => {
      expect(() => generateSlug('')).toThrow(ValidationError);
      expect(() => generateSlug(' ')).toThrow(ValidationError);
    });
  });

  describe('isValidUUID', () => {
    it('should validate UUIDs correctly', () => {
      expect(isValidUUID('123e4567-e89b-4d3f-89ab-12d3e4f56789')).toBe(true);
      expect(isValidUUID('invalid')).toBe(false);
      expect(isValidUUID('123e4567-e89b-1d3f-89ab-12d3e4f56789')).toBe(false);
    });
  });

  describe('retry', () => {
    it('should retry failed operations', async () => {
      let attempts = 0;
      const fn = jest.fn().mockImplementation(() => {
        attempts++;
        if (attempts < 2) {
          throw new Error('Temporary error');
        }
        return Promise.resolve('success');
      });

      const result = await retry(fn, 3, 100);
      expect(result).toBe('success');
      expect(attempts).toBe(2);
    });

    it('should throw after max attempts', async () => {
      const fn = jest.fn().mockRejectedValue(new Error('Persistent error'));
      await expect(retry(fn, 2, 100)).rejects.toThrow('Persistent error');
      expect(fn).toHaveBeenCalledTimes(2);
    });
  });

  describe('debounce', () => {
    beforeEach(() => {
      jest.useFakeTimers();
    });

    afterEach(() => {
      jest.useRealTimers();
    });

    it('should debounce function calls', () => {
      const fn = jest.fn();
      const debouncedFn = debounce(fn, 1000);

      debouncedFn();
      debouncedFn();
      debouncedFn();

      expect(fn).not.toHaveBeenCalled();

      jest.runAllTimers();

      expect(fn).toHaveBeenCalledTimes(1);
    });
  });

  describe('throttle', () => {
    beforeEach(() => {
      jest.useFakeTimers();
    });

    afterEach(() => {
      jest.useRealTimers();
    });

    it('should throttle function calls', () => {
      const fn = jest.fn();
      const throttledFn = throttle(fn, 1000);

      throttledFn();
      throttledFn();
      throttledFn();

      expect(fn).toHaveBeenCalledTimes(1);

      jest.runAllTimers();

      throttledFn();
      expect(fn).toHaveBeenCalledTimes(2);
    });
  });
}); 