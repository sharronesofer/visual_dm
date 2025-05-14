import { promises as fs } from 'fs';
import fs_sync from 'fs';
import path from 'path';
import { Readable, Writable } from 'stream';
import { MediaProcessingService } from '../MediaProcessingService';
import {
  ProcessingJobStatus,
  StreamProcessingOptions,
  ProcessingProgress,
  ProcessingJob
} from '../types/MediaProcessing';
import { ServiceError } from '../base/types';
import { ConversionOptions, ConversionResult } from '../converters/FormatConverter';

const testFilesDir = path.join(__dirname, '../../../test/fixtures/media');

// Helper functions for test file creation
async function createTestImage(): Promise<void> {
  const testImagePath = path.join(testFilesDir, 'test.jpg');
  const imageBuffer = Buffer.from('fake image data');
  await fs.writeFile(testImagePath, imageBuffer);
}

async function createTestVideo(): Promise<void> {
  const testVideoPath = path.join(testFilesDir, 'test.mp4');
  const videoBuffer = Buffer.from('fake video data');
  await fs.writeFile(testVideoPath, videoBuffer);
}

async function createTestAudio(): Promise<void> {
  const testAudioPath = path.join(testFilesDir, 'test.mp3');
  const audioBuffer = Buffer.from('fake audio data');
  await fs.writeFile(testAudioPath, audioBuffer);
}

async function createTestDocument(): Promise<void> {
  const testDocPath = path.join(testFilesDir, 'test.docx');
  const docBuffer = Buffer.from('fake document data');
  await fs.writeFile(testDocPath, docBuffer);
}

