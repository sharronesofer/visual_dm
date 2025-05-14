import { promises as fs } from 'fs';
import fs_sync from 'fs';
import path from 'path';
import { ImageMetadataExtractor } from '../ImageMetadataExtractor';
import { VideoMetadataExtractor } from '../VideoMetadataExtractor';
import { AudioMetadataExtractor } from '../AudioMetadataExtractor';
import { DocumentMetadataExtractor } from '../DocumentMetadataExtractor';
import { MetadataExtractorFactory } from '../MetadataExtractorFactory';

const testFilesDir = path.join(__dirname, '../../../../test/fixtures/media');

describe('MetadataExtractors', () => {
  let imageExtractor: ImageMetadataExtractor;
  let videoExtractor: VideoMetadataExtractor;
  let audioExtractor: AudioMetadataExtractor;
  let documentExtractor: DocumentMetadataExtractor;
  let factory: MetadataExtractorFactory;

  beforeAll(async () => {
    // Create test files directory if it doesn't exist
    await fs.mkdir(testFilesDir, { recursive: true });

    // Initialize extractors
    imageExtractor = new ImageMetadataExtractor();
    videoExtractor = new VideoMetadataExtractor();
    audioExtractor = new AudioMetadataExtractor();
    documentExtractor = new DocumentMetadataExtractor();
    factory = MetadataExtractorFactory.getInstance();
  });

  describe('ImageMetadataExtractor', () => {
    it('should handle supported image types', () => {
      expect(imageExtractor.canHandle('image/jpeg')).toBe(true);
      expect(imageExtractor.canHandle('image/png')).toBe(true);
      expect(imageExtractor.canHandle('image/gif')).toBe(true);
      expect(imageExtractor.canHandle('image/webp')).toBe(true);
      expect(imageExtractor.canHandle('video/mp4')).toBe(false);
    });

    it('should extract metadata from JPEG image', async () => {
      const testImage = path.join(testFilesDir, 'test.jpg');
      await createTestJpeg(testImage);

      const result = await imageExtractor.extract(testImage);
      expect(result.success).toBe(true);
      expect(result.data?.metadata).toBeDefined();
      expect(result.data?.metadata.format).toBe('jpeg');
      expect(result.data?.metadata.width).toBeGreaterThan(0);
      expect(result.data?.metadata.height).toBeGreaterThan(0);

      await fs.unlink(testImage);
    });
  });

  describe('VideoMetadataExtractor', () => {
    it('should handle supported video types', () => {
      expect(videoExtractor.canHandle('video/mp4')).toBe(true);
      expect(videoExtractor.canHandle('video/webm')).toBe(true);
      expect(videoExtractor.canHandle('video/x-matroska')).toBe(true);
      expect(videoExtractor.canHandle('image/jpeg')).toBe(false);
    });

    it('should extract metadata from MP4 video', async () => {
      const testVideo = path.join(testFilesDir, 'test.mp4');
      await createTestMp4(testVideo);

      const result = await videoExtractor.extract(testVideo);
      expect(result.success).toBe(true);
      expect(result.data?.metadata).toBeDefined();
      expect(result.data?.metadata.format).toBe('mp4');
      expect(result.data?.metadata.duration).toBeGreaterThan(0);
      expect(result.data?.metadata.videoCodec).toBeDefined();

      await fs.unlink(testVideo);
    });
  });

  describe('AudioMetadataExtractor', () => {
    it('should handle supported audio types', () => {
      expect(audioExtractor.canHandle('audio/mpeg')).toBe(true);
      expect(audioExtractor.canHandle('audio/mp4')).toBe(true);
      expect(audioExtractor.canHandle('audio/ogg')).toBe(true);
      expect(audioExtractor.canHandle('video/mp4')).toBe(false);
    });

    it('should extract metadata from MP3 audio', async () => {
      const testAudio = path.join(testFilesDir, 'test.mp3');
      await createTestMp3(testAudio);

      const result = await audioExtractor.extract(testAudio);
      expect(result.success).toBe(true);
      expect(result.data?.metadata).toBeDefined();
      expect(result.data?.metadata.format).toBe('mp3');
      expect(result.data?.metadata.duration).toBeGreaterThan(0);
      expect(result.data?.metadata.audioCodec).toBeDefined();

      await fs.unlink(testAudio);
    });
  });

  describe('DocumentMetadataExtractor', () => {
    it('should handle supported document types', () => {
      expect(documentExtractor.canHandle('application/pdf')).toBe(true);
      expect(documentExtractor.canHandle('application/vnd.openxmlformats-officedocument.wordprocessingml.document')).toBe(true);
      expect(documentExtractor.canHandle('text/plain')).toBe(true);
      expect(documentExtractor.canHandle('image/jpeg')).toBe(false);
    });

    it('should extract metadata from PDF document', async () => {
      const testPdf = path.join(testFilesDir, 'test.pdf');
      await createTestPdf(testPdf);

      const result = await documentExtractor.extract(testPdf);
      expect(result.success).toBe(true);
      expect(result.data?.metadata).toBeDefined();
      expect(result.data?.metadata.format).toBe('pdf');
      expect(result.data?.metadata.custom?.pageCount).toBeGreaterThan(0);

      await fs.unlink(testPdf);
    });
  });

  describe('MetadataExtractorFactory', () => {
    it('should return appropriate extractor for media type', () => {
      expect(factory.getExtractor('image/jpeg')).toBeInstanceOf(ImageMetadataExtractor);
      expect(factory.getExtractor('video/mp4')).toBeInstanceOf(VideoMetadataExtractor);
      expect(factory.getExtractor('audio/mpeg')).toBeInstanceOf(AudioMetadataExtractor);
      expect(factory.getExtractor('application/pdf')).toBeInstanceOf(DocumentMetadataExtractor);
    });

    it('should throw error for unsupported media type', () => {
      expect(() => factory.getExtractor('invalid/type')).toThrow('UnsupportedMediaType');
    });

    it('should return all supported types', () => {
      const supportedTypes = factory.getSupportedTypes();
      expect(supportedTypes).toContain('image/jpeg');
      expect(supportedTypes).toContain('video/mp4');
      expect(supportedTypes).toContain('audio/mpeg');
      expect(supportedTypes).toContain('application/pdf');
    });
  });
});

