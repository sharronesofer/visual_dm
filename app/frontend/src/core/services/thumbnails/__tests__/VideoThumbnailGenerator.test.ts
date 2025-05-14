import { lookup } from 'mime-types';
import { VideoThumbnailGenerator } from '../VideoThumbnailGenerator';
import { ThumbnailOptions } from '../ThumbnailGenerator';
import { ValidationError } from '../../../errors/ValidationError';

// Mock ffmpeg
jest.mock('fluent-ffmpeg', () => {
  const mockFfmpeg = jest.fn().mockReturnValue({
    screenshots: jest.fn().mockReturnThis(),
    on: jest.fn().mockReturnThis(),
  });
  const mockFfprobe = jest.fn();
  return Object.assign(mockFfmpeg, { ffprobe: mockFfprobe });
});

// Mock mime-types
jest.mock('mime-types', () => ({
  lookup: jest.fn(),
}));

// Mock sharp
jest.mock('sharp', () => {
  const mockSharp = jest.fn().mockReturnValue({
    metadata: jest.fn().mockResolvedValue({ width: 800, height: 600, format: 'jpeg' }),
    resize: jest.fn().mockReturnThis(),
    toFormat: jest.fn().mockReturnThis(),
    toBuffer: jest.fn().mockResolvedValue(Buffer.from('test-image')),
  });
  return mockSharp;
});

// Import ffmpeg after mocking
const ffmpeg = require('fluent-ffmpeg');

describe('VideoThumbnailGenerator', () => {
  let generator: VideoThumbnailGenerator;
  const testVideo = Buffer.from('test-video');
  const defaultOptions: ThumbnailOptions = {
    width: 200,
    height: 200,
    quality: 80,
    format: 'jpeg',
    preserveAspectRatio: true,
    timestamp: 0,
  };

  beforeEach(() => {
    jest.clearAllMocks();
    generator = new VideoThumbnailGenerator();
  });

  describe('canHandle', () => {
    it('should return true for supported video types', () => {
      const supportedTypes = [
        'video/mp4',
        'video/webm',
        'video/ogg',
        'video/quicktime',
        'video/x-msvideo',
      ];

      supportedTypes.forEach((mimeType) => {
        expect(generator.canHandle(mimeType)).toBe(true);
      });
    });

    it('should return false for unsupported types', () => {
      const unsupportedTypes = [
        'video/avi',
        'image/jpeg',
        'audio/mp3',
        'text/plain',
      ];

      unsupportedTypes.forEach((mimeType) => {
        expect(generator.canHandle(mimeType)).toBe(false);
      });
    });
  });

  describe('generateThumbnail', () => {
    beforeEach(() => {
      // Mock successful ffprobe response
      ffmpeg.ffprobe.mockImplementation((_, callback) => {
        callback(null, {
          format: {
            duration: 100,
            format_name: 'mp4',
          },
        });
      });

      // Mock successful screenshots
      (ffmpeg as jest.Mock).mockReturnValue({
        screenshots: jest.fn().mockReturnThis(),
        on: jest.fn().mockImplementation(function(this: any, event: string, callback: () => void) {
          if (event === 'end') {
            callback();
          }
          return this;
        }),
      });
    });

    it('should generate thumbnail from buffer', async () => {
      const result = await generator.generateThumbnail(testVideo, defaultOptions);

      expect(result.success).toBe(true);
      expect(result.data).toBeDefined();
      expect(ffmpeg).toHaveBeenCalled();
    });

    it('should generate thumbnail from file path', async () => {
      (lookup as jest.Mock).mockReturnValue('video/mp4');
      const result = await generator.generateThumbnail('test.mp4', defaultOptions);

      expect(result.success).toBe(true);
      expect(result.data).toBeDefined();
      expect(ffmpeg).toHaveBeenCalledWith('test.mp4');
    });

    it('should handle invalid file input', async () => {
      const result = await generator.generateThumbnail('', defaultOptions);

      expect(result.success).toBe(false);
      expect(result.error).toBeInstanceOf(ValidationError);
      expect(result.data).toBeNull();
    });

    it('should handle invalid options', async () => {
      const invalidOptions: ThumbnailOptions = {
        ...defaultOptions,
        width: -100, // Invalid width
      };

      const result = await generator.generateThumbnail(testVideo, invalidOptions);

      expect(result.success).toBe(false);
      expect(result.error).toBeInstanceOf(ValidationError);
      expect(result.data).toBeNull();
    });

    it('should handle invalid timestamp', async () => {
      const invalidOptions: ThumbnailOptions = {
        ...defaultOptions,
        timestamp: -1, // Invalid timestamp
      };

      const result = await generator.generateThumbnail(testVideo, invalidOptions);

      expect(result.success).toBe(false);
      expect(result.error).toBeInstanceOf(ValidationError);
      expect(result.data).toBeNull();
    });

    it('should handle ffprobe errors', async () => {
      ffmpeg.ffprobe.mockImplementation((_, callback) => {
        callback(new Error('FFprobe failed'), null);
      });

      const result = await generator.generateThumbnail(testVideo, defaultOptions);

      expect(result.success).toBe(false);
      expect(result.error).toBeInstanceOf(ValidationError);
      expect(result.data).toBeNull();
    });

    it('should handle frame extraction errors', async () => {
      (ffmpeg as jest.Mock).mockReturnValue({
        screenshots: jest.fn().mockReturnThis(),
        on: jest.fn().mockImplementation(function(this: any, event: string, callback: (err?: Error) => void) {
          if (event === 'error') {
            callback(new Error('Frame extraction failed'));
          }
          return this;
        }),
      });

      const result = await generator.generateThumbnail(testVideo, defaultOptions);

      expect(result.success).toBe(false);
      expect(result.error).toBeInstanceOf(ValidationError);
      expect(result.data).toBeNull();
    });

    it('should use default options when none provided', async () => {
      await generator.generateThumbnail(testVideo);

      expect(ffmpeg).toHaveBeenCalled();
      const mockFfmpeg = ffmpeg as unknown as jest.Mock;
      expect(mockFfmpeg().screenshots).toHaveBeenCalledWith(
        expect.objectContaining({
          timestamps: [0],
        })
      );
    });

    it('should preserve aspect ratio when specified', async () => {
      const options: ThumbnailOptions = {
        ...defaultOptions,
        preserveAspectRatio: true,
      };

      await generator.generateThumbnail(testVideo, options);

      const mockSharp = (await import('sharp')).default as unknown as jest.Mock;
      expect(mockSharp().resize).toHaveBeenCalledWith(
        expect.any(Number),
        expect.any(Number),
        expect.objectContaining({ fit: 'inside' })
      );
    });

    it('should not preserve aspect ratio when specified', async () => {
      const options: ThumbnailOptions = {
        ...defaultOptions,
        preserveAspectRatio: false,
      };

      await generator.generateThumbnail(testVideo, options);

      const mockSharp = (await import('sharp')).default as unknown as jest.Mock;
      expect(mockSharp().resize).toHaveBeenCalledWith(
        expect.any(Number),
        expect.any(Number),
        expect.objectContaining({ fit: 'fill' })
      );
    });
  });

  describe('cleanup', () => {
    it('should not throw error on cleanup', async () => {
      await expect(generator.cleanup()).resolves.not.toThrow();
    });
  });
}); 