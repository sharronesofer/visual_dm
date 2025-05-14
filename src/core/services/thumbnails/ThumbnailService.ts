import { lookup } from 'mime-types';
import { ServiceResponse } from '../base/types';
import { ValidationError } from '../../errors/ValidationError';
import { ThumbnailGenerator, ThumbnailOptions, ThumbnailResult } from './ThumbnailGenerator';
import { ImageThumbnailGenerator } from './ImageThumbnailGenerator';
import { VideoThumbnailGenerator } from './VideoThumbnailGenerator';
import { AudioThumbnailGenerator } from './AudioThumbnailGenerator';
import { DocumentThumbnailGenerator } from './DocumentThumbnailGenerator';
import { ThumbnailCache, ThumbnailCacheConfig } from './ThumbnailCache';
import { Logger } from '../../utils/logger';

export interface ThumbnailServiceConfig {
  cache?: ThumbnailCacheConfig;
}

export class ThumbnailService {
  private readonly generators: ThumbnailGenerator[];
  private readonly logger: Logger;
  private readonly cache: ThumbnailCache;

  constructor(config?: ThumbnailServiceConfig) {
    this.generators = [
      new ImageThumbnailGenerator(),
      new VideoThumbnailGenerator(),
      new AudioThumbnailGenerator(),
      new DocumentThumbnailGenerator()
    ];
    this.logger = Logger.getInstance().child('ThumbnailService');
    this.cache = new ThumbnailCache(config?.cache);
  }

  async initialize(): Promise<void> {
    await this.cache.initialize();
  }

  async generateThumbnail(file: Buffer | string, options?: ThumbnailOptions): Promise<ServiceResponse<ThumbnailResult>> {
    try {
      // Check cache first
      const cachedResult = await this.cache.get(file, options || {});
      if (cachedResult) {
        this.logger.debug('Thumbnail found in cache');
        return {
          success: true,
          data: cachedResult
        };
      }

      let mimeType: string;

      if (typeof file === 'string') {
        mimeType = lookup(file) || '';
      } else {
        // Try to detect mime type from buffer
        const fileType = await import('file-type');
        const type = await fileType.fileTypeFromBuffer(file);
        mimeType = type?.mime || '';
      }

      if (!mimeType) {
        return {
          success: false,
          error: new ValidationError('Could not determine file type', {
            code: 'UNKNOWN_TYPE',
            status: 400
          }),
          data: null
        };
      }

      const generator = this.findGenerator(mimeType);
      if (!generator) {
        return {
          success: false,
          error: new ValidationError(`Unsupported file type: ${mimeType}`, {
            code: 'UNSUPPORTED_TYPE',
            status: 400
          }),
          data: null
        };
      }

      const result = await generator.generateThumbnail(file, options);
      if (result.success && result.data) {
        // Cache the successful result
        await this.cache.set(file, options || {}, result.data);
      }

      return result;
    } catch (error) {
      this.logger.error('Failed to generate thumbnail', error instanceof Error ? error : undefined, {
        error: error instanceof Error ? error.message : 'Unknown error'
      });
      return {
        success: false,
        error: new ValidationError('Failed to generate thumbnail', {
          code: 'GENERATION_ERROR',
          status: 500
        }),
        data: null
      };
    }
  }

  private findGenerator(mimeType: string): ThumbnailGenerator | undefined {
    return this.generators.find(generator => generator.canHandle(mimeType));
  }

  async cleanup(): Promise<void> {
    // Clean up any temporary files or resources
    await Promise.all([
      ...this.generators.map(generator => generator.cleanup()),
      this.cache.clear()
    ]);
  }
} 