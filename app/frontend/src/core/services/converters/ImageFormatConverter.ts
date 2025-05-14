import sharp from 'sharp';
import { lookup } from 'mime-types';
import { createReadStream, createWriteStream } from 'fs';
import { BaseFormatConverter } from './BaseFormatConverter';
import { 
  ConversionOptions, 
  ConversionResult, 
  StreamConversionResult 
} from './FormatConverter';
import { ServiceResponse, ServiceError } from '../base/types';
import { promises as fs } from 'fs';
import { ValidationError } from '../../errors/ValidationError';
import { Readable, Writable } from 'stream';
import { v4 as uuidv4 } from 'uuid';
import path from 'path';
import * as os from 'os';
import { StreamProcessingResult, ConversionMetadata } from '../types/MediaProcessing';

interface ImageConversionOptions extends ConversionOptions {
  compressionLevel?: number;
}

interface ExtendedConversionOptions extends ConversionOptions {
  compressionLevel?: number;
}

interface SharpFormatOptions {
  jpeg: sharp.JpegOptions;
  png: sharp.PngOptions;
  webp: sharp.WebpOptions;
  avif: sharp.AvifOptions;
  tiff: sharp.TiffOptions;
}

export class ImageFormatConverter extends BaseFormatConverter {
  private readonly supportedInputFormats = [
    'jpeg', 'jpg', 'png', 'webp', 'avif', 'tiff', 'gif'
  ];

  private readonly supportedOutputFormats = [
    'jpeg', 'jpg', 'png', 'webp', 'avif', 'tiff'
  ];

  private readonly tempDir: string;
  protected readonly defaultOptions: ExtendedConversionOptions;
  private startTime: number;
  private conversionStartTime: number;

  constructor(tempDir: string = path.join(process.cwd(), 'temp')) {
    super();
    this.tempDir = tempDir;
    this.defaultOptions = {
      targetFormat: '',
      quality: 80,
      compressionLevel: 6,
      chunkSize: 64 * 1024, // 64KB chunks
    };
    this.startTime = Date.now();
    this.conversionStartTime = this.startTime;
  }

  canConvertFrom(mimeType: string): boolean {
    return this.supportedInputFormats.includes(mimeType.toLowerCase());
  }

  canConvertTo(format: string): boolean {
    return this.supportedOutputFormats.includes(format.toLowerCase());
  }

  getSupportedInputFormats(): string[] {
    return this.supportedInputFormats;
  }

  getSupportedOutputFormats(): string[] {
    return this.supportedOutputFormats;
  }

  protected async validateOptions(options?: ConversionOptions): Promise<ExtendedConversionOptions> {
    const mergedOptions = await super.validateOptions(options);
    return {
      ...mergedOptions,
      compressionLevel: (options as ExtendedConversionOptions)?.compressionLevel || this.defaultOptions.compressionLevel
    };
  }

