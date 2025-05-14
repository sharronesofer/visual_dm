import { ThumbnailService, ThumbnailServiceConfig } from '../ThumbnailService';
import { ThumbnailOptions, ThumbnailResult } from '../ThumbnailGenerator';
import { ThumbnailCache } from '../ThumbnailCache';
import { Logger } from '../../../utils/logger';

// Mock file-type
jest.mock('file-type', () => ({
  fileTypeFromBuffer: jest.fn()
}));

// Mock mime-types
jest.mock('mime-types', () => ({
  lookup: jest.fn()
}));

// Mock Logger
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

// Mock ThumbnailCache
jest.mock('../ThumbnailCache');

describe('ThumbnailService', () => {
  let service: ThumbnailService;
  let mockCache: jest.Mocked<ThumbnailCache>;
  let mockLogger: any;

  const testFile = Buffer.from('test-file');
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

  beforeEach(() => {
    jest.clearAllMocks();

    // Set up mock cache
    mockCache = {
      initialize: jest.fn().mockResolvedValue(undefined),
      get: jest.fn().mockResolvedValue(null),
      set: jest.fn().mockResolvedValue(undefined),
      clear: jest.fn().mockResolvedValue(undefined)
    } as any;

    (ThumbnailCache as jest.Mock).mockImplementation(() => mockCache);

    // Set up mock logger
    mockLogger = (Logger.getInstance() as any).child('');

    // Create service instance
    service = new ThumbnailService();
  });

  describe('initialize', () => {
    it('should initialize cache', async () => {
      await service.initialize();
      expect(mockCache.initialize).toHaveBeenCalled();
    });

    it('should handle initialization errors', async () => {
      const error = new Error('Init error');
      mockCache.initialize.mockRejectedValueOnce(error);

      await expect(service.initialize()).rejects.toThrow(error);
    });
  });

  describe('generateThumbnail', () => {
    it('should return cached thumbnail if available', async () => {
      mockCache.get.mockResolvedValueOnce(testResult);

      const result = await service.generateThumbnail(testFile, testOptions);

      expect(result).toEqual({
        success: true,
        data: testResult
      });
      expect(mockCache.get).toHaveBeenCalledWith(testFile, testOptions);
      expect(mockLogger.debug).toHaveBeenCalledWith('Thumbnail found in cache');
    });

    it('should generate and cache thumbnail if not cached', async () => {
      // Mock file type detection
      const fileType = await import('file-type');
      (fileType.fileTypeFromBuffer as jest.Mock).mockResolvedValueOnce({
        mime: 'image/jpeg'
      });

      // Mock cache miss
      mockCache.get.mockResolvedValueOnce(null);

      const result = await service.generateThumbnail(testFile, testOptions);

      expect(result.success).toBe(true);
      expect(mockCache.set).toHaveBeenCalledWith(
        testFile,
        testOptions,
        expect.objectContaining({
          data: expect.any(Buffer),
          metadata: expect.any(Object)
        })
      );
    });

    it('should handle unknown file types', async () => {
      const fileType = await import('file-type');
      (fileType.fileTypeFromBuffer as jest.Mock).mockResolvedValueOnce(null);

      const result = await service.generateThumbnail(testFile, testOptions);

      expect(result).toEqual({
        success: false,
        error: expect.objectContaining({
          message: 'Could not determine file type',
          code: 'UNKNOWN_TYPE',
          statusCode: 400
        }),
        data: null
      });
      expect(mockCache.set).not.toHaveBeenCalled();
    });

    it('should handle unsupported file types', async () => {
      const fileType = await import('file-type');
      (fileType.fileTypeFromBuffer as jest.Mock).mockResolvedValueOnce({
        mime: 'application/x-unsupported'
      });

      const result = await service.generateThumbnail(testFile, testOptions);

      expect(result).toEqual({
        success: false,
        error: expect.objectContaining({
          message: expect.stringContaining('Unsupported file type'),
          code: 'UNSUPPORTED_TYPE',
          statusCode: 400
        }),
        data: null
      });
      expect(mockCache.set).not.toHaveBeenCalled();
    });

    it('should handle generation errors', async () => {
      const fileType = await import('file-type');
      (fileType.fileTypeFromBuffer as jest.Mock).mockRejectedValueOnce(
        new Error('Generation error')
      );

      const result = await service.generateThumbnail(testFile, testOptions);

      expect(result).toEqual({
        success: false,
        error: expect.objectContaining({
          message: 'Failed to generate thumbnail',
          code: 'GENERATION_ERROR',
          statusCode: 500
        }),
        data: null
      });
      expect(mockCache.set).not.toHaveBeenCalled();
      expect(mockLogger.error).toHaveBeenCalledWith(
        'Failed to generate thumbnail',
        expect.any(Error),
        expect.objectContaining({
          error: 'Generation error'
        })
      );
    });

    it('should handle file paths', async () => {
      const lookup = require('mime-types').lookup;
      lookup.mockReturnValueOnce('image/jpeg');

      await service.generateThumbnail('test.jpg', testOptions);

      expect(lookup).toHaveBeenCalledWith('test.jpg');
    });
  });

  describe('cleanup', () => {
    it('should cleanup cache and generators', async () => {
      await service.cleanup();
      expect(mockCache.clear).toHaveBeenCalled();
    });

    it('should handle cleanup errors', async () => {
      const error = new Error('Cleanup error');
      mockCache.clear.mockRejectedValueOnce(error);

      await expect(service.cleanup()).rejects.toThrow(error);
    });
  });
}); 