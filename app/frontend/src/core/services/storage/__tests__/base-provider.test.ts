import { join } from 'path';
import { BaseStorageProvider } from '../base-provider';
import { StorageError, StorageTimeoutError, StorageOperationOptions } from '../interfaces';

// Concrete implementation for testing
class TestStorageProvider extends BaseStorageProvider {
  public exposedNormalizePath(path: string): string {
    return this.normalizePath(path);
  }

  public exposedGetRelativePath(path: string): string {
    return this.getRelativePath(path);
  }

  public exposedCreateMetadata(path: string, size: number, customMetadata?: Record<string, unknown>) {
    return this.createMetadata(path, size, customMetadata);
  }

  public async exposedWithTimeout<T>(
    operation: () => Promise<T>,
    path: string,
    operationName: string,
    timeout?: number
  ): Promise<T> {
    return this.withTimeout(operation, path, operationName, timeout);
  }

  public async exposedValidateOverwrite(path: string, options?: StorageOperationOptions): Promise<void> {
    return this.validateOverwrite(path, options);
  }

  // Required abstract method implementations
  async save() { return { path: '', metadata: { name: '', mimeType: '', size: 0, createdAt: new Date(), modifiedAt: new Date() } }; }
  async read() { return Buffer.from(''); }
  async delete() { return true; }
  async exists() { return false; }
  async list() { return []; }
  async getMetadata() { return { name: '', mimeType: '', size: 0, createdAt: new Date(), modifiedAt: new Date() }; }
  getUrl() { return ''; }
  async copy() { return { path: '', metadata: { name: '', mimeType: '', size: 0, createdAt: new Date(), modifiedAt: new Date() } }; }
  async move() { return { path: '', metadata: { name: '', mimeType: '', size: 0, createdAt: new Date(), modifiedAt: new Date() } }; }
}

describe('BaseStorageProvider', () => {
  let provider: TestStorageProvider;
  const testBasePath = '/test/base/path';

  beforeEach(() => {
    provider = new TestStorageProvider({ basePath: testBasePath });
  });

  describe('normalizePath', () => {
    it('should normalize relative paths', () => {
      const result = provider.exposedNormalizePath('test/path/file.txt');
      expect(result).toBe(join(testBasePath, 'test/path/file.txt'));
    });

    it('should preserve absolute paths', () => {
      const absolutePath = '/absolute/path/file.txt';
      const result = provider.exposedNormalizePath(absolutePath);
      expect(result).toBe(absolutePath);
    });

    it('should remove parent directory references', () => {
      const result = provider.exposedNormalizePath('../../../test/file.txt');
      expect(result).toBe(join(testBasePath, 'test/file.txt'));
    });

    it('should throw on invalid paths', () => {
      expect(() => provider.exposedNormalizePath('\0invalid')).toThrow(StorageError);
    });
  });

  describe('getRelativePath', () => {
    it('should convert absolute path to relative', () => {
      const absolutePath = join(testBasePath, 'test/file.txt');
      const result = provider.exposedGetRelativePath(absolutePath);
      expect(result).toBe('test/file.txt');
    });

    it('should handle paths outside base path', () => {
      const outsidePath = '/outside/path/file.txt';
      const result = provider.exposedGetRelativePath(outsidePath);
      expect(result.startsWith('..')).toBe(true);
    });
  });

  describe('createMetadata', () => {
    it('should create metadata with defaults', () => {
      const result = provider.exposedCreateMetadata('test.txt', 100);
      expect(result).toEqual({
        name: 'test.txt',
        mimeType: 'text/plain',
        size: 100,
        createdAt: expect.any(Date),
        modifiedAt: expect.any(Date),
        metadata: undefined
      });
    });

    it('should include custom metadata', () => {
      const customMetadata = { author: 'test' };
      const result = provider.exposedCreateMetadata('test.txt', 100, customMetadata);
      expect(result.metadata).toEqual(customMetadata);
    });

    it('should handle unknown file types', () => {
      const result = provider.exposedCreateMetadata('test.unknown', 100);
      expect(result.mimeType).toBe('application/octet-stream');
    });
  });

  describe('withTimeout', () => {
    it('should complete operation within timeout', async () => {
      const result = await provider.exposedWithTimeout(
        () => Promise.resolve('success'),
        'test.txt',
        'test',
        1000
      );
      expect(result).toBe('success');
    });

    it('should throw TimeoutError on timeout', async () => {
      await expect(
        provider.exposedWithTimeout(
          () => new Promise(resolve => setTimeout(resolve, 100)),
          'test.txt',
          'test',
          50
        )
      ).rejects.toThrow(StorageTimeoutError);
    });

    it('should wrap other errors', async () => {
      await expect(
        provider.exposedWithTimeout(
          () => Promise.reject(new Error('test error')),
          'test.txt',
          'test',
          1000
        )
      ).rejects.toThrow(StorageError);
    });
  });

  describe('validateOverwrite', () => {
    it('should allow overwrite when file does not exist', async () => {
      await expect(provider.exposedValidateOverwrite('test.txt')).resolves.toBeUndefined();
    });

    it('should allow overwrite when explicitly enabled', async () => {
      jest.spyOn(provider, 'exists').mockResolvedValue(true);
      await expect(
        provider.exposedValidateOverwrite('test.txt', { overwrite: true })
      ).resolves.toBeUndefined();
    });

    it('should throw when file exists and overwrite not enabled', async () => {
      jest.spyOn(provider, 'exists').mockResolvedValue(true);
      await expect(
        provider.exposedValidateOverwrite('test.txt', { overwrite: false })
      ).rejects.toThrow();
    });
  });
}); 