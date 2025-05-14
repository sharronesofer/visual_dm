import { 
  ThumbnailGenerator, 
  ThumbnailOptions, 
  ThumbnailResult, 
  ThumbnailInput, 
  ThumbnailFormat,
  isBuffer,
  isReadable,
  isFilePath
} from './types';
import { ServiceResponse } from '../base/types';
import { ValidationError } from '../../errors/ValidationError';
import { Logger } from '../../utils/logger';

export abstract class BaseThumbnailGenerator implements ThumbnailGenerator {
  protected readonly logger: Logger;
  protected readonly defaultOptions: ThumbnailOptions = {
    width: 200,
    height: 200,
    quality: 80,
    format: 'jpeg',
    preserveAspectRatio: true
  };

  constructor() {
    this.logger = Logger.getInstance().child(this.constructor.name);
  }

  abstract canHandle(mimeType: string): boolean;
  abstract generateThumbnail(input: ThumbnailInput, options: ThumbnailOptions): Promise<ServiceResponse<ThumbnailResult>>;
  abstract getSupportedFormats(): ThumbnailFormat[];

  getDefaultOptions(): ThumbnailOptions {
    return { ...this.defaultOptions };
  }

  async validateOptions(options: ThumbnailOptions): Promise<boolean> {
    try {
      // Validate dimensions
      if (options.width && (options.width < 1 || options.width > 4096)) {
        throw new ValidationError('Width must be between 1 and 4096 pixels');
      }
      if (options.height && (options.height < 1 || options.height > 4096)) {
        throw new ValidationError('Height must be between 1 and 4096 pixels');
      }

      // Validate quality
      if (options.quality && (options.quality < 1 || options.quality > 100)) {
        throw new ValidationError('Quality must be between 1 and 100');
      }

      // Validate format
      if (options.format && !this.getSupportedFormats().includes(options.format)) {
        throw new ValidationError('Invalid format specified');
      }

      // Validate timestamp (for video thumbnails)
      if (options.timestamp !== undefined && options.timestamp < 0) {
        throw new ValidationError('Timestamp cannot be negative');
      }

      // Validate page number (for document thumbnails)
      if (options.page !== undefined && options.page < 1) {
        throw new ValidationError('Page number must be positive');
      }

      return true;
    } catch (error) {
      this.logger.error('Thumbnail options validation failed:', error);
      return false;
    }
  }

  async cleanup(): Promise<void> {
    // Base implementation - can be overridden by specific generators
    this.logger.debug('Cleaning up resources');
  }

  protected mergeWithDefaultOptions(options: ThumbnailOptions): ThumbnailOptions {
    return {
      ...this.defaultOptions,
      ...options
    };
  }

  protected async validateInput(input: ThumbnailInput): Promise<boolean> {
    if (!input) {
      throw new ValidationError('No input provided');
    }

    if (isFilePath(input)) {
      if (!input.trim()) {
        throw new ValidationError('Invalid file path');
      }
    } else if (isBuffer(input)) {
      if (input.length === 0) {
        throw new ValidationError('Empty buffer provided');
      }
    } else if (isReadable(input)) {
      // Readable streams are valid by default
      // Specific implementations may add additional checks
    } else {
      throw new ValidationError('Invalid input type');
    }

    return true;
  }
} 