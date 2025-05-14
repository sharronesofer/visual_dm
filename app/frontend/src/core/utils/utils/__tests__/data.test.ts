import {
  deepClone,
  omit,
  pick,
  groupBy,
  sortBy,
  filterBy,
  mapValues,
  unique,
  chunk,
  flatten,
  keyBy,
} from '../data';

describe('Data Manipulation Utilities', () => {
  describe('deepClone', () => {
    it('should clone primitive values', () => {
      expect(deepClone(42)).toBe(42);
      expect(deepClone('test')).toBe('test');
      expect(deepClone(true)).toBe(true);
      expect(deepClone(null)).toBe(null);
      expect(deepClone(undefined)).toBe(undefined);
    });

    it('should deep clone objects', () => {
      const obj = {
        a: 1,
        b: { c: 2, d: { e: 3 } },
        f: [1, { g: 4 }],
      };
      const cloned = deepClone(obj);
      expect(cloned).toEqual(obj);
      expect(cloned).not.toBe(obj);
      expect(cloned.b).not.toBe(obj.b);
      expect(cloned.b.d).not.toBe(obj.b.d);
      expect(cloned.f).not.toBe(obj.f);
      expect(cloned.f[1]).not.toBe(obj.f[1]);
    });

    it('should handle arrays', () => {
      const arr = [1, [2, 3], { a: 4 }];
      const cloned = deepClone(arr);
      expect(cloned).toEqual(arr);
      expect(cloned).not.toBe(arr);
      expect(cloned[1]).not.toBe(arr[1]);
      expect(cloned[2]).not.toBe(arr[2]);
    });
  });

  describe('omit', () => {
    it('should omit specified keys from object', () => {
      const obj = { a: 1, b: 2, c: 3, d: 4 };
      expect(omit(obj, ['b', 'd'])).toEqual({ a: 1, c: 3 });
    });

    it('should handle non-existent keys', () => {
      const obj = { a: 1, b: 2 };
      expect(omit(obj, ['c' as any])).toEqual({ a: 1, b: 2 });
    });
  });

  describe('pick', () => {
    it('should pick specified keys from object', () => {
      const obj = { a: 1, b: 2, c: 3, d: 4 };
      expect(pick(obj, ['b', 'd'])).toEqual({ b: 2, d: 4 });
    });

    it('should handle non-existent keys', () => {
      const obj = { a: 1, b: 2 };
      expect(pick(obj, ['b', 'c' as any])).toEqual({ b: 2 });
    });
  });

  describe('groupBy', () => {
    const items = [
      { id: 1, type: 'a', value: 10 },
      { id: 2, type: 'b', value: 20 },
      { id: 3, type: 'a', value: 30 },
    ];

    it('should group by key', () => {
      expect(groupBy(items, 'type')).toEqual({
        a: [
          { id: 1, type: 'a', value: 10 },
          { id: 3, type: 'a', value: 30 },
        ],
        b: [{ id: 2, type: 'b', value: 20 }],
      });
    });

    it('should group by function', () => {
      expect(
        groupBy(items, item => (item.value > 15 ? 'high' : 'low'))
      ).toEqual({
        low: [{ id: 1, type: 'a', value: 10 }],
        high: [
          { id: 2, type: 'b', value: 20 },
          { id: 3, type: 'a', value: 30 },
        ],
      });
    });
  });

  describe('sortBy', () => {
    const items = [
      { id: 2, value: 'b' },
      { id: 1, value: 'a' },
      { id: 3, value: 'c' },
    ];

    it('should sort by key ascending', () => {
      expect(sortBy(items, 'id')).toEqual([
        { id: 1, value: 'a' },
        { id: 2, value: 'b' },
        { id: 3, value: 'c' },
      ]);
    });

    it('should sort by key descending', () => {
      expect(sortBy(items, 'id', 'desc')).toEqual([
        { id: 3, value: 'c' },
        { id: 2, value: 'b' },
        { id: 1, value: 'a' },
      ]);
    });

    it('should sort by function', () => {
      expect(sortBy(items, item => item.value)).toEqual([
        { id: 1, value: 'a' },
        { id: 2, value: 'b' },
        { id: 3, value: 'c' },
      ]);
    });
  });

  describe('filterBy', () => {
    const items = [
      { id: 1, type: 'a', active: true },
      { id: 2, type: 'b', active: false },
      { id: 3, type: 'a', active: true },
    ];

    it('should filter by predicate object', () => {
      expect(filterBy(items, { type: 'a', active: true })).toEqual([
        { id: 1, type: 'a', active: true },
        { id: 3, type: 'a', active: true },
      ]);
    });

    it('should filter by function', () => {
      expect(filterBy(items, item => item.id > 1 && item.active)).toEqual([
        { id: 3, type: 'a', active: true },
      ]);
    });
  });

  describe('mapValues', () => {
    it('should map object values', () => {
      const obj = { a: 1, b: 2, c: 3 };
      expect(mapValues(obj, (value, key) => `${key}:${value * 2}`)).toEqual({
        a: 'a:2',
        b: 'b:4',
        c: 'c:6',
      });
    });
  });

  describe('unique', () => {
    it('should create unique array of primitives', () => {
      expect(unique([1, 2, 2, 3, 1, 4])).toEqual([1, 2, 3, 4]);
    });

    it('should create unique array by key', () => {
      const items = [
        { id: 1, value: 'a' },
        { id: 2, value: 'b' },
        { id: 1, value: 'c' },
      ];
      expect(unique(items, 'id')).toEqual([
        { id: 1, value: 'a' },
        { id: 2, value: 'b' },
      ]);
    });
  });

  describe('chunk', () => {
    it('should chunk array into smaller arrays', () => {
      expect(chunk([1, 2, 3, 4, 5], 2)).toEqual([[1, 2], [3, 4], [5]]);
      expect(chunk([1, 2, 3, 4], 2)).toEqual([
        [1, 2],
        [3, 4],
      ]);
    });

    it('should handle empty array', () => {
      expect(chunk([], 2)).toEqual([]);
    });
  });

  describe('flatten', () => {
    it('should flatten nested arrays', () => {
      expect(flatten([1, [2, 3], [4, [5, 6]]])).toEqual([1, 2, 3, 4, 5, 6]);
    });

    it('should handle empty arrays', () => {
      expect(flatten([])).toEqual([]);
      expect(flatten([[], []])).toEqual([]);
    });
  });

  describe('keyBy', () => {
    const items = [
      { id: 'a', value: 1 },
      { id: 'b', value: 2 },
      { id: 'c', value: 3 },
    ];

    it('should create object from array using key', () => {
      expect(keyBy(items, 'id')).toEqual({
        a: { id: 'a', value: 1 },
        b: { id: 'b', value: 2 },
        c: { id: 'c', value: 3 },
      });
    });

    it('should create object from array using function', () => {
      expect(keyBy(items, item => `key_${item.id}`)).toEqual({
        key_a: { id: 'a', value: 1 },
        key_b: { id: 'b', value: 2 },
        key_c: { id: 'c', value: 3 },
      });
    });
  });
});
