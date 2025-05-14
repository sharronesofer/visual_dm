import { lookup } from 'mime-types';
import { DocumentThumbnailGenerator } from '../DocumentThumbnailGenerator';
import { ThumbnailOptions } from '../ThumbnailGenerator';
import { ValidationError } from '../../../errors/ValidationError';
import * as pdfjsLib from 'pdfjs-dist';
import { createCanvas } from 'canvas';

// Mock pdfjs-dist
jest.mock('pdfjs-dist', () => ({
  getDocument: jest.fn().mockReturnValue({
    promise: Promise.resolve({
      getPage: jest.fn().mockResolvedValue({
        getViewport: jest.fn().mockReturnValue({
          width: 800,
          height: 600,
        }),
        render: jest.fn().mockReturnValue({
          promise: Promise.resolve(),
        }),
      }),
    }),
  }),
}));

// Mock canvas
jest.mock('canvas', () => ({
  createCanvas: jest.fn().mockReturnValue({
    getContext: jest.fn().mockReturnValue({
      // Mock canvas context methods
      drawImage: jest.fn(),
      fillRect: jest.fn(),
    }),
    toBuffer: jest.fn().mockReturnValue(Buffer.from('test-image')),
  }),
}));

// Mock sharp
jest.mock('sharp', () => {
  const mockSharp = jest.fn().mockReturnValue({
    metadata: jest.fn().mockResolvedValue({ width: 800, height: 600, format: 'jpeg' }),
    resize: jest.fn().mockReturnThis(),
    toFormat: jest.fn().mockReturnThis(),
    toBuffer: jest.fn().mockResolvedValue({ 
      data: Buffer.from('test-image'),
      info: { width: 200, height: 200, size: 1000 }
    }),
  });
  return { default: mockSharp };
});

// Mock mime-types
jest.mock('mime-types', () => ({
  lookup: jest.fn(),
}));

describe('DocumentThumbnailGenerator', () => {
  let generator: DocumentThumbnailGenerator;
  const testDocument = Buffer.from('test-document');
  const defaultOptions: ThumbnailOptions = {
    width: 200,
    height: 200,
    quality: 80,
    format: 'jpeg',
    preserveAspectRatio: true,
  };

  beforeEach(() => {
    jest.clearAllMocks();
    generator = new DocumentThumbnailGenerator();
  });

  describe('canHandle', () => {
    it('should return true for supported document types', () => {
      const supportedTypes = [
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'application/msword',
        'application/vnd.ms-excel',
        'application/vnd.ms-powerpoint',
      ];

      supportedTypes.forEach((mimeType) => {
        expect(generator.canHandle(mimeType)).toBe(true);
      });
    });

    it('should return false for unsupported types', () => {
      const unsupportedTypes = [
        'application/json',
        'text/plain',
        'image/jpeg',
        'video/mp4',
      ];

      unsupportedTypes.forEach((mimeType) => {
        expect(generator.canHandle(mimeType)).toBe(false);
      });
    });
  });

  describe('generateThumbnail', () => {
    beforeEach(() => {
      // Mock successful PDF document loading
      (pdfjsLib.getDocument as jest.Mock).mockReturnValue({
        promise: Promise.resolve({
          getPage: jest.fn().mockResolvedValue({
            getViewport: jest.fn().mockReturnValue({
              width: 800,
              height: 600,
            }),
            render: jest.fn().mockReturnValue({
              promise: Promise.resolve(),
            }),
          }),
        }),
      });
    });

    it('should generate thumbnail from buffer', async () => {
      const result = await generator.generateThumbnail(testDocument, defaultOptions);

      expect(result.success).toBe(true);
      expect(result.data).toBeDefined();
      expect(pdfjsLib.getDocument).toHaveBeenCalled();
    });

    it('should generate thumbnail from file path', async () => {
      (lookup as jest.Mock).mockReturnValue('application/pdf');
      const result = await generator.generateThumbnail('test.pdf', defaultOptions);

      expect(result.success).toBe(true);
      expect(result.data).toBeDefined();
      expect(pdfjsLib.getDocument).toHaveBeenCalledWith('test.pdf');
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

      const result = await generator.generateThumbnail(testDocument, invalidOptions);

      expect(result.success).toBe(false);
      expect(result.error).toBeInstanceOf(ValidationError);
      expect(result.data).toBeNull();
    });

    it('should handle PDF loading errors', async () => {
      (pdfjsLib.getDocument as jest.Mock).mockReturnValue({
        promise: Promise.reject(new Error('Failed to load PDF')),
      });

      const result = await generator.generateThumbnail(testDocument, defaultOptions);

      expect(result.success).toBe(false);
      expect(result.error).toBeInstanceOf(ValidationError);
      expect(result.data).toBeNull();
    });

    it('should handle rendering errors', async () => {
      (pdfjsLib.getDocument as jest.Mock).mockReturnValue({
        promise: Promise.resolve({
          getPage: jest.fn().mockResolvedValue({
            getViewport: jest.fn().mockReturnValue({
              width: 800,
              height: 600,
            }),
            render: jest.fn().mockReturnValue({
              promise: Promise.reject(new Error('Rendering failed')),
            }),
          }),
        }),
      });

      const result = await generator.generateThumbnail(testDocument, defaultOptions);

      expect(result.success).toBe(false);
      expect(result.error).toBeInstanceOf(ValidationError);
      expect(result.data).toBeNull();
    });

    it('should use default options when none provided', async () => {
      await generator.generateThumbnail(testDocument);

      const mockSharp = (await import('sharp')).default as unknown as jest.Mock;
      expect(mockSharp().resize).toHaveBeenCalledWith(
        expect.any(Number),
        expect.any(Number),
        expect.objectContaining({ fit: 'inside' })
      );
    });

    it('should preserve aspect ratio when specified', async () => {
      const options: ThumbnailOptions = {
        ...defaultOptions,
        preserveAspectRatio: true,
      };

      await generator.generateThumbnail(testDocument, options);

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

      await generator.generateThumbnail(testDocument, options);

      const mockSharp = (await import('sharp')).default as unknown as jest.Mock;
      expect(mockSharp().resize).toHaveBeenCalledWith(
        expect.any(Number),
        expect.any(Number),
        expect.objectContaining({ fit: 'fill' })
      );
    });

    it('should handle custom dimensions', async () => {
      const options: ThumbnailOptions = {
        ...defaultOptions,
        width: 300,
        height: 150,
      };

      await generator.generateThumbnail(testDocument, options);

      const mockSharp = (await import('sharp')).default as unknown as jest.Mock;
      expect(mockSharp().resize).toHaveBeenCalledWith(
        300,
        150,
        expect.any(Object)
      );
    });

    it('should handle custom page number', async () => {
      const options: ThumbnailOptions = {
        ...defaultOptions,
        page: 2,
      };

      await generator.generateThumbnail(testDocument, options);

      expect(pdfjsLib.getDocument).toHaveBeenCalled();
      const mockPdf = await (pdfjsLib.getDocument as jest.Mock).mock.results[0].value.promise;
      expect(mockPdf.getPage).toHaveBeenCalledWith(2);
    });
  });

  describe('cleanup', () => {
    it('should not throw error on cleanup', async () => {
      await expect(generator.cleanup()).resolves.not.toThrow();
    });
  });
}); 