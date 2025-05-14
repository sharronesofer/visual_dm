import { join } from 'path';
import { mkdir, writeFile, readFile, unlink, readdir } from 'fs/promises';
import { ThumbnailCache, ThumbnailCacheConfig } from '../ThumbnailCache';
import { ThumbnailOptions, ThumbnailResult } from '../ThumbnailGenerator';
import { Logger } from '../../../utils/logger';

// Mock fs/promises
jest.mock('fs/promises', () => ({
  mkdir: jest.fn(),
  writeFile: jest.fn(),
  readFile: jest.fn(),
  unlink: jest.fn(),
  readdir: jest.fn(),
  stat: jest.fn()
}));

// Mock Logger
type MockLogger = {
  debug: jest.Mock;
  info: jest.Mock;
  warn: jest.Mock;
  error: jest.Mock;
};

jest.mock('../../../utils/logger', () => ({
  Logger: {
    getInstance: jest.fn().mockReturnValue({
      child: jest.fn().mockReturnValue({
        debug: jest.fn(),
        info: jest.fn(),
        warn: jest.fn(),
        error: jest.fn()
      })
    })
  }
}));

describe('ThumbnailCache', () => {
  let cache: ThumbnailCache;
  let config: ThumbnailCacheConfig;
  let mockLogger: MockLogger;

  beforeEach(() => {
    // Clear all mocks
    jest.clearAllMocks();

    // Set up test configuration
    config = {
      maxMemoryEntries: 2,
      maxCacheSize: 1024 * 1024, // 1MB
      cachePath: join(process.cwd(), 'test-cache'),
      ttl: 1000 // 1 second
    };

    // Create cache instance
    cache = new ThumbnailCache(config);

    // Get mock logger instance
    mockLogger = (Logger.getInstance() as any).child('') as MockLogger;
  });

  describe('initialize', () => {
    it('should create cache directory', async () => {
      await cache.initialize();
      expect(mkdir).toHaveBeenCalledWith(config.cachePath, { recursive: true });
      expect(mockLogger.info).toHaveBeenCalledWith(
        'Thumbnail cache initialized',
        expect.objectContaining({ path: config.cachePath })
      );
    });

    it('should handle directory creation error', async () => {
      const error = new Error('Failed to create directory');
      (mkdir as jest.Mock).mockRejectedValueOnce(error);

      await expect(cache.initialize()).rejects.toThrow(error);
      expect(mockLogger.error).toHaveBeenCalledWith(
        'Failed to initialize thumbnail cache',
        undefined,
        expect.objectContaining({ error: error.message })
      );
    });
  });

  describe('get and set', () => {
    const testContent = Buffer.from('test-content');
    const testOptions: ThumbnailOptions = { width: 100, height: 100 };
    const testResult: ThumbnailResult = {
      data: Buffer.from('test-thumbnail'),
      metadata: {
        width: 100,
        height: 100,
        format: 'jpeg',
        size: 1000,
        originalFormat: 'jpeg',
        generatedAt: new Date()
      }
    };

    beforeEach(async () => {
      await cache.initialize();
    });

    it('should store and retrieve from memory cache', async () => {
      await cache.set(testContent, testOptions, testResult);
      const result = await cache.get(testContent, testOptions);
      expect(result).toEqual(testResult);
      expect(writeFile).toHaveBeenCalled();
      expect(mockLogger.debug).toHaveBeenCalledWith(
        'Thumbnail found in memory cache',
        expect.any(Object)
      );
    });

    it('should store and retrieve from disk cache when not in memory', async () => {
      // Mock stat and readFile to simulate existing cache file
      (require('fs/promises').stat as jest.Mock).mockResolvedValueOnce({
        mtimeMs: Date.now(),
        size: 1000
      });
      (readFile as jest.Mock).mockResolvedValueOnce(Buffer.from(JSON.stringify(testResult)));

      const result = await cache.get(testContent, testOptions);
      expect(result).toEqual(testResult);
      expect(mockLogger.debug).toHaveBeenCalledWith(
        'Thumbnail found in disk cache',
        expect.any(Object)
      );
    });

    it('should handle disk read errors', async () => {
      const error = new Error('Read error') as NodeJS.ErrnoException;
      error.code = 'EIO';
      (readFile as jest.Mock).mockRejectedValueOnce(error);

      const result = await cache.get(testContent, testOptions);
      expect(result).toBeNull();
      expect(mockLogger.warn).toHaveBeenCalledWith(
        'Failed to read cached thumbnail',
        expect.objectContaining({
          error: error.message,
          code: error.code
        })
      );
    });

    it('should handle disk write errors', async () => {
      const error = new Error('Write error');
      (writeFile as jest.Mock).mockRejectedValueOnce(error);

      await cache.set(testContent, testOptions, testResult);
      expect(mockLogger.error).toHaveBeenCalledWith(
        'Failed to write thumbnail to disk cache',
        undefined,
        expect.objectContaining({ error: error.message })
      );
    });

    it('should cleanup old entries when cache is full', async () => {
      // Fill cache beyond capacity
      const entries = Array.from({ length: 3 }, (_, i) => ({
        content: Buffer.from(`content-${i}`),
        options: { ...testOptions },
        result: {
          ...testResult,
          data: Buffer.from(`thumbnail-${i}`)
        }
      }));

      for (const entry of entries) {
        await cache.set(entry.content, entry.options, entry.result);
      }

      // Verify oldest entry was removed
      const oldestResult = await cache.get(entries[0].content, entries[0].options);
      expect(oldestResult).toBeNull();

      // Verify newest entries remain
      const newestResult = await cache.get(entries[2].content, entries[2].options);
      expect(newestResult).toEqual(entries[2].result);
    });
  });

  describe('clear', () => {
    it('should clear memory and disk cache', async () => {
      (readdir as jest.Mock).mockResolvedValueOnce(['file1.bin', 'file2.bin']);

      await cache.clear();

      expect(unlink).toHaveBeenCalledTimes(2);
      expect(mockLogger.error).not.toHaveBeenCalled();
    });

    it('should handle clear errors', async () => {
      const error = new Error('Clear error');
      (readdir as jest.Mock).mockRejectedValueOnce(error);

      await expect(cache.clear()).rejects.toThrow(error);
      expect(mockLogger.error).toHaveBeenCalledWith(
        'Failed to clear disk cache',
        undefined,
        expect.objectContaining({ error: error.message })
      );
    });
  });
}); 