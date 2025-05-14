import {
  capitalizeFirst,
  toTitleCase,
  truncate,
  camelToKebab,
  kebabToCamel,
  toSnakeCase,
  stripHtml,
  slugify,
  wordWrap,
  formatPhoneNumber,
  formatCodeBlock
} from '../textFormat';

describe('Text Formatting Utilities', () => {
  describe('capitalizeFirst', () => {
    it('should capitalize first letter', () => {
      expect(capitalizeFirst('hello')).toBe('Hello');
      expect(capitalizeFirst('world')).toBe('World');
    });

    it('should handle empty strings', () => {
      expect(capitalizeFirst('')).toBe('');
      expect(capitalizeFirst(null as any)).toBe(null);
    });

    it('should not modify already capitalized text', () => {
      expect(capitalizeFirst('Hello')).toBe('Hello');
    });
  });

  describe('toTitleCase', () => {
    it('should convert text to title case', () => {
      expect(toTitleCase('hello world')).toBe('Hello World');
      expect(toTitleCase('the quick brown fox')).toBe('The Quick Brown Fox');
    });

    it('should handle empty strings', () => {
      expect(toTitleCase('')).toBe('');
      expect(toTitleCase(null as any)).toBe(null);
    });

    it('should handle multiple spaces', () => {
      expect(toTitleCase('hello   world')).toBe('Hello   World');
    });
  });

  describe('truncate', () => {
    it('should truncate text to specified length', () => {
      expect(truncate('Hello World', 8)).toBe('Hello...');
      expect(truncate('Short', 10)).toBe('Short');
    });

    it('should handle empty strings', () => {
      expect(truncate('', 5)).toBe('');
      expect(truncate(null as any, 5)).toBe(null);
    });
  });

  describe('camelToKebab', () => {
    it('should convert camelCase to kebab-case', () => {
      expect(camelToKebab('helloWorld')).toBe('hello-world');
      expect(camelToKebab('thisIsATest')).toBe('this-is-a-test');
    });

    it('should handle numbers', () => {
      expect(camelToKebab('hello123World')).toBe('hello123-world');
    });
  });

  describe('kebabToCamel', () => {
    it('should convert kebab-case to camelCase', () => {
      expect(kebabToCamel('hello-world')).toBe('helloWorld');
      expect(kebabToCamel('this-is-a-test')).toBe('thisIsATest');
    });
  });

  describe('toSnakeCase', () => {
    it('should convert text to snake_case', () => {
      expect(toSnakeCase('helloWorld')).toBe('hello_world');
      expect(toSnakeCase('This Is A Test')).toBe('this_is_a_test');
    });

    it('should handle hyphens', () => {
      expect(toSnakeCase('hello-world')).toBe('hello_world');
    });
  });

  describe('stripHtml', () => {
    it('should remove HTML tags', () => {
      expect(stripHtml('<p>Hello <b>World</b></p>')).toBe('Hello World');
      expect(stripHtml('<div>Test</div>')).toBe('Test');
    });

    it('should handle nested tags', () => {
      expect(stripHtml('<div><p>Hello <b>World</b></p></div>')).toBe('Hello World');
    });
  });

  describe('slugify', () => {
    it('should create URL-friendly slugs', () => {
      expect(slugify('Hello World')).toBe('hello-world');
      expect(slugify('This Is A Test!')).toBe('this-is-a-test');
    });

    it('should handle special characters', () => {
      expect(slugify('Hello & World!')).toBe('hello-world');
      expect(slugify('Test@123')).toBe('test123');
    });
  });

  describe('wordWrap', () => {
    it('should wrap text at specified width', () => {
      expect(wordWrap('Hello World', 5)).toBe('Hello\nWorld');
      expect(wordWrap('This is a test', 7)).toBe('This is\na test');
    });
  });

  describe('formatPhoneNumber', () => {
    it('should format phone numbers', () => {
      expect(formatPhoneNumber('1234567890')).toBe('(123) 456-7890');
      expect(formatPhoneNumber('5551234567')).toBe('(555) 123-4567');
    });

    it('should handle invalid formats', () => {
      expect(formatPhoneNumber('123')).toBe('123');
      expect(formatPhoneNumber('abc')).toBe('abc');
    });
  });

  describe('formatCodeBlock', () => {
    it('should format code blocks with language', () => {
      expect(formatCodeBlock('const x = 1;', 'javascript')).toBe('```javascript\nconst x = 1;\n```');
    });

    it('should handle empty language', () => {
      expect(formatCodeBlock('test')).toBe('```\ntest\n```');
    });
  });
}); 