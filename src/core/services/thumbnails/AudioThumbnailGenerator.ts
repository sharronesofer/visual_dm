import { lookup } from 'mime-types';
import { join } from 'path';
import { tmpdir } from 'os';
import { v4 as uuidv4 } from 'uuid';
import { writeFile } from 'fs/promises';
import ffmpeg from 'fluent-ffmpeg';
import { BaseThumbnailGenerator } from './BaseThumbnailGenerator';
import { ThumbnailOptions, ThumbnailResult } from './ThumbnailGenerator';
import { ServiceResponse } from '../base/types';
import { ValidationError } from '../../errors/ValidationError';

export class AudioThumbnailGenerator extends BaseThumbnailGenerator {
  private readonly supportedMimeTypes = [
    'audio/mpeg',
    'audio/wav',
    'audio/ogg',
    'audio/flac',
    'audio/aac',
    'audio/webm'
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

      let audioPath: string;
      let needsCleanup = false;

      if (Buffer.isBuffer(file)) {
        // If file is a buffer, write it to a temporary file
        const tempPath = join(tmpdir(), `${uuidv4()}.mp3`);
        await writeFile(tempPath, file);
        audioPath = tempPath;
        needsCleanup = true;
      } else {
        const mimeType = lookup(file) || '';
        if (!this.canHandle(mimeType)) {
          return {
            success: false,
            error: new ValidationError(`Unsupported audio format: ${mimeType}`, {
              code: 'UNSUPPORTED_FORMAT',
              status: 400
            }),
            data: null
          };
        }
        audioPath = file;
      }

      try {
        const metadata = await this.getAudioMetadata(audioPath);
        const waveformPath = join(tmpdir(), `${uuidv4()}.png`);

        // Generate waveform image
        await this.generateWaveform(audioPath, waveformPath, mergedOptions);

        // Process the waveform image using sharp
        const processedImage = await this.processImage(waveformPath, mergedOptions);

        const result: ThumbnailResult = {
          data: processedImage.data,
          metadata: {
            width: processedImage.info.width,
            height: processedImage.info.height,
            format: mergedOptions.format || 'jpeg',
            size: processedImage.info.size,
            originalFormat: metadata.format,
            generatedAt: new Date()
          },
          path: waveformPath
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
      this.logger.error('Failed to generate audio thumbnail:', error);
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

  private getAudioMetadata(audioPath: string): Promise<{ duration: number; format: string }> {
    return new Promise((resolve, reject) => {
      ffmpeg.ffprobe(audioPath, (err: Error | null, metadata: ffmpeg.FfprobeData) => {
        if (err) {
          reject(new ValidationError('Failed to read audio metadata', {
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

  private generateWaveform(audioPath: string, outputPath: string, options: ThumbnailOptions): Promise<void> {
    return new Promise((resolve, reject) => {
      const width = options.width || 200;
      const height = options.height || 200;

      ffmpeg(audioPath)
        .outputOptions([
          '-filter_complex',
          `[0:a]showwavespic=s=${width}x${height}:colors=white[fg];color=s=${width}x${height}:color=black[bg];[bg][fg]overlay=format=auto,format=rgb24[v]`,
          '-map',
          '[v]',
          '-frames:v',
          '1'
        ])
        .output(outputPath)
        .on('end', () => resolve())
        .on('error', (err: Error) => reject(new ValidationError(`Failed to generate waveform: ${err.message}`, {
          code: 'WAVEFORM_GENERATION_ERROR',
          status: 500
        })))
        .run();
    });
  }

  private async processImage(imagePath: string, options: ThumbnailOptions): Promise<{ data: Buffer; info: { width: number; height: number; size: number } }> {
    const sharp = (await import('sharp')).default;
    const image = sharp(imagePath);
    const metadata = await image.metadata();

    const { width, height } = this.calculateDimensions(
      metadata.width || 0,
      metadata.height || 0,
      options.width || 200,
      options.height || 200,
      options.preserveAspectRatio
    );

    const processedImage = await image
      .resize(width, height, {
        fit: options.preserveAspectRatio ? 'inside' : 'fill'
      })
      .toFormat(options.format || 'jpeg', {
        quality: options.quality || 80
      })
      .toBuffer({ resolveWithObject: true });

    return {
      data: processedImage.data,
      info: {
        width: processedImage.info.width,
        height: processedImage.info.height,
        size: processedImage.info.size
      }
    };
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