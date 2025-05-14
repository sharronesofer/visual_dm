/// <reference types="node" />
import { TypedEventEmitter } from '../../utils/TypedEventEmitter';
import { lookup } from 'mime-types';
import { Logger } from '../../utils/logger';
import { ValidationError } from '../../errors/ValidationError';
import { ServiceResponse, ServiceError } from '../base/types';
import {
  FormatConverter,
  ConversionOptions,
  ConversionResult,
  StreamProcessingResult,
  ConversionProgress,
  ConversionStats,
  ConversionEventHandler,
  StreamOptions,
  FormatConverterEvents
} from './FormatConverter';
import { Readable, Writable } from 'stream';
import fs from 'fs/promises';
import os from 'os';
import path from 'path';

export interface ResourceTracker {
  tempFiles: Set<string>;
  streams: Set<Readable | Writable>;
  timers: Set<NodeJS.Timeout>;
}

export abstract class BaseFormatConverter extends TypedEventEmitter<FormatConverterEvents> implements FormatConverter {
  protected readonly logger: Logger;
  protected readonly defaultOptions: ConversionOptions;
  protected stats: ConversionStats;
  protected resources: ResourceTracker;
  protected memoryThreshold: number;

  constructor() {
    super();
    this.logger = Logger.getInstance().child(this.constructor.name);
    this.defaultOptions = {
      targetFormat: '',
      quality: 80,
      preserveMetadata: true,
      stripExif: false,
      compressionLevel: 6,
      chunkSize: 8 * 1024 * 1024, // 8MB default chunk size
      memoryLimit: os.totalmem() * 0.8 // 80% of total system memory
    };
    this.stats = {
      inputSize: 0,
      outputSize: 0,
      conversionTime: 0,
      successCount: 0,
      failureCount: 0,
      totalConversions: 0,
      peakMemoryUsage: 0
    };
    this.resources = {
      tempFiles: new Set<string>(),
      streams: new Set<Readable | Writable>(),
      timers: new Set<NodeJS.Timeout>()
    };
    this.memoryThreshold = os.totalmem() * 0.8; // 80% of total system memory
  }

  abstract canConvertFrom(mimeType: string): boolean;
  abstract canConvertTo(format: string): boolean;
  abstract getSupportedInputFormats(): string[];
  abstract getSupportedOutputFormats(): string[];

  public async convert(
    input: Buffer | string,
    options: ConversionOptions
  ): Promise<ServiceResponse<ConversionResult>> {
    const startTime = Date.now();

    try {
      // Validate input and options
      await this.validateInput(input);
      const mergedOptions = await this.validateOptions(options);

      // Create input stream from Buffer or file path
      const inputStream = typeof input === 'string'
        ? Readable.from(await this.readFile(input))
        : Readable.from(input);
      this.trackResource('streams', inputStream);

      // Create output chunks collector with memory monitoring
      const chunks: Buffer[] = [];
      let totalMemoryUsed = 0;
      const outputStream = new Writable({
        write: (chunk, encoding, callback) => {
          totalMemoryUsed += chunk.length;
          
          // Check memory usage
          if (totalMemoryUsed > this.memoryThreshold) {
            callback(new Error('Memory usage exceeded threshold'));
            return;
          }

          chunks.push(chunk);
          this.updateMemoryStats(totalMemoryUsed);
          callback();
        }
      });
      this.trackResource('streams', outputStream);

      // Set up progress monitoring
      const progressTimer = setInterval(() => {
        const progress: ConversionProgress = {
          bytesProcessed: totalMemoryUsed,
          totalBytes: input instanceof Buffer ? input.length : 0,
          percent: 0,
          stage: 'converting',
          timeElapsed: Date.now() - startTime,
          memoryUsage: process.memoryUsage().heapUsed
        };
        if (progress.totalBytes > 0) {
          progress.percent = (progress.bytesProcessed / progress.totalBytes) * 100;
        }
        this.emit('progress', progress);
      }, 100);
      this.trackResource('timers', progressTimer);

      // Perform stream conversion
      const streamResult = await this.convertStream(inputStream, outputStream, mergedOptions);

      if (streamResult.success && streamResult.data) {
        const data = Buffer.concat(chunks);
        const result: ConversionResult = {
          data,
          metadata: streamResult.data.metadata,
          originalFormat: streamResult.data.originalFormat,
          conversionTime: Date.now() - startTime,
          memoryUsage: {
            peak: this.stats.peakMemoryUsage,
            final: process.memoryUsage().heapUsed
          }
        };

        // Update stats
        this.updateStats(true, input, data, result.conversionTime);
        this.emit('complete', result);

        return {
          success: true,
          data: result
        };
      } else {
        const serviceError = streamResult.error instanceof ServiceError 
          ? streamResult.error 
          : new ServiceError('ConversionError', streamResult.error?.message || 'Conversion failed without error details');
        
        // Update stats
        this.updateStats(false, input, null, Date.now() - startTime);
        this.emit('error', serviceError);

        return {
          success: false,
          error: serviceError,
          data: undefined
        };
      }
    } catch (error) {
      this.logger.error('Conversion failed:', error);
      const serviceError = error instanceof ServiceError ? error : new ServiceError(
        'ConversionError',
        error instanceof Error ? error.message : String(error)
      );
      this.emit('error', serviceError);
      return { 
        success: false, 
        error: serviceError,
        data: undefined 
      };
    } finally {
      // Clean up resources
      await this.cleanup();
    }
  }

