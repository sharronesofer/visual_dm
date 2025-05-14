import { EventEmitter } from 'events';
import { promises as fs } from 'fs';
import { createWriteStream } from 'fs';
import { lookup } from 'mime-types';
import { v4 as uuidv4 } from 'uuid';
import path from 'path';
import { Readable } from 'stream';
import {
  MetadataExtractor,
  MediaMetadata,
  MetadataExtractionOptions,
  MetadataExtractionProgress,
  MetadataExtractionResult
} from './MetadataExtractor';
import { ServiceResponse, ServiceError } from '../base/types';
import { Logger } from '../../utils/logger';
import { ValidationError } from '../../errors/ValidationError';

export abstract class BaseMetadataExtractor extends EventEmitter implements MetadataExtractor {
  protected readonly logger: Logger;
  protected readonly tempDir: string;
  protected readonly defaultOptions: MetadataExtractionOptions = {
    extractExif: true,
    extractIptc: true,
    extractXmp: true,
    extractId3: true,
    computeHash: false,
    computeColorProfile: false,
    useCache: true,
    maxBufferSize: 100 * 1024 * 1024, // 100MB
    timeout: 30000 // 30 seconds
  };

  constructor(tempDir: string = path.join(process.cwd(), 'temp')) {
    super();
    this.logger = Logger.getInstance().child(this.constructor.name);
    this.tempDir = tempDir;
  }

  abstract canHandle(mimeType: string): boolean;
  abstract getSupportedTypes(): string[];
  protected abstract processExtraction(
    input: Buffer | string,
    options: MetadataExtractionOptions
  ): Promise<ServiceResponse<MetadataExtractionResult>>;

  public async extract(
    input: Buffer | string | Readable,
    options?: MetadataExtractionOptions
  ): Promise<ServiceResponse<MetadataExtractionResult>> {
    const startTime = Date.now();
    let tempFilePath: string | undefined;

    try {
      // Validate input
      if (!input) {
        throw new ValidationError('Input is required');
      }

      // Validate options first
      const isValid = await this.validateOptions(options);
      if (!isValid) {
        throw new ValidationError('Invalid options provided');
      }

      // Merge and validate options internally
      const mergedOptions = await this.validateOptionsInternal(options);

      // Handle stream input by writing to temp file
      if (input instanceof Readable) {
        tempFilePath = await this.handleStreamInput(input, mergedOptions);
        input = tempFilePath;
      }

      // Process the extraction
      const result = await this.processExtraction(input, mergedOptions);

      // Add extraction time to result
      if (result.success && result.data) {
        result.data.extractionTime = Date.now() - startTime;
      }

      return result;
    } catch (error) {
      return this.handleError(error);
    } finally {
      // Clean up temp file if created
      if (tempFilePath) {
        await this.cleanup(tempFilePath);
      }
    }
  }

  public async extractBatch(
    inputs: Array<Buffer | string | Readable>,
    options?: MetadataExtractionOptions
  ): Promise<ServiceResponse<MetadataExtractionResult[]>> {
    try {
      const results = await Promise.all(
        inputs.map(input => this.extract(input, options))
      );

      // Check if any extractions failed
      const failures = results.filter(result => !result.success);
      if (failures.length > 0) {
        const serviceError: ServiceError = {
          code: 'BATCH_EXTRACTION_ERROR',
          message: `${failures.length} extractions failed`,
          status: 500
        };
        return {
          success: false,
          error: serviceError,
          data: results.map(result => result.data).filter(Boolean) as MetadataExtractionResult[]
        };
      }

      return {
        success: true,
        data: results.map(result => result.data!),
      };
    } catch (error) {
      return this.handleError(error);
    }
  }

  public async validateOptions(options?: MetadataExtractionOptions): Promise<boolean> {
    try {
      const mergedOptions = {
        ...this.defaultOptions,
        ...options
      };

      if (mergedOptions.maxBufferSize && mergedOptions.maxBufferSize < 0) {
        throw new ValidationError('maxBufferSize must be positive');
      }

      if (mergedOptions.timeout && mergedOptions.timeout < 0) {
        throw new ValidationError('timeout must be positive');
      }

      return true;
    } catch (error) {
      return false;
    }
  }

