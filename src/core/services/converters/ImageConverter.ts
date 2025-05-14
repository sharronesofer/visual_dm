import { BaseFormatConverter } from './FormatConverter';
import { ConversionOptions, ConversionResult, ServiceResponse, StreamProcessingResult } from './FormatConverter';
import { Readable, Writable } from 'stream';
import { ServiceError } from '../base/types';
import sharp from 'sharp';
import { promises as fs } from 'fs';
import * as fs_sync from 'fs';
import * as os from 'os';
import * as path from 'path';
import { v4 as uuidv4 } from 'uuid';

export class ImageConverter extends BaseFormatConverter {
  private readonly inputFormats = ['jpeg', 'png', 'gif', 'webp', 'tiff', 'bmp'];
  private readonly outputFormats = ['jpeg', 'png', 'gif', 'webp'];
  private readonly defaultOptions: ConversionOptions = {
    targetFormat: 'jpeg',
    quality: 80,
    compressionLevel: 6,
    chunkSize: 64 * 1024, // 64KB chunks
    preserveMetadata: false,
    preserveAspectRatio: true
  };

  public getSupportedInputFormats(): string[] {
    return [...this.inputFormats];
  }

  public getSupportedOutputFormats(): string[] {
    return [...this.outputFormats];
  }

  public canConvertTo(format: string): boolean {
    return this.outputFormats.includes(format.toLowerCase());
  }

  private async validateInput(input: Buffer | string): Promise<void> {
    if (typeof input === 'string') {
      try {
        await fs.access(input);
      } catch {
        throw new ServiceError('InvalidInput', 'Input file does not exist', { input });
      }
    } else if (!Buffer.isBuffer(input)) {
      throw new ServiceError('InvalidInput', 'Input must be a Buffer or file path', { input });
    }
  }

  private async validateOptions(options: ConversionOptions): Promise<ConversionOptions> {
    const mergedOptions = { ...this.defaultOptions, ...options };

    if (!mergedOptions.targetFormat) {
      throw new ServiceError('InvalidOptions', 'Target format is required');
    }

    if (!this.canConvertTo(mergedOptions.targetFormat)) {
      throw new ServiceError(
        'UnsupportedFormat',
        `Unsupported output format: ${mergedOptions.targetFormat}`,
        { supportedFormats: this.outputFormats }
      );
    }

    return mergedOptions;
  }

  public async convert(
    input: Buffer | string,
    options: ConversionOptions
  ): Promise<ServiceResponse<ConversionResult>> {
    try {
      await this.validateInput(input);
      const mergedOptions = await this.validateOptions(options);

      // Read input if it's a file path
      let inputBuffer: Buffer;
      if (typeof input === 'string') {
        inputBuffer = await fs.readFile(input);
      } else {
        inputBuffer = input;
      }

      const startTime = Date.now();
      let pipeline = sharp(inputBuffer);

      // Get original metadata
      const metadata = await pipeline.metadata();
      const originalFormat = metadata.format || 'unknown';

      // Configure conversion options
      if (mergedOptions.width || mergedOptions.height) {
        pipeline = pipeline.resize({
          width: mergedOptions.width,
          height: mergedOptions.height,
          fit: mergedOptions.preserveAspectRatio ? 'inside' : 'fill',
          withoutEnlargement: true
        });
      }

      // Apply format-specific options
      const formatOptions: any = {
        quality: mergedOptions.quality
      };

      switch (mergedOptions.targetFormat.toLowerCase()) {
        case 'jpeg':
          formatOptions.mozjpeg = true;
          break;
        case 'png':
          formatOptions.compressionLevel = mergedOptions.compressionLevel;
          formatOptions.palette = true;
          break;
        case 'webp':
          formatOptions.lossless = false;
          break;
        case 'gif':
          // GIF-specific options if needed
          break;
      }

      // Convert to target format
      pipeline = pipeline.toFormat(mergedOptions.targetFormat as keyof sharp.FormatEnum, formatOptions);

      // Process the image
      const { data, info } = await pipeline.toBuffer({ resolveWithObject: true });

      const result: ConversionResult = {
        data,
        format: mergedOptions.targetFormat,
        size: data.length,
        width: info.width,
        height: info.height
      };

      return {
        success: true,
        data: result
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof ServiceError ? error : new ServiceError(
          'ConversionError',
          'Failed to convert image',
          { error }
        ),
        data: null
      };
    }
  }