  async convert(input: Buffer | string, options?: ConversionOptions): Promise<ServiceResponse<ConversionResult>> {
    try {
      // Validate input and options
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
          fit: 'inside',
          withoutEnlargement: true
        });
      }

      // Apply quality settings based on format
      let formatOptions: any = {};
      switch (mergedOptions.targetFormat.toLowerCase()) {
        case 'jpeg':
          formatOptions = {
            quality: mergedOptions.quality,
            mozjpeg: true
          };
          break;
        case 'png':
          formatOptions = {
            compressionLevel: mergedOptions.compressionLevel,
            palette: true
          };
          break;
        case 'webp':
          formatOptions = {
            quality: mergedOptions.quality,
            lossless: false
          };
          break;
        case 'tiff':
          formatOptions = {
            quality: mergedOptions.quality,
            compression: 'jpeg'
          };
          break;
        case 'avif':
          formatOptions = {
            quality: mergedOptions.quality,
            lossless: false,
            effort: 4
          };
          break;
      }

      // Convert to target format
      pipeline = pipeline.toFormat(mergedOptions.targetFormat as keyof sharp.FormatEnum, formatOptions);

      // Process the image
      const outputBuffer = await pipeline.toBuffer({ resolveWithObject: true });
      const endTime = Date.now();

      // Update conversion stats
      this.updateStats(true, input, outputBuffer.data, endTime - startTime);

      // Return the result
      return {
        success: true,
        data: {
          data: outputBuffer.data,
          metadata: {
            format: mergedOptions.targetFormat,
            size: outputBuffer.data.length,
            width: outputBuffer.info.width,
            height: outputBuffer.info.height,
            createdAt: new Date()
          },
          originalFormat,
          conversionTime: endTime - startTime
        }
      };
    } catch (error) {
      this.logger.error('Image conversion failed:', error);
      return {
        success: false,
        data: null,
        error: new ServiceError('IMAGE_CONVERSION_ERROR', error instanceof Error ? error.message : String(error))
      };
    }
  }

  async cleanup(): Promise<void> {
    await super.cleanup();
    // Add any image-specific cleanup if needed
  }

  protected async processStream(
    inputStream: Readable,
    outputStream: Writable,
    options: ConversionOptions,
    onProgress: (bytesProcessed: number) => void
  ): Promise<ServiceResponse<StreamConversionResult>> {
    let tempInputPath: string | undefined;
    let tempOutputPath: string | undefined;
    const startTime = Date.now();

    try {
      // Create temp directory if it doesn't exist
      await fs.mkdir(this.tempDir, { recursive: true });

      // Create temporary files for input and output
      tempInputPath = path.join(this.tempDir, `stream-input-${uuidv4()}`);
      tempOutputPath = path.join(this.tempDir, `stream-output-${uuidv4()}.${options.targetFormat}`);

      // Write input stream to temporary file
      const writeStream = createWriteStream(tempInputPath);
      let bytesWritten = 0;

      await new Promise<void>((resolve, reject) => {
        inputStream.on('data', (chunk: Buffer | string) => {
          const buffer = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk);
          bytesWritten += buffer.length;
          onProgress(bytesWritten);
          writeStream.write(buffer);
        });
        inputStream.on('end', () => {
          writeStream.end();
          resolve();
        });
        inputStream.on('error', reject);
        writeStream.on('error', reject);
      });

      // Create Sharp pipeline
      let pipeline = sharp(tempInputPath);

      // Get original metadata
      const metadata = await pipeline.metadata();
      const originalFormat = metadata.format || 'unknown';

      // Configure conversion options
      if (options.width || options.height) {
        pipeline = pipeline.resize({
          width: options.width,
          height: options.height,
          fit: 'inside',
          withoutEnlargement: true
        });
      }

      // Apply quality settings based on format
      let formatOptions: any = {};
      const imageOptions = await this.validateOptions(options);
      switch (options.targetFormat.toLowerCase()) {
        case 'jpeg':
          formatOptions = {
            quality: options.quality,
            mozjpeg: true
          };
          break;
        case 'png':
          formatOptions = {
            compressionLevel: imageOptions.compressionLevel,
            palette: true
          };
          break;
        case 'webp':
          formatOptions = {
            quality: options.quality,
            lossless: false
          };
          break;
        case 'tiff':
          formatOptions = {
            quality: options.quality,
            compression: 'jpeg'
          };
          break;
        case 'avif':
          formatOptions = {
            quality: options.quality,
            lossless: false,
            effort: 4
          };
          break;
      }

      // Convert to target format
      pipeline = pipeline.toFormat(options.targetFormat as keyof sharp.FormatEnum, formatOptions);

      // Process the image and write to output file
      await pipeline.toFile(tempOutputPath);

      // Read the output file in chunks and write to output stream
      const readStream = createReadStream(tempOutputPath, {
        highWaterMark: options.chunkSize || this.defaultOptions.chunkSize
      });

      await new Promise<void>((resolve, reject) => {
        readStream.on('data', (chunk: Buffer | string) => {
          const buffer = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk);
          outputStream.write(buffer);
        });
        readStream.on('end', () => {
          outputStream.end();
          resolve();
        });
        readStream.on('error', reject);
        outputStream.on('error', reject);
      });

      // Get output metadata
      const outputMetadata = await sharp(tempOutputPath).metadata();
      const stats = await fs.stat(tempOutputPath);
      const endTime = Date.now();
      const conversionTime = endTime - startTime;

      // Update stats
      this.updateStats(true, inputStream, outputStream, conversionTime);

      return {
        success: true,
        data: {
          metadata: {
            format: options.targetFormat,
            size: stats.size,
            width: outputMetadata.width,
            height: outputMetadata.height,
            createdAt: new Date()
          },
          originalFormat,
          conversionTime
        }
      };

    } catch (error) {
      this.logger.error('Stream processing failed:', error);
      return {
        success: false,
        data: null,
        error: new ServiceError('STREAM_PROCESSING_ERROR', error instanceof Error ? error.message : String(error))
      };
    } finally {
      // Clean up temporary files
      try {
        if (tempInputPath) {
          await fs.unlink(tempInputPath);
        }
        if (tempOutputPath) {
          await fs.unlink(tempOutputPath);
        }
      } catch (cleanupError) {
        this.logger.warn('Error cleaning up temporary files:', cleanupError);
      }
    }
  }

  public async convertStream(
    inputStream: Readable,
    outputStream: Writable,
    options: ConversionOptions
  ): Promise<ServiceResponse<StreamProcessingResult>> {
    try {
      this.startTime = Date.now();

      // Validate formats
      const format = options.targetFormat.toLowerCase();
      if (!this.supportedOutputFormats.includes(format)) {
        throw new ServiceError(
          'UnsupportedFormat',
          `Unsupported output format: ${format}`,
          { supportedFormats: this.supportedOutputFormats }
        );
      }

      // Create temporary files for processing
      const tempDir = options.tempDir || os.tmpdir();
      const tempInputPath = path.join(tempDir, `input-${Date.now()}.tmp`);
      const tempOutputPath = path.join(tempDir, `output-${Date.now()}.${format}`);

      try {
        // Write input stream to temporary file
        const writeStream = createWriteStream(tempInputPath);
        await new Promise<void>((resolve, reject) => {
          inputStream.pipe(writeStream)
            .on('finish', resolve)
            .on('error', reject);
        });

        // Process the image using sharp
        const sharpInstance = sharp(tempInputPath);

        // Configure conversion options based on format
        const formatOptions: Partial<SharpFormatOptions> = {
          jpeg: {
            quality: options.quality || this.defaultOptions.quality,
            chromaSubsampling: '4:4:4',
          },
          png: {
            compressionLevel: options.compression ? 9 : 6,
          },
          webp: {
            quality: options.quality || this.defaultOptions.quality,
            lossless: options.compression === false,
          },
          avif: {
            quality: options.quality || this.defaultOptions.quality,
            lossless: options.compression === false,
          },
          tiff: {
            quality: options.quality || this.defaultOptions.quality,
            compression: options.compression ? 'lzw' : 'none',
          },
        };

        const formatKey = format === 'jpg' ? 'jpeg' : format;
        const formatOption = formatOptions[formatKey as keyof SharpFormatOptions];
        
        if (formatOption) {
          sharpInstance.toFormat(formatKey as keyof sharp.FormatEnum, formatOption);
        } else {
          sharpInstance.toFormat(formatKey as keyof sharp.FormatEnum);
        }

        // Apply resizing if dimensions are specified
        if (options.width || options.height) {
          sharpInstance.resize(options.width, options.height, {
            fit: 'inside',
            withoutEnlargement: true,
          });
        }

        // Start conversion timing
        this.conversionStartTime = Date.now();

        // Process the image and get metadata
        const metadata = await sharpInstance.metadata();
        const outputBuffer = await sharpInstance.toBuffer();

        // Calculate conversion time
        const conversionTime = Date.now() - this.conversionStartTime;

        // Write to output stream in chunks
        const chunkSize = Math.max(
          options.chunkSize || this.defaultOptions.chunkSize,
          1024 // Minimum 1KB chunks
        );
        
        let bytesProcessed = 0;
        
        for (let i = 0; i < outputBuffer.length; i += chunkSize) {
          const chunk = outputBuffer.slice(i, Math.min(i + chunkSize, outputBuffer.length));
          bytesProcessed += chunk.length;
          
          // Emit progress
          this.emit('progress', {
            bytesProcessed,
            totalBytes: outputBuffer.length,
          });
          
          // Write chunk to output stream with backpressure handling
          if (!outputStream.write(chunk)) {
            await new Promise(resolve => outputStream.once('drain', resolve));
          }
        }
        
        // End the output stream
        outputStream.end();

        // Prepare metadata (ensure all required fields are present)
        const conversionMetadata: ConversionMetadata = {
          format: metadata.format || format,
          width: metadata.width || 0,
          height: metadata.height || 0,
          channels: metadata.channels || 0,
          size: outputBuffer.length,
          codec: metadata.compression || undefined,
          bitrate: undefined,
          duration: undefined,
        };

        return {
          success: true,
          data: {
            bytesProcessed,
            totalBytes: outputBuffer.length,
            processingTime: Date.now() - this.startTime,
            conversionTime,
            originalFormat: metadata.format || 'unknown',
            metadata: conversionMetadata,
          },
        };
      } finally {
        // Clean up temporary files
        await fs.unlink(tempInputPath).catch(() => {});
        if (await fs.access(tempOutputPath).then(() => true, () => false)) {
          await fs.unlink(tempOutputPath).catch(() => {});
        }
      }
    } catch (error) {
      return {
        success: false,
        error: error instanceof ServiceError ? error : new ServiceError(
          'ProcessingError',
          'Failed to process image stream',
          { error }
        ),
        data: null,
      };
    }
  }
} 