describe('MediaProcessingService', () => {
  let service: MediaProcessingService;

  beforeAll(async () => {
    // Create test files directory if it doesn't exist
    await fs.mkdir(testFilesDir, { recursive: true });

    // Create test files
    await Promise.all([
      createTestImage(),
      createTestVideo(),
      createTestAudio(),
      createTestDocument()
    ]);

    service = MediaProcessingService.getInstance();
    await service.initialize();
  });

  afterAll(async () => {
    await service.cleanup();
    // Clean up test files
    await fs.rm(testFilesDir, { recursive: true, force: true });
  });

  describe('Initialization', () => {
    it('should initialize successfully', async () => {
      const newService = MediaProcessingService.getInstance();
      await expect(newService.initialize()).resolves.not.toThrow();
    });

    it('should be a singleton', () => {
      const instance1 = MediaProcessingService.getInstance();
      const instance2 = MediaProcessingService.getInstance();
      expect(instance1).toBe(instance2);
    });
  });

  describe('Input Validation', () => {
    it('should reject null input', async () => {
      await expect(
        service.process(null as any, {
          mimeType: 'image/jpeg',
          thumbnail: { width: 100, height: 100 }
        })
      ).resolves.toEqual({
        success: false,
        error: expect.any(ServiceError)
      });
    });

    it('should reject empty string input', async () => {
      await expect(
        service.process('', {
          mimeType: 'image/jpeg',
          thumbnail: { width: 100, height: 100 }
        })
      ).resolves.toEqual({
        success: false,
        error: expect.any(ServiceError)
      });
    });

    it('should reject missing MIME type', async () => {
      const buffer = await fs.readFile(path.join(testFilesDir, 'test.jpg'));
      await expect(
        service.process(buffer, {
          mimeType: '',
          thumbnail: { width: 100, height: 100 }
        })
      ).resolves.toEqual({
        success: false,
        error: expect.any(ServiceError)
      });
    });

    it('should reject when no operations are requested', async () => {
      const buffer = await fs.readFile(path.join(testFilesDir, 'test.jpg'));
      await expect(
        service.process(buffer, {
          mimeType: 'image/jpeg'
        })
      ).resolves.toEqual({
        success: false,
        error: expect.any(ServiceError)
      });
    });
  });

  describe('Image Processing', () => {
    let imageBuffer: Buffer;

    beforeAll(async () => {
      imageBuffer = await fs.readFile(path.join(testFilesDir, 'test.jpg'));
    });

    it('should generate thumbnail', async () => {
      const result = await service.process(imageBuffer, {
        mimeType: 'image/jpeg',
        thumbnail: {
          width: 100,
          height: 100,
          format: 'jpeg',
          quality: 80
        }
      });

      expect(result.success).toBe(true);
      expect(result.data).toBeDefined();
      expect(result.data!.thumbnail).toBeInstanceOf(Buffer);
      expect(result.data!.processingTime).toBeGreaterThan(0);
    });

    it('should convert format', async () => {
      const result = await service.process(imageBuffer, {
        mimeType: 'image/jpeg',
        conversion: {
          targetFormat: 'png',
          quality: 90
        }
      });

      expect(result.success).toBe(true);
      expect(result.data).toBeDefined();
      expect(result.data!.converted).toBeInstanceOf(Buffer);
      expect(result.data!.processingTime).toBeGreaterThan(0);
    });

    it('should extract metadata', async () => {
      const result = await service.process(imageBuffer, {
        mimeType: 'image/jpeg',
        metadata: {
          extractExif: true,
          extractIptc: true,
          extractXmp: true
        }
      });

      expect(result.success).toBe(true);
      expect(result.data).toBeDefined();
      expect(result.data!.metadata).toEqual(
        expect.objectContaining({
          format: expect.any(String),
          width: expect.any(Number),
          height: expect.any(Number)
        })
      );
    });

    it('should process multiple operations concurrently', async () => {
      const result = await service.process(imageBuffer, {
        mimeType: 'image/jpeg',
        thumbnail: {
          width: 100,
          height: 100
        },
        conversion: {
          targetFormat: 'png'
        },
        metadata: {
          extractExif: true
        }
      });

      expect(result.success).toBe(true);
      expect(result.data).toBeDefined();
      expect(result.data!.thumbnail).toBeInstanceOf(Buffer);
      expect(result.data!.converted).toBeInstanceOf(Buffer);
      expect(result.data!.metadata).toBeDefined();
    });
  });

  describe('Video Processing', () => {
    let videoBuffer: Buffer;

    beforeAll(async () => {
      videoBuffer = await fs.readFile(path.join(testFilesDir, 'test.mp4'));
    });

    it('should generate video thumbnail', async () => {
      const result = await service.process(videoBuffer, {
        mimeType: 'video/mp4',
        thumbnail: {
          width: 200,
          height: 200,
          timestamp: 1  // 1 second into the video
        }
      });

      expect(result.success).toBe(true);
      expect(result.data).toBeDefined();
      expect(result.data!.thumbnail).toBeInstanceOf(Buffer);
    });

    it('should convert video format', async () => {
      const result = await service.process(videoBuffer, {
        mimeType: 'video/mp4',
        conversion: {
          targetFormat: 'webm',
          quality: 28
        }
      });

      expect(result.success).toBe(true);
      expect(result.data).toBeDefined();
      expect(result.data!.converted).toBeInstanceOf(Buffer);
    });

    it('should extract video metadata', async () => {
      const result = await service.process(videoBuffer, {
        mimeType: 'video/mp4',
        metadata: {
          extractExif: true
        }
      });

      expect(result.success).toBe(true);
      expect(result.data).toBeDefined();
      expect(result.data!.metadata).toEqual(
        expect.objectContaining({
          duration: expect.any(Number),
          width: expect.any(Number),
          height: expect.any(Number),
          codec: expect.any(String)
        })
      );
    });
  });

  describe('Audio Processing', () => {
    let audioBuffer: Buffer;

    beforeAll(async () => {
      audioBuffer = await fs.readFile(path.join(testFilesDir, 'test.mp3'));
    });

    it('should convert audio format', async () => {
      const result = await service.process(audioBuffer, {
        mimeType: 'audio/mpeg',
        conversion: {
          targetFormat: 'wav',
          quality: 5
        }
      });

      expect(result.success).toBe(true);
      expect(result.data).toBeDefined();
      expect(result.data!.converted).toBeInstanceOf(Buffer);
    });

    it('should extract audio metadata', async () => {
      const result = await service.process(audioBuffer, {
        mimeType: 'audio/mpeg',
        metadata: {
          extractExif: true
        }
      });

      expect(result.success).toBe(true);
      expect(result.data).toBeDefined();
      expect(result.data!.metadata).toEqual(
        expect.objectContaining({
          duration: expect.any(Number),
          bitrate: expect.any(Number),
          sampleRate: expect.any(Number)
        })
      );
    });
  });

  describe('Document Processing', () => {
    let pdfBuffer: Buffer;

    beforeAll(async () => {
      pdfBuffer = await fs.readFile(path.join(testFilesDir, 'test.pdf'));
    });

    it('should generate document thumbnail', async () => {
      const result = await service.process(pdfBuffer, {
        mimeType: 'application/pdf',
        thumbnail: {
          width: 200,
          height: 200,
          page: 1
        }
      });

      expect(result.success).toBe(true);
      expect(result.data).toBeDefined();
      expect(result.data!.thumbnail).toBeInstanceOf(Buffer);
    });

    it('should convert document format', async () => {
      const result = await service.process(pdfBuffer, {
        mimeType: 'application/pdf',
        conversion: {
          targetFormat: 'docx',
          quality: 90
        }
      });

      expect(result.success).toBe(true);
      expect(result.data).toBeDefined();
      expect(result.data!.converted).toBeInstanceOf(Buffer);
    });

    it('should extract document metadata', async () => {
      const result = await service.process(pdfBuffer, {
        mimeType: 'application/pdf',
        metadata: {
          extractExif: true
        }
      });

      expect(result.success).toBe(true);
      expect(result.data).toBeDefined();
      expect(result.data!.metadata).toEqual(
        expect.objectContaining({
          pageCount: expect.any(Number),
          author: expect.any(String),
          title: expect.any(String)
        })
      );
    });
  });

  describe('Caching', () => {
    it('should cache and return cached results', async () => {
      const buffer = await fs.readFile(path.join(testFilesDir, 'test.jpg'));
      const options = {
        mimeType: 'image/jpeg',
        thumbnail: { width: 100, height: 100 },
        cache: { enabled: true }
      };

      // First request should process
      const result1 = await service.process(buffer, options);
      expect(result1.success).toBe(true);

      // Second request should return cached result
      const result2 = await service.process(buffer, options);
      expect(result2.success).toBe(true);
      expect(result2.data!.processingTime).toBeLessThan(
        result1.data!.processingTime
      );
    });
  });

  describe('Error Handling', () => {
    it('should handle invalid file formats', async () => {
      const buffer = Buffer.from('invalid file content');
      const result = await service.process(buffer, {
        mimeType: 'image/jpeg',
        thumbnail: { width: 100, height: 100 }
      });

      expect(result.success).toBe(false);
      expect(result.error).toBeInstanceOf(ServiceError);
    });

    it('should handle processing failures gracefully', async () => {
      const buffer = await fs.readFile(path.join(testFilesDir, 'test.jpg'));
      // Corrupt the buffer
      buffer[0] = 0;
      buffer[1] = 0;

      const result = await service.process(buffer, {
        mimeType: 'image/jpeg',
        thumbnail: { width: 100, height: 100 }
      });

      expect(result.success).toBe(false);
      expect(result.error).toBeInstanceOf(ServiceError);
    });
  });

  describe('Stream Processing', () => {
    let inputStream: Readable;
    let outputStream: Writable;
    let testBuffer: Buffer;

    beforeEach(async () => {
      testBuffer = await fs.readFile(path.join(testFilesDir, 'test.jpg'));
      inputStream = Readable.from(testBuffer);
      outputStream = new Writable({
        write(chunk: Buffer | string, encoding: BufferEncoding, callback: (error?: Error | null) => void): void {
          callback();
        }
      });
    });

    afterEach(() => {
      if (inputStream.destroy && !inputStream.destroyed) {
        inputStream.destroy();
      }
      if (outputStream.destroy && !outputStream.destroyed) {
        outputStream.destroy();
      }
    });

    it('should process image stream successfully', async () => {
      const options: StreamProcessingOptions = {
        mimeType: 'image/jpeg',
        conversion: {
          targetFormat: 'png',
          quality: 90
        },
        chunkSize: 1024 * 1024,
        progressInterval: 50
      };

      const result = await service.processStream(inputStream, outputStream, options);

      expect(result.success).toBe(true);
      expect(result.data).toBeDefined();
      expect(result.data!.originalFormat).toBe('jpeg');
      expect(result.data!.processingTime).toBeGreaterThan(0);
      expect(result.data!.bytesProcessed).toBeGreaterThan(0);
    });

    it('should process video stream successfully', async () => {
      const videoBuffer = await fs.readFile(path.join(testFilesDir, 'test.mp4'));
      const videoInputStream = Readable.from(videoBuffer);
      const videoOutputStream = new Writable({
        write(chunk: Buffer | string, encoding: BufferEncoding, callback: (error?: Error | null) => void): void {
          callback();
        }
      });

      const options: StreamProcessingOptions = {
        mimeType: 'video/mp4',
        conversion: {
          targetFormat: 'webm',
          videoCodec: 'vp9',
          audioCodec: 'opus',
          quality: 28,
          fps: 30,
          width: 1280,
          height: 720,
          bitrate: '2M',
          audioBitrate: '128k'
        },
        chunkSize: 1024 * 1024,
        progressInterval: 50
      };

      const result = await service.processStream(videoInputStream, videoOutputStream, options);

      expect(result.success).toBe(true);
      expect(result.data).toBeDefined();
      expect(result.data!.originalFormat).toBe('mp4');
      expect(result.data!.processingTime).toBeGreaterThan(0);
      expect(result.data!.bytesProcessed).toBeGreaterThan(0);
      expect(result.data!.totalBytes).toBeGreaterThan(0);
    });

    it('should process audio stream successfully', async () => {
      const audioBuffer = await fs.readFile(path.join(testFilesDir, 'test.mp3'));
      const audioInputStream = Readable.from(audioBuffer);
      const audioOutputStream = new Writable({
        write(chunk: Buffer | string, encoding: BufferEncoding, callback: (error?: Error | null) => void): void {
          callback();
        }
      });

      const options: StreamProcessingOptions = {
        mimeType: 'audio/mpeg',
        conversion: {
          targetFormat: 'ogg',
          audioCodec: 'vorbis',
          quality: 5,
          audioBitrate: '192k',
          channels: 2,
          sampleRate: 44100
        },
        chunkSize: 1024 * 1024,
        progressInterval: 50
      };

      const result = await service.processStream(audioInputStream, audioOutputStream, options);

      expect(result.success).toBe(true);
      expect(result.data).toBeDefined();
      expect(result.data!.originalFormat).toBe('mp3');
      expect(result.data!.processingTime).toBeGreaterThan(0);
      expect(result.data!.bytesProcessed).toBeGreaterThan(0);
      expect(result.data!.totalBytes).toBeGreaterThan(0);
    });

    it('should process document stream successfully', async () => {
      const docBuffer = await fs.readFile(path.join(testFilesDir, 'test.docx'));
      const docInputStream = Readable.from(docBuffer);
      const docOutputStream = new Writable({
        write(chunk: Buffer | string, encoding: BufferEncoding, callback: (error?: Error | null) => void): void {
          callback();
        }
      });

      const options: StreamProcessingOptions = {
        mimeType: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        conversion: {
          targetFormat: 'pdf',
          quality: 90,
          preserveMetadata: true
        },
        chunkSize: 1024 * 1024,
        progressInterval: 50
      };

      const result = await service.processStream(docInputStream, docOutputStream, options);

      expect(result.success).toBe(true);
      expect(result.data).toBeDefined();
      expect(result.data!.originalFormat).toBe('docx');
      expect(result.data!.processingTime).toBeGreaterThan(0);
      expect(result.data!.bytesProcessed).toBeGreaterThan(0);
      expect(result.data!.totalBytes).toBeGreaterThan(0);
    });

    it('should handle errors during stream processing', async () => {
      const options: StreamProcessingOptions = {
        mimeType: 'image/jpeg',
        conversion: {
          targetFormat: 'invalid_format'
        }
      };

      const result = await service.processStream(inputStream, outputStream, options);

      expect(result.success).toBe(false);
      expect(result.error).toBeDefined();
      expect(result.error!.code).toBe('STREAM_PROCESSING_ERROR');
    });

    it('should track progress during stream processing', async () => {
      const progressUpdates: number[] = [];
      const options: StreamProcessingOptions = {
        mimeType: 'image/jpeg',
        conversion: {
          targetFormat: 'png',
          quality: 90
        },
        progressInterval: 50
      };

      service.on('progress', (progress: ProcessingProgress) => {
        progressUpdates.push(progress.overall);
      });

      await service.processStream(inputStream, outputStream, options);

      expect(progressUpdates.length).toBeGreaterThan(0);
      expect(progressUpdates[progressUpdates.length - 1]).toBe(100);
    });

    it('should process multiple streams in parallel', async () => {
      const streams = await Promise.all([
        fs.readFile(path.join(testFilesDir, 'test.jpg')),
        fs.readFile(path.join(testFilesDir, 'test.mp4')),
        fs.readFile(path.join(testFilesDir, 'test.mp3'))
      ]);

      const options: StreamProcessingOptions[] = [
        {
          mimeType: 'image/jpeg',
          conversion: { 
            targetFormat: 'png',
            quality: 90
          }
        },
        {
          mimeType: 'video/mp4',
          conversion: { 
            targetFormat: 'webm',
            videoCodec: 'vp9',
            audioCodec: 'opus'
          }
        },
        {
          mimeType: 'audio/mpeg',
          conversion: { 
            targetFormat: 'ogg',
            audioCodec: 'vorbis'
          }
        }
      ];

      const results = await Promise.all(
        streams.map((buffer, index) => {
          const inputStream = Readable.from(buffer);
          const outputStream = new Writable({
            write(chunk: Buffer | string, encoding: BufferEncoding, callback: (error?: Error | null) => void): void {
              callback();
            }
          });
          return service.processStream(inputStream, outputStream, options[index]);
        })
      );

      results.forEach(result => {
        expect(result.success).toBe(true);
        expect(result.data).toBeDefined();
        expect(result.data!.processingTime).toBeGreaterThan(0);
      });
    });
  });
}); 