// Test file creation helpers
async function createTestJpeg(filePath: string): Promise<void> {
  // Create a simple JPEG file using Sharp
  const sharp = require('sharp');
  await sharp({
    create: {
      width: 100,
      height: 100,
      channels: 3,
      background: { r: 255, g: 0, b: 0 }
    }
  })
  .jpeg()
  .toFile(filePath);
}

async function createTestMp4(filePath: string): Promise<void> {
  // Create a simple MP4 file using FFmpeg
  const ffmpeg = require('fluent-ffmpeg');
  await new Promise<void>((resolve, reject) => {
    ffmpeg()
      .input('color=c=red:s=100x100:d=1')
      .inputFormat('lavfi')
      .output(filePath)
      .on('end', () => resolve())
      .on('error', (err: Error) => reject(err))
      .run();
  });
}

async function createTestMp3(filePath: string): Promise<void> {
  // Create a simple MP3 file using FFmpeg
  const ffmpeg = require('fluent-ffmpeg');
  await new Promise<void>((resolve, reject) => {
    ffmpeg()
      .input('anullsrc=r=44100:cl=mono')
      .inputFormat('lavfi')
      .duration(1)
      .output(filePath)
      .on('end', () => resolve())
      .on('error', (err: Error) => reject(err))
      .run();
  });
}

async function createTestPdf(filePath: string): Promise<void> {
  // Create a simple PDF file using PDFKit
  const PDFDocument = require('pdfkit');
  const doc = new PDFDocument();
  const writeStream = fs_sync.createWriteStream(filePath);
  
  await new Promise<void>((resolve, reject) => {
    doc.pipe(writeStream);
    doc.text('Test PDF Document');
    doc.end();
    writeStream.on('finish', () => resolve());
    writeStream.on('error', (err: Error) => reject(err));
  });
} 