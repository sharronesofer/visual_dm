import { ThumbnailOptions, ThumbnailResult, ThumbnailGenerator } from './types';
import { ValidationError } from './errors';
import * as fs from 'fs';

export abstract class BaseThumbnailGenerator implements ThumbnailGenerator {
  protected defaultOptions: ThumbnailOptions = {
    width: 200,
    height: 200,
    quality: 80,
    format: 'jpeg',
    maintainAspectRatio: true,
  };

  abstract generate(input: string | Buffer, options?: ThumbnailOptions): Promise<ThumbnailResult>;
  abstract supports(mimeType: string): boolean;

  protected mergeOptions(options?: ThumbnailOptions): ThumbnailOptions {
    return { ...this.defaultOptions, ...options };
  }

  protected validateInput(input: string | Buffer): void {
    if (!input) {
      throw new ValidationError('INPUT_REQUIRED', 'Input file or buffer is required');
    }
    if (typeof input === 'string' && !fs.existsSync(input)) {
      throw new ValidationError('FILE_NOT_FOUND', `File not found: ${input}`);
    }
  }
} 