  public abstract convertStream(
    inputStream: Readable,
    outputStream: Writable,
    options: ConversionOptions
  ): Promise<ServiceResponse<StreamProcessingResult>>;

  public getStats(): ConversionStats {
    return { ...this.stats };
  }

  public resetStats(): void {
    this.stats = {
      inputSize: 0,
      outputSize: 0,
      conversionTime: 0,
      successCount: 0,
      failureCount: 0,
      totalConversions: 0,
      peakMemoryUsage: 0
    };
  }

  public async cleanup(): Promise<void> {
    try {
      // Clean up temporary files
      for (const file of this.resources.tempFiles) {
        try {
          await fs.unlink(file);
        } catch (error) {
          this.logger.warn(`Failed to delete temporary file ${file}:`, error);
        }
      }
      this.resources.tempFiles.clear();

      // Clean up streams
      for (const stream of this.resources.streams) {
        try {
          if (!stream.destroyed) {
            stream.destroy();
          }
        } catch (error) {
          this.logger.warn('Failed to destroy stream:', error);
        }
      }
      this.resources.streams.clear();

      // Clean up timers
      for (const timer of this.resources.timers) {
        clearInterval(timer);
      }
      this.resources.timers.clear();
    } catch (error) {
      this.logger.error('Error during cleanup:', error);
      throw error;
    }
  }

  protected trackResource<T extends keyof ResourceTracker>(type: T, resource: ResourceTracker[T] extends Set<infer U> ? U : never): void {
    this.resources[type].add(resource as any);
  }

  protected async validateOptions(options?: ConversionOptions): Promise<ConversionOptions> {
    const mergedOptions = {
      ...this.defaultOptions,
      ...options
    };

    if (!mergedOptions.targetFormat) {
      throw new Error('Target format is required');
    }

    if (!this.canConvertTo(mergedOptions.targetFormat)) {
      throw new Error(`Unsupported target format: ${mergedOptions.targetFormat}`);
    }

    // Validate memory-related options
    if (mergedOptions.memoryLimit && mergedOptions.memoryLimit > os.totalmem()) {
      throw new Error('Memory limit cannot exceed system total memory');
    }

    if (mergedOptions.chunkSize && mergedOptions.chunkSize > (mergedOptions.memoryLimit || this.memoryThreshold) / 4) {
      throw new Error('Chunk size cannot exceed 25% of memory limit');
    }

    return mergedOptions;
  }

  protected async validateInput(input: Buffer | string): Promise<void> {
    if (!input) {
      throw new ValidationError('Input is required');
    }

    if (input instanceof Buffer && input.length === 0) {
      throw new ValidationError('Input buffer cannot be empty');
    }

    if (typeof input === 'string') {
      if (!input.trim()) {
        throw new ValidationError('Input path cannot be empty');
      }
      try {
        await fs.access(input);
      } catch {
        throw new ValidationError(`Input file does not exist: ${input}`);
      }
    }
  }

  protected async readFile(path: string): Promise<Buffer> {
    const stats = await fs.stat(path);
    if (stats.size > this.memoryThreshold) {
      throw new Error(`File size (${stats.size} bytes) exceeds memory threshold (${this.memoryThreshold} bytes)`);
    }
    return fs.readFile(path);
  }

  protected updateStats(success: boolean, input: Buffer | string, output: Buffer | null, time: number): void {
    this.stats.totalConversions++;
    if (success) {
      this.stats.successCount++;
      this.stats.inputSize += input instanceof Buffer ? input.length : 0;
      this.stats.outputSize += output ? output.length : 0;
    } else {
      this.stats.failureCount++;
    }
    this.stats.conversionTime += time;
  }

  protected updateMemoryStats(currentUsage: number): void {
    this.stats.peakMemoryUsage = Math.max(this.stats.peakMemoryUsage, currentUsage);
  }

  protected async createTempDirectory(): Promise<string> {
    const tempDir = await fs.mkdtemp(path.join(os.tmpdir(), 'format-converter-'));
    this.trackResource('tempFiles', tempDir);
    return tempDir;
  }

  protected closeQuietly(stream: Readable | Writable | null): void {
    if (stream && !stream.destroyed) {
      try {
        stream.destroy();
      } catch (error) {
        this.logger.warn('Error closing stream:', error);
      }
    }
  }

  public getSupportedFormats(): string[] {
    return [...this.getSupportedInputFormats(), ...this.getSupportedOutputFormats()];
  }
} 