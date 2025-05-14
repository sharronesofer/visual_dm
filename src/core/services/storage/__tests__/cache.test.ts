import { StorageCache, StorageCacheConfig } from '../cache';
import { StorageMetadata } from '../interfaces';
import { MemoryCacheProvider } from '../cache';

describe('StorageCache', () => {
  let cache: StorageCache;
  const defaultConfig: StorageCacheConfig = {
    maxItems: 3,
    maxSize: 1000,
    defaultTTL: 100,
    cacheMetadata: true,
    cacheContents: true,
    cacheListings: true
  };

  beforeEach(() => {
    cache = new StorageCache(defaultConfig);
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  describe('metadata caching', () => {
    const testMetadata: StorageMetadata = {
      name: 'test.txt',
      mimeType: 'text/plain',
      size: 100,
      createdAt: new Date(),
      modifiedAt: new Date()
    };

    it('should cache and retrieve metadata', () => {
      cache.setMetadata('test.txt', testMetadata);
      expect(cache.getMetadata('test.txt')).toEqual(testMetadata);
    });

    it('should respect TTL for metadata', () => {
      cache.setMetadata('test.txt', testMetadata);
      jest.advanceTimersByTime(defaultConfig.defaultTTL! + 1);
      expect(cache.getMetadata('test.txt')).toBeUndefined();
    });

    it('should respect custom TTL for metadata', () => {
      const customTTL = 200;
      cache.setMetadata('test.txt', testMetadata, customTTL);
      jest.advanceTimersByTime(defaultConfig.defaultTTL! + 1);
      expect(cache.getMetadata('test.txt')).toBeDefined();
      jest.advanceTimersByTime(customTTL);
      expect(cache.getMetadata('test.txt')).toBeUndefined();
    });

    it('should not cache metadata when disabled', () => {
      cache = new StorageCache({ ...defaultConfig, cacheMetadata: false });
      cache.setMetadata('test.txt', testMetadata);
      expect(cache.getMetadata('test.txt')).toBeUndefined();
    });
  });

  describe('contents caching', () => {
    const testContents = Buffer.from('test content');

    it('should cache and retrieve contents', () => {
      cache.setContents('test.txt', testContents);
      expect(cache.getContents('test.txt')).toEqual(testContents);
    });

    it('should respect TTL for contents', () => {
      cache.setContents('test.txt', testContents);
      jest.advanceTimersByTime(defaultConfig.defaultTTL! + 1);
      expect(cache.getContents('test.txt')).toBeUndefined();
    });

    it('should respect custom TTL for contents', () => {
      const customTTL = 200;
      cache.setContents('test.txt', testContents, customTTL);
      jest.advanceTimersByTime(defaultConfig.defaultTTL! + 1);
      expect(cache.getContents('test.txt')).toBeDefined();
      jest.advanceTimersByTime(customTTL);
      expect(cache.getContents('test.txt')).toBeUndefined();
    });

    it('should not cache contents when disabled', () => {
      cache = new StorageCache({ ...defaultConfig, cacheContents: false });
      cache.setContents('test.txt', testContents);
      expect(cache.getContents('test.txt')).toBeUndefined();
    });
  });

  describe('listing caching', () => {
    const testListing = ['file1.txt', 'file2.txt'];

    it('should cache and retrieve listings', () => {
      cache.setListing('dir', testListing);
      expect(cache.getListing('dir')).toEqual(testListing);
    });

    it('should respect TTL for listings', () => {
      cache.setListing('dir', testListing);
      jest.advanceTimersByTime(defaultConfig.defaultTTL! + 1);
      expect(cache.getListing('dir')).toBeUndefined();
    });

    it('should respect custom TTL for listings', () => {
      const customTTL = 200;
      cache.setListing('dir', testListing, customTTL);
      jest.advanceTimersByTime(defaultConfig.defaultTTL! + 1);
      expect(cache.getListing('dir')).toBeDefined();
      jest.advanceTimersByTime(customTTL);
      expect(cache.getListing('dir')).toBeUndefined();
    });

    it('should not cache listings when disabled', () => {
      cache = new StorageCache({ ...defaultConfig, cacheListings: false });
      cache.setListing('dir', testListing);
      expect(cache.getListing('dir')).toBeUndefined();
    });
  });

  describe('cache eviction', () => {
    it('should evict items when max items reached', () => {
      const items = ['item1', 'item2', 'item3', 'item4'];
      items.forEach(item => {
        cache.setMetadata(item, {
          name: item,
          mimeType: 'text/plain',
          size: 100,
          createdAt: new Date(),
          modifiedAt: new Date()
        });
      });

      // First item should be evicted
      expect(cache.getMetadata('item1')).toBeUndefined();
      expect(cache.getMetadata('item4')).toBeDefined();
    });

    it('should evict items when max size reached', () => {
      cache = new StorageCache({ ...defaultConfig, maxSize: 250 });
      
      // Add items that will exceed max size
      cache.setContents('file1', Buffer.alloc(100));
      cache.setContents('file2', Buffer.alloc(100));
      cache.setContents('file3', Buffer.alloc(100));

      // First item should be evicted to make room
      expect(cache.getContents('file1')).toBeUndefined();
      expect(cache.getContents('file3')).toBeDefined();
    });

    it('should evict expired items first', () => {
      cache.setContents('file1', Buffer.alloc(100));
      jest.advanceTimersByTime(defaultConfig.defaultTTL! + 1);
      
      cache.setContents('file2', Buffer.alloc(100));
      
      // Expired item should be evicted first
      expect(cache.getContents('file1')).toBeUndefined();
      expect(cache.getContents('file2')).toBeDefined();
    });
  });

  describe('invalidation', () => {
    it('should invalidate specific cache entry', () => {
      const metadata: StorageMetadata = {
        name: 'test.txt',
        mimeType: 'text/plain',
        size: 100,
        createdAt: new Date(),
        modifiedAt: new Date()
      };
      const contents = Buffer.from('test');
      const listing = ['test.txt'];

      cache.setMetadata('test.txt', metadata);
      cache.setContents('test.txt', contents);
      cache.setListing('dir', listing);

      cache.invalidate('test.txt');

      expect(cache.getMetadata('test.txt')).toBeUndefined();
      expect(cache.getContents('test.txt')).toBeUndefined();
      expect(cache.getListing('dir')).toBeDefined();
    });

    it('should clear all cache entries', () => {
      cache.setMetadata('test.txt', {
        name: 'test.txt',
        mimeType: 'text/plain',
        size: 100,
        createdAt: new Date(),
        modifiedAt: new Date()
      });
      cache.setContents('test.txt', Buffer.from('test'));
      cache.setListing('dir', ['test.txt']);

      cache.clear();

      expect(cache.getStats().metadataEntries).toBe(0);
      expect(cache.getStats().contentsEntries).toBe(0);
      expect(cache.getStats().listingEntries).toBe(0);
      expect(cache.getStats().totalSize).toBe(0);
    });
  });

  describe('statistics', () => {
    it('should track cache statistics correctly', () => {
      const metadata: StorageMetadata = {
        name: 'test.txt',
        mimeType: 'text/plain',
        size: 100,
        createdAt: new Date(),
        modifiedAt: new Date()
      };
      const contents = Buffer.from('test');
      const listing = ['test.txt'];

      cache.setMetadata('test.txt', metadata);
      cache.setContents('test.txt', contents);
      cache.setListing('dir', listing);

      const stats = cache.getStats();
      expect(stats.metadataEntries).toBe(1);
      expect(stats.contentsEntries).toBe(1);
      expect(stats.listingEntries).toBe(1);
      expect(stats.totalSize).toBeGreaterThan(0);
      expect(stats.maxSize).toBe(defaultConfig.maxSize);
    });
  });
});

describe('MemoryCacheProvider', () => {
  it('should set and get values', () => {
    const cache = new MemoryCacheProvider<string>({ maxItems: 10 });
    cache.set('a', 'foo');
    expect(cache.get('a')).toBe('foo');
  });

  it('should return undefined for missing keys', () => {
    const cache = new MemoryCacheProvider<string>({ maxItems: 10 });
    expect(cache.get('missing')).toBeUndefined();
  });

  it('should delete values', () => {
    const cache = new MemoryCacheProvider<string>({ maxItems: 10 });
    cache.set('a', 'foo');
    cache.delete('a');
    expect(cache.get('a')).toBeUndefined();
  });

  it('should clear all values', () => {
    const cache = new MemoryCacheProvider<string>({ maxItems: 10 });
    cache.set('a', 'foo');
    cache.set('b', 'bar');
    cache.clear();
    expect(cache.get('a')).toBeUndefined();
    expect(cache.get('b')).toBeUndefined();
  });

  it('should expire values after TTL', done => {
    const cache = new MemoryCacheProvider<string>({ maxItems: 10, defaultTTL: 50 });
    cache.set('a', 'foo');
    setTimeout(() => {
      expect(cache.get('a')).toBeUndefined();
      done();
    }, 60);
  });

  it('should evict least recently used items when maxItems is exceeded', () => {
    const cache = new MemoryCacheProvider<string>({ maxItems: 2 });
    cache.set('a', 'foo');
    cache.set('b', 'bar');
    cache.get('a'); // a is now most recently used
    cache.set('c', 'baz'); // should evict b
    expect(cache.get('a')).toBe('foo');
    expect(cache.get('b')).toBeUndefined();
    expect(cache.get('c')).toBe('baz');
  });

  it('should evict items to stay under maxSize', () => {
    const cache = new MemoryCacheProvider<string>({ maxSize: 10 });
    cache.set('a', '12345'); // size ~10
    cache.set('b', '67890'); // triggers eviction
    expect(cache.get('a')).toBeUndefined();
    expect(cache.get('b')).toBe('67890');
  });

  it('should report stats', () => {
    const cache = new MemoryCacheProvider<string>({ maxItems: 10 });
    cache.set('a', 'foo');
    const stats = cache.stats();
    expect(stats.entries).toBe(1);
    expect(stats.totalSize).toBeGreaterThan(0);
    expect(stats.maxSize).toBeGreaterThan(0);
  });

  it('should return true for has() if key exists and not expired', () => {
    const cache = new MemoryCacheProvider<string>({ maxItems: 10 });
    cache.set('a', 'foo');
    expect(cache.has('a')).toBe(true);
    cache.delete('a');
    expect(cache.has('a')).toBe(false);
  });
}); 