import { Readable, Writable } from 'stream';
import { promises as fs } from 'fs';
import * as path from 'path';
import { VideoFormatConverter } from '../VideoFormatConverter';
import { ConversionOptions } from '../FormatConverter';
import { StreamProcessingResult } from '../../types/MediaProcessing';

describe('VideoFormatConverter', () => {
  let converter: VideoFormatConverter;
  let inputBuffer: Buffer;
  let outputChunks: Buffer[];
  let mockOutputStream: Writable;
  let tempDir: string;

  beforeEach(async () => {
    converter = new VideoFormatConverter();
    tempDir = path.join(__dirname, 'temp');
    
    // Create a test video buffer (minimal MP4)
    inputBuffer = Buffer.from([
      0x00, 0x00, 0x00, 0x20, 0x66, 0x74, 0x79, 0x70, 0x69, 0x73, 0x6F, 0x6D,
      0x00, 0x00, 0x02, 0x00, 0x69, 0x73, 0x6F, 0x6D, 0x69, 0x73, 0x6F, 0x32,
      0x6D, 0x70, 0x34, 0x31, 0x00, 0x00, 0x00, 0x08, 0x66, 0x72, 0x65, 0x65,
      0x00, 0x00, 0x02, 0x00, 0x6D, 0x64, 0x61, 0x74
    ]);

    // Create a mock output stream that collects chunks
    outputChunks = [];
    mockOutputStream = new Writable({
      write(chunk: Buffer, encoding: BufferEncoding, callback: (error?: Error | null) => void) {
        outputChunks.push(chunk);
        callback();
      }
    });

    // Create temp directory for tests
    await fs.mkdir(tempDir, { recursive: true });
  });

  afterEach(async () => {
    if (mockOutputStream.destroy && !mockOutputStream.destroyed) {
      mockOutputStream.destroy();
    }

    // Clean up temp directory
    try {
      const files = await fs.readdir(tempDir);
      await Promise.all(
        files.map(file => fs.unlink(path.join(tempDir, file)))
      );
      await fs.rmdir(tempDir);
    } catch (error) {
      // Ignore cleanup errors
    }
  });

  describe('convertStream', () => {
    it('should convert MP4 to WebM', async () => {
      const options: ConversionOptions = {
        targetFormat: 'webm',
        videoBitrate: '800k',
        audioBitrate: '128k',
        tempDir,
      };

      const inputStream = Readable.from(inputBuffer);
      const result = await converter.convertStream(inputStream, mockOutputStream, options);

      expect(result.success).toBe(true);
      expect(result.data).toBeDefined();
      expect(result.data!.originalFormat).toBe('mp4');
      expect(result.data!.metadata.format).toBe('webm');
      expect(result.data!.bytesProcessed).toBeGreaterThan(0);
      expect(result.data!.totalBytes).toBeGreaterThan(0);
      expect(result.data!.processingTime).toBeGreaterThan(0);
      expect(result.data!.conversionTime).toBeGreaterThan(0);
      expect(outputChunks.length).toBeGreaterThan(0);
    });

    it('should convert MP4 to MP4 with different codec', async () => {
      const options: ConversionOptions = {
        targetFormat: 'mp4',
        videoCodec: 'libx265', // Use HEVC codec
        audioBitrate: '192k',
        quality: 28, // CRF value for x265
        tempDir,
      };

      const inputStream = Readable.from(inputBuffer);
      const result = await converter.convertStream(inputStream, mockOutputStream, options);

      expect(result.success).toBe(true);
      expect(result.data).toBeDefined();
      expect(result.data!.metadata.codec).toBe('hevc');
    });

    it('should handle resizing during conversion', async () => {
      const options: ConversionOptions = {
        targetFormat: 'mp4',
        width: 1280,
        height: 720,
        videoBitrate: '1000k',
        tempDir,
      };

      const inputStream = Readable.from(inputBuffer);
      const result = await converter.convertStream(inputStream, mockOutputStream, options);

      expect(result.success).toBe(true);
      expect(result.data).toBeDefined();
      expect(result.data!.metadata.width).toBeLessThanOrEqual(1280);
      expect(result.data!.metadata.height).toBeLessThanOrEqual(720);
    });

    it('should emit progress events during conversion', async () => {
      const options: ConversionOptions = {
        targetFormat: 'mp4',
        videoBitrate: '1000k',
        chunkSize: 1024,
        tempDir,
      };

      const progressEvents: Array<{ bytesProcessed: number; totalBytes: number }> = [];
      converter.on('progress', (progress) => {
        progressEvents.push(progress);
      });

      const inputStream = Readable.from(inputBuffer);
      await converter.convertStream(inputStream, mockOutputStream, options);

      expect(progressEvents.length).toBeGreaterThan(0);
      expect(progressEvents[progressEvents.length - 1].bytesProcessed).toBe(progressEvents[progressEvents.length - 1].totalBytes);
    });

    it('should handle errors gracefully', async () => {
      const options: ConversionOptions = {
        targetFormat: 'invalid',
        tempDir,
      };

      const inputStream = Readable.from(inputBuffer);
      const result = await converter.convertStream(inputStream, mockOutputStream, options);

      expect(result.success).toBe(false);
      expect(result.error).toBeDefined();
      expect(result.error!.code).toBe('UnsupportedFormat');
    });

    it('should handle stream errors', async () => {
      const options: ConversionOptions = {
        targetFormat: 'mp4',
        tempDir,
      };

      const errorStream = new Readable({
        read() {
          this.destroy(new Error('Stream error'));
        }
      });

      const result = await converter.convertStream(errorStream, mockOutputStream, options);

      expect(result.success).toBe(false);
      expect(result.error).toBeDefined();
    });

    it('should clean up temporary files after conversion', async () => {
      const options: ConversionOptions = {
        targetFormat: 'mp4',
        tempDir,
      };

      const inputStream = Readable.from(inputBuffer);
      await converter.convertStream(inputStream, mockOutputStream, options);

      // Check if directory is empty
      const files = await fs.readdir(tempDir);
      expect(files.length).toBe(0);
    });
  });

  describe('getSupportedFormats', () => {
    it('should return supported input formats', () => {
      const formats = converter.getSupportedInputFormats();
      expect(formats).toContain('mp4');
      expect(formats).toContain('webm');
      expect(formats).toContain('mov');
    });

    it('should return supported output formats', () => {
      const formats = converter.getSupportedOutputFormats();
      expect(formats).toContain('mp4');
      expect(formats).toContain('webm');
      expect(formats).toContain('mov');
    });
  });
}); 