  protected async validateOptionsInternal(options?: MetadataExtractionOptions): Promise<MetadataExtractionOptions> {
    const mergedOptions = {
      ...this.defaultOptions,
      ...options
    };

    if (mergedOptions.maxBufferSize && mergedOptions.maxBufferSize < 0) {
      throw new ValidationError('maxBufferSize must be positive');
    }

    if (mergedOptions.timeout && mergedOptions.timeout < 0) {
      throw new ValidationError('timeout must be positive');
    }

    return mergedOptions;
  }

  public getDefaultOptions(): MetadataExtractionOptions {
    return { ...this.defaultOptions };
  }

  public addEventListener(
    event: 'progress',
    handler: (progress: MetadataExtractionProgress) => void
  ): void {
    this.on(event, handler);
  }

  public removeEventListener(
    event: 'progress',
    handler: (progress: MetadataExtractionProgress) => void
  ): void {
    this.off(event, handler);
  }

  public async cleanup(tempFilePath?: string): Promise<void> {
    if (tempFilePath) {
      try {
        await fs.unlink(tempFilePath);
      } catch (error) {
        this.logger.warn('Failed to delete temp file:', { error, path: tempFilePath });
      }
    }
  }

  protected async handleStreamInput(
    stream: Readable,
    options: MetadataExtractionOptions
  ): Promise<string> {
    // Create temp directory if it doesn't exist
    await fs.mkdir(this.tempDir, { recursive: true });

    // Create temp file path
    const tempFilePath = path.join(this.tempDir, `stream-${uuidv4()}`);
    const writeStream = createWriteStream(tempFilePath);

    let bytesProcessed = 0;
    const startTime = Date.now();

    return new Promise((resolve, reject) => {
      stream.on('data', (chunk: Buffer) => {
        bytesProcessed += chunk.length;

        // Check buffer size limit
        if (options.maxBufferSize && bytesProcessed > options.maxBufferSize) {
          stream.destroy();
          writeStream.destroy();
          reject(new Error('Input stream exceeds maximum buffer size'));
          return;
        }

        // Emit progress
        this.emit('progress', {
          bytesProcessed,
          totalBytes: -1, // Unknown for streams
          stage: 'reading',
          percentage: -1
        });

        writeStream.write(chunk);
      });

      stream.on('end', () => {
        writeStream.end();
        resolve(tempFilePath);
      });

      stream.on('error', (error) => {
        writeStream.destroy();
        reject(error);
      });

      // Handle timeout
      if (options.timeout) {
        setTimeout(() => {
          stream.destroy();
          writeStream.destroy();
          reject(new Error('Stream processing timed out'));
        }, options.timeout);
      }
    });
  }

  protected handleError(error: unknown): ServiceResponse<any> {
    const errorMessage = error instanceof Error ? error.message : String(error);
    this.logger.error('Metadata extraction error:', { error: errorMessage });

    const serviceError: ServiceError = {
      code: 'METADATA_EXTRACTION_ERROR',
      message: errorMessage,
      status: error instanceof ValidationError ? 400 : 500
    };

    return {
      success: false,
      error: serviceError,
      data: null
    };
  }

  protected emitProgress(progress: MetadataExtractionProgress): void {
    this.emit('progress', progress);
  }

  protected async validateInput(input: Buffer | string): Promise<boolean> {
    try {
      if (Buffer.isBuffer(input)) {
        return true;
      }

      // Check if file exists and is readable
      await fs.access(input, fs.constants.R_OK);
      return true;
    } catch (error) {
      throw new ValidationError('Invalid input: file does not exist or is not readable');
    }
  }

  protected getMimeType(input: Buffer | string): string {
    if (typeof input === 'string') {
      return lookup(input) || 'application/octet-stream';
    }
    // For buffers, we'll need to implement magic number detection
    // or rely on the specific extractor implementation
    return 'application/octet-stream';
  }
} 