  public async convertStream(
    inputStream: Readable,
    outputStream: Writable,
    options: ConversionOptions
  ): Promise<ServiceResponse<StreamProcessingResult>> {
    let tempInputPath: string | undefined;
    let tempOutputPath: string | undefined;
    const startTime = Date.now();

    try {
      const mergedOptions = await this.validateOptions(options);
      const tempDir = mergedOptions.tempDir || os.tmpdir();

      // Create temporary files
      tempInputPath = path.join(tempDir, `input-${uuidv4()}`);
      tempOutputPath = path.join(tempDir, `output-${uuidv4()}.${mergedOptions.targetFormat}`);

      // Write input stream to temporary file
      const writeStream = fs_sync.createWriteStream(tempInputPath);
      let bytesProcessed = 0;

      await new Promise<void>((resolve, reject) => {
        inputStream.on('data', (chunk: Buffer) => {
          bytesProcessed += chunk.length;
          writeStream.write(chunk);
          this.emit('progress', { bytesProcessed });
        });
        inputStream.on('end', () => {
          writeStream.end();
          resolve();
        });
        inputStream.on('error', reject);
        writeStream.on('error', reject);
      });

      // Process the image using sharp
      let pipeline = sharp(tempInputPath);
      const metadata = await pipeline.metadata();
      const originalFormat = metadata.format || 'unknown';

      // Configure conversion options
      if (mergedOptions.width || mergedOptions.height) {
        pipeline = pipeline.resize({
          width: mergedOptions.width,
          height: mergedOptions.height,
          fit: mergedOptions.preserveAspectRatio ? 'inside' : 'fill',
          withoutEnlargement: true
        });
      }

      // Apply format-specific options
      const formatOptions: any = {
        quality: mergedOptions.quality
      };

      switch (mergedOptions.targetFormat.toLowerCase()) {
        case 'jpeg':
          formatOptions.mozjpeg = true;
          break;
        case 'png':
          formatOptions.compressionLevel = mergedOptions.compressionLevel;
          formatOptions.palette = true;
          break;
        case 'webp':
          formatOptions.lossless = false;
          break;
        case 'gif':
          // GIF-specific options if needed
          break;
      }

      // Convert to target format
      pipeline = pipeline.toFormat(mergedOptions.targetFormat as keyof sharp.FormatEnum, formatOptions);

      // Process the image and write to output file
      await pipeline.toFile(tempOutputPath);

      // Read the output file in chunks and write to output stream
      const readStream = fs_sync.createReadStream(tempOutputPath, {
        highWaterMark: mergedOptions.chunkSize
      });

      let totalBytes = 0;
      await new Promise<void>((resolve, reject) => {
        readStream.on('data', (chunk: Buffer) => {
          totalBytes += chunk.length;
          if (!outputStream.write(chunk)) {
            readStream.pause();
          }
        });
        outputStream.on('drain', () => {
          readStream.resume();
        });
        readStream.on('end', () => {
          outputStream.end();
          resolve();
        });
        readStream.on('error', reject);
        outputStream.on('error', reject);
      });

      const endTime = Date.now();
      const processingTime = endTime - startTime;

      return {
        success: true,
        data: {
          bytesProcessed: totalBytes,
          totalBytes,
          processingTime,
          originalFormat,
          format: mergedOptions.targetFormat,
          size: totalBytes
        }
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof ServiceError ? error : new ServiceError(
          'StreamConversionError',
          'Failed to convert image stream',
          { error }
        ),
        data: null
      };
    } finally {
      // Clean up temporary files
      if (tempInputPath) {
        await fs.unlink(tempInputPath).catch(() => {});
      }
      if (tempOutputPath) {
        await fs.unlink(tempOutputPath).catch(() => {});
      }
    }
  }
} 