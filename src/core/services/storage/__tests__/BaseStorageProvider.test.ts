import { BaseStorageProvider, BaseStorageConfig, ProgressData } from '../BaseStorageProvider';
import { StorageOptions, StorageResult, StorageItem, StorageError, StorageErrorCode } from '../../../interfaces/storage/StorageProvider';
import { Readable } from 'stream';

// Create a concrete implementation for testing
class TestStorageProvider extends BaseStorageProvider {
  protected async performSave(
    data: Buffer | Readable,
    fullPath: string,
    options: StorageOptions
  ): Promise<StorageResult> {
    return {
      path: fullPath,
      size: Buffer.isBuffer(data) ? data.length : 0,
      metadata: options.metadata
    };
  }

  protected async performGet(fullPath: string): Promise<Buffer | Readable> {
    return Buffer.from('test');
  }

  protected async performDelete(fullPath: string): Promise<boolean> {
    return true;
  }

  protected async performExists(fullPath: string): Promise<boolean> {
    return true;
  }

  protected async performGetUrl(fullPath: string): Promise<string> {
    return `https://example.com/${fullPath}`;
  }

  protected async performList(fullPath: string): Promise<StorageItem[]> {
    return [{
      path: fullPath + '/test.txt',
      size: 100,
      lastModified: new Date(),
      isDirectory: false
    }];
  }

  protected async performCopy(fullSourcePath: string, fullDestPath: string): Promise<boolean> {
    return true;
  }

  protected async performMove(fullSourcePath: string, fullDestPath: string): Promise<boolean> {
    return true;
  }

  protected async performGetMetadata(fullPath: string): Promise<Record<string, any>> {
    return { test: 'metadata' };
  }

  protected async performUpdateMetadata(
    fullPath: string,
    metadata: Record<string, any>
  ): Promise<Record<string, any>> {
    return metadata;
  }

  protected async ensureParentDirectory(fullPath: string): Promise<void> {
    // No-op for testing
  }

  protected mapError(error: unknown): StorageError {
    if (error instanceof Error) {
      return new StorageError(StorageErrorCode.UNKNOWN, error.message);
    }
    return new StorageError(StorageErrorCode.UNKNOWN, 'Unknown error');
  }
}

describe('BaseStorageProvider', () => {
  let provider: TestStorageProvider;
  const defaultConfig: BaseStorageConfig = {
    basePath: '/test/base',
    defaultOptions: {
      contentType: 'text/plain',
      isPublic: true
    },
    enableProgress: true
  };

  beforeEach(() => {
    provider = new TestStorageProvider(defaultConfig);
  });

  describe('constructor', () => {
    it('should initialize with default config', () => {
      const defaultProvider = new TestStorageProvider();
      expect(defaultProvider).toBeInstanceOf(BaseStorageProvider);
    });

    it('should initialize with custom config', () => {
      expect(provider).toBeInstanceOf(BaseStorageProvider);
    });
  });

  describe('path resolution', () => {
    it('should resolve paths relative to base path', async () => {
      const result = await provider.save(Buffer.from('test'), 'file.txt');
      expect(result.path).toBe('test/base/file.txt');
    });

    it('should handle paths with different separators', async () => {
      const result = await provider.save(Buffer.from('test'), '\\folder\\file.txt');
      expect(result.path).toBe('test/base/folder/file.txt');
    });

    it('should handle paths without base path', async () => {
      const simpleProvider = new TestStorageProvider();
      const result = await simpleProvider.save(Buffer.from('test'), 'file.txt');
      expect(result.path).toBe('file.txt');
    });
  });

  describe('options merging', () => {
    it('should merge options with defaults', async () => {
      const customOptions: StorageOptions = {
        contentType: 'application/json',
        metadata: { test: 'value' }
      };

      const result = await provider.save(Buffer.from('test'), 'file.txt', customOptions);
      expect(result.metadata).toEqual({ test: 'value' });
    });

    it('should use default options when none provided', async () => {
      const result = await provider.save(Buffer.from('test'), 'file.txt');
      expect(result.url).toBeDefined(); // Because defaultOptions.isPublic is true
    });
  });

  describe('progress events', () => {
    it('should emit progress events when enabled', (done) => {
      const progressData: ProgressData = {
        bytesTransferred: 50,
        totalBytes: 100,
        percent: 50
      };

      provider.once('progress', (data) => {
        expect(data).toEqual(progressData);
        done();
      });

      provider.emit('progress', progressData);
    });

    it('should not emit progress events when disabled', () => {
      const noProgressProvider = new TestStorageProvider({
        enableProgress: false
      });

      const progressListener = jest.fn();
      noProgressProvider.on('progress', progressListener);

      noProgressProvider.emit('progress', {
        bytesTransferred: 50,
        totalBytes: 100
      });

      expect(progressListener).not.toHaveBeenCalled();
    });
  });

  describe('error handling', () => {
    it('should map errors in save operation', async () => {
      const errorProvider = new TestStorageProvider();
      jest.spyOn(errorProvider as any, 'performSave').mockRejectedValue(new Error('Save failed'));

      await expect(errorProvider.save(Buffer.from('test'), 'file.txt'))
        .rejects
        .toThrow(StorageError);
    });

    it('should map errors in other operations', async () => {
      const errorProvider = new TestStorageProvider();
      jest.spyOn(errorProvider as any, 'performGet').mockRejectedValue(new Error('Get failed'));
      jest.spyOn(errorProvider as any, 'performDelete').mockRejectedValue(new Error('Delete failed'));
      jest.spyOn(errorProvider as any, 'performExists').mockRejectedValue(new Error('Exists failed'));

      await expect(errorProvider.get('file.txt')).rejects.toThrow(StorageError);
      await expect(errorProvider.delete('file.txt')).rejects.toThrow(StorageError);
      await expect(errorProvider.exists('file.txt')).rejects.toThrow(StorageError);
    });
  });

  describe('optional operations', () => {
    it('should support copy operation', async () => {
      const result = await provider.copy('source.txt', 'dest.txt');
      expect(result).toBe(true);
    });

    it('should support move operation', async () => {
      const result = await provider.move('source.txt', 'dest.txt');
      expect(result).toBe(true);
    });

    it('should support metadata operations', async () => {
      const metadata = await provider.getMetadata('file.txt');
      expect(metadata).toEqual({ test: 'metadata' });

      const updatedMetadata = await provider.updateMetadata('file.txt', { new: 'value' });
      expect(updatedMetadata).toEqual({ new: 'value' });
    });
  });
}); 