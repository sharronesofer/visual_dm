import {
  setCacheValue,
  getCacheValue,
  deleteCacheValue,
  clearCache,
  Cache,
  InvalidateCache,
  CacheManager,
} from '../cache';

describe('Cache Utilities', () => {
  beforeEach(() => {
    // Clear cache before each test
    clearCache();
  });

  describe('Basic Cache Operations', () => {
    it('should set and get cache value', () => {
      const key = 'test-key';
      const value = { data: 'test' };

      setCacheValue(key, value);
      const cached = getCacheValue(key);

      expect(cached).toEqual(value);
    });

    it('should handle cache miss', () => {
      const key = 'non-existent';
      const cached = getCacheValue(key);

      expect(cached).toBeNull();
    });

    it('should delete cache value', () => {
      const key = 'test-key';
      const value = { data: 'test' };

      setCacheValue(key, value);
      deleteCacheValue(key);
      const cached = getCacheValue(key);

      expect(cached).toBeNull();
    });

    it('should clear all cache values', () => {
      setCacheValue('key1', 'value1');
      setCacheValue('key2', 'value2');

      clearCache();

      expect(getCacheValue('key1')).toBeNull();
      expect(getCacheValue('key2')).toBeNull();
    });
  });

  describe('Cache Configuration', () => {
    it('should respect TTL configuration', async () => {
      const key = 'test-key';
      const value = { data: 'test' };
      const ttl = 100; // 100ms

      setCacheValue(key, value, { ttl });
      expect(getCacheValue(key)).toEqual(value);

      await new Promise(resolve => setTimeout(resolve, 150));
      expect(getCacheValue(key)).toBeNull();
    });

    it('should respect cache prefix', () => {
      const key = 'test-key';
      const value = { data: 'test' };
      const prefix = 'prefix';

      setCacheValue(key, value, { prefix });

      // Should be accessible with prefix
      expect(getCacheValue(key, { prefix })).toEqual(value);

      // Should not be accessible without prefix
      expect(getCacheValue(key)).toBeNull();
    });

    it('should not cache when disabled', () => {
      const key = 'test-key';
      const value = { data: 'test' };

      setCacheValue(key, value, { enabled: false });
      expect(getCacheValue(key)).toBeNull();
    });
  });

  describe('Cache Decorators', () => {
    class TestService {
      private callCount = 0;

      @Cache()
      getData(id: string): Promise<any> {
        this.callCount++;
        return Promise.resolve({ id, data: 'test' });
      }

      @Cache({ ttl: 100 })
      getDataWithTTL(id: string): Promise<any> {
        this.callCount++;
        return Promise.resolve({ id, data: 'test' });
      }

      @InvalidateCache(['test-key'])
      updateData(id: string): Promise<void> {
        return Promise.resolve();
      }

      getCallCount(): number {
        return this.callCount;
      }
    }

    let service: TestService;

    beforeEach(() => {
      service = new TestService();
    });

    it('should cache method results', async () => {
      const result1 = await service.getData('123');
      const result2 = await service.getData('123');

      expect(result1).toEqual(result2);
      expect(service.getCallCount()).toBe(1);
    });

    it('should respect TTL in decorator', async () => {
      const result1 = await service.getDataWithTTL('123');
      await new Promise(resolve => setTimeout(resolve, 50));
      const result2 = await service.getDataWithTTL('123');

      expect(result1).toEqual(result2);
      expect(service.getCallCount()).toBe(1);

      await new Promise(resolve => setTimeout(resolve, 100));
      const result3 = await service.getDataWithTTL('123');

      expect(service.getCallCount()).toBe(2);
    });

    it('should invalidate cache on method call', async () => {
      setCacheValue('test-key', { data: 'test' });
      await service.updateData('123');
      expect(getCacheValue('test-key')).toBeNull();
    });
  });

  describe('CacheManager', () => {
    let cacheManager: CacheManager;

    beforeEach(() => {
      cacheManager = new CacheManager();
    });

    it('should manage cache with instance configuration', () => {
      const key = 'test-key';
      const value = { data: 'test' };

      cacheManager.set(key, value);
      expect(cacheManager.get(key)).toEqual(value);

      cacheManager.delete(key);
      expect(cacheManager.get(key)).toBeNull();
    });

    it('should update configuration', () => {
      const key = 'test-key';
      const value = { data: 'test' };

      cacheManager.setConfig({ enabled: false });
      cacheManager.set(key, value);
      expect(cacheManager.get(key)).toBeNull();

      cacheManager.setConfig({ enabled: true });
      cacheManager.set(key, value);
      expect(cacheManager.get(key)).toEqual(value);
    });

    it('should clear all values', () => {
      cacheManager.set('key1', 'value1');
      cacheManager.set('key2', 'value2');

      cacheManager.clear();

      expect(cacheManager.get('key1')).toBeNull();
      expect(cacheManager.get('key2')).toBeNull();
    });

    it('should get configuration', () => {
      const config = { ttl: 1000, prefix: 'test' };
      cacheManager.setConfig(config);

      expect(cacheManager.getConfig()).toEqual({
        enabled: true,
        ttl: 1000,
        prefix: 'test',
      });
    });
  });

  describe('Error Handling', () => {
    it('should handle invalid keys', () => {
      expect(() => setCacheValue(undefined as any, 'value')).toThrow();
      expect(() => getCacheValue(undefined as any)).toThrow();
      expect(() => deleteCacheValue(undefined as any)).toThrow();
    });

    it('should handle circular references', () => {
      const circular: any = { data: 'test' };
      circular.self = circular;

      expect(() => setCacheValue('key', circular)).toThrow();
    });
  });
});
