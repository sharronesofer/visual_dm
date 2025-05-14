import { ThumbnailOptions, ThumbnailResult, ServiceResponse, ServiceError, ThumbnailGenerator } from './types';
import { ImageThumbnailGenerator } from './image';
import { VideoThumbnailGenerator } from './video';
import { AudioThumbnailGenerator } from './audio';
import { DocumentThumbnailGenerator } from './document';
import { ThumbnailServiceError, ValidationError } from './errors';

export class ThumbnailService {
  private generators: ThumbnailGenerator[] = [];

  constructor() {
    this.generators = [
      new ImageThumbnailGenerator(),
      new VideoThumbnailGenerator(),
      new AudioThumbnailGenerator(),
      new DocumentThumbnailGenerator(),
    ];
  }

  public async generateThumbnail(
    input: string | Buffer,
    mimeType: string,
    options?: ThumbnailOptions
  ): Promise<ServiceResponse<ThumbnailResult>> {
    try {
      const generator = this.getGenerator(mimeType);
      if (!generator) {
        return {
          success: false,
          error: {
            code: 'UNSUPPORTED_TYPE',
            message: `Unsupported mime type: ${mimeType}`,
          },
        };
      }
      const result = await generator.generate(input, options);
      return {
        success: true,
        data: result,
      };
    } catch (error) {
      return {
        success: false,
        error: this.formatError(error),
      };
    }
  }

  private getGenerator(mimeType: string): ThumbnailGenerator | undefined {
    return this.generators.find((generator) => generator.supports(mimeType));
  }

  private formatError(error: any): ServiceError {
    if (error instanceof ValidationError || error instanceof ThumbnailServiceError) {
      return {
        code: error.code,
        message: error.message,
        details: error.details,
      };
    }
    return {
      code: 'INTERNAL_ERROR',
      message: error?.message || 'Unknown error',
      details: error,
    };
  }
} 