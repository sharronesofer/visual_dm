import ffmpeg from 'fluent-ffmpeg';
import { lookup } from 'mime-types';
import { promisify } from 'util';
import { writeFile } from 'fs/promises';
import { join } from 'path';
import { tmpdir } from 'os';
import { v4 as uuidv4 } from 'uuid';
import { BaseThumbnailGenerator } from './BaseThumbnailGenerator';
import { ThumbnailOptions, ThumbnailResult } from './ThumbnailGenerator';
import { ServiceResponse } from '../base/types';
import { ValidationError } from '../../errors/ValidationError';

export class VideoThumbnailGenerator extends BaseThumbnailGenerator {
  private readonly supportedMimeTypes = [
    'video/mp4',
    'video/webm',
    'video/ogg',
    'video/quicktime',
    'video/x-msvideo'
  ];

  canHandle(mimeType: string): boolean {
    return this.supportedMimeTypes.includes(mimeType);
  }

  async generateThumbnail(file: Buffer | string, options?: ThumbnailOptions): Promise<ServiceResponse<ThumbnailResult>> {
    try {
      await this.validateFile(file);
      const mergedOptions = this.mergeWithDefaultOptions(options);

      if (!(await this.validateOptions(mergedOptions))) {
        return {
          success: false,
          error: new ValidationError('Invalid thumbnail options', {
            code: 'INVALID_OPTIONS',
            status: 400
          }),
          data: null
        };
      }

      let videoPath: string;
      let needsCleanup = false;

      if (Buffer.isBuffer(file)) {
        // If file is a buffer, write it to a temporary file
        const tempPath = join(tmpdir(), `${uuidv4()}.mp4`);
        await writeFile(tempPath, file);
        videoPath = tempPath;
        needsCleanup = true;
      } else {
        const mimeType = lookup(file) || '';
        if (!this.canHandle(mimeType)) {
          return {
            success: false,
            error: new ValidationError(`Unsupported video format: ${mimeType}`, {
              code: 'UNSUPPORTED_FORMAT',
              status: 400
            }),
            data: null
          };
        }
        videoPath = file;
      }

      try {
        const metadata = await this.getVideoMetadata(videoPath);
        const timestamp = mergedOptions.timestamp || 0;

        if (timestamp < 0 || timestamp > metadata.duration) {
          return {
            success: false,
            error: new ValidationError('Invalid timestamp', {
              code: 'INVALID_TIMESTAMP',
              status: 400
            }),
            data: null
          };
        }

        const thumbnailPath = join(tmpdir(), `${uuidv4()}.jpg`);
        await this.extractFrame(videoPath, thumbnailPath, timestamp);

        const result: ThumbnailResult = {
          data: await this.processImage(thumbnailPath, mergedOptions),
          metadata: {
            width: mergedOptions.width || 200,
            height: mergedOptions.height || 200,
            format: mergedOptions.format || 'jpeg',
            size: 0, // Will be updated after processing
            originalFormat: metadata.format,
            generatedAt: new Date()
          },
          path: thumbnailPath
        };

        return {
          success: true,
          data: result
        };
      } finally {
        if (needsCleanup) {
          // Clean up temporary files
          await this.cleanup();
        }
      }
    } catch (error) {
      this.logger.error('Failed to generate video thumbnail:', error);
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

  private getVideoMetadata(videoPath: string): Promise<{ duration: number; format: string }> {
    return new Promise((resolve, reject) => {
      ffmpeg.ffprobe(videoPath, (err: Error | null, metadata: ffmpeg.FfprobeData) => {
        if (err) {
          reject(new ValidationError('Failed to read video metadata', {
            code: 'METADATA_ERROR',
            status: 500
          }));
          return;
        }

        resolve({
          duration: metadata.format.duration || 0,
          format: metadata.format.format_name || 'unknown'
        });
      });
    });
  }

  private extractFrame(videoPath: string, outputPath: string, timestamp: number): Promise<void> {
    return new Promise((resolve, reject) => {
      ffmpeg(videoPath)
        .screenshots({
          timestamps: [timestamp],
          filename: outputPath,
          folder: '.',
          size: '?x?'
        })
        .on('end', () => resolve())
        .on('error', (err: Error) => reject(new ValidationError(`Failed to extract frame: ${err.message}`, {
          code: 'FRAME_EXTRACTION_ERROR',
          status: 500
        })));
    });
  }

  private async processImage(imagePath: string, options: ThumbnailOptions): Promise<Buffer> {
    // Use sharp to process the extracted frame
    const sharp = (await import('sharp')).default;
    const image = sharp(imagePath);

    const { width, height } = this.calculateDimensions(
      await image.metadata().then(m => m.width || 0),
      await image.metadata().then(m => m.height || 0),
      options.width || 200,
      options.height || 200,
      options.preserveAspectRatio
    );

    return image
      .resize(width, height, {
        fit: options.preserveAspectRatio ? 'inside' : 'fill'
      })
      .toFormat(options.format || 'jpeg', {
        quality: options.quality || 80
      })
      .toBuffer();
  }

  private calculateDimensions(
    originalWidth: number,
    originalHeight: number,
    targetWidth: number,
    targetHeight: number,
    preserveAspectRatio: boolean = true
  ): { width: number; height: number } {
    if (!preserveAspectRatio) {
      return { width: targetWidth, height: targetHeight };
    }

    const aspectRatio = originalWidth / originalHeight;
    let width = targetWidth;
    let height = targetHeight;

    if (targetWidth / targetHeight > aspectRatio) {
      width = Math.round(targetHeight * aspectRatio);
    } else {
      height = Math.round(targetWidth / aspectRatio);
    }

    return { width, height };
  }

  async cleanup(): Promise<void> {
    // Implement cleanup logic for temporary files
    await super.cleanup();
  }
} 