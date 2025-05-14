import { BaseThumbnailGenerator } from './base';
import { ThumbnailOptions, ThumbnailResult } from './types';
import { ValidationError } from './errors';
import ffmpeg from 'fluent-ffmpeg';
import fs from 'fs';
import os from 'os';
import path from 'path';
import { v4 as uuidv4 } from 'uuid';

const SUPPORTED_VIDEO_TYPES = [
  'video/mp4',
  'video/quicktime',
  'video/x-matroska',
  'video/webm',
  'video/avi',
];

export class VideoThumbnailGenerator extends BaseThumbnailGenerator {
  supports(mimeType: string): boolean {
    return SUPPORTED_VIDEO_TYPES.includes(mimeType);
  }

  async generate(input: string | Buffer, options?: ThumbnailOptions): Promise<ThumbnailResult> {
    this.validateInput(input);
    const opts = this.mergeOptions(options);
    const tempDir = os.tmpdir();
    const tempInput = typeof input === 'string' ? input : path.join(tempDir, uuidv4() + '.mp4');
    const tempOutput = path.join(tempDir, uuidv4() + '.jpg');
    let cleanupInput = false;
    try {
      if (typeof input !== 'string') {
        fs.writeFileSync(tempInput, input);
        cleanupInput = true;
      }
      await new Promise<void>((resolve, reject) => {
        ffmpeg(tempInput)
          .on('end', () => resolve())
          .on('error', (err) => reject(err))
          .screenshots({
            timestamps: [opts.timestamp || 0],
            filename: path.basename(tempOutput),
            folder: tempDir,
            size: `${opts.width || 200}x${opts.height || 200}`,
          });
      });
      const buffer = fs.readFileSync(tempOutput);
      // Optionally, use sharp to get metadata
      const sharp = await import('sharp');
      const metadata = await sharp.default(buffer).metadata();
      const result: ThumbnailResult = {
        buffer,
        width: metadata.width || opts.width || 0,
        height: metadata.height || opts.height || 0,
        format: metadata.format || 'jpeg',
        size: buffer.length,
      };
      return result;
    } catch (err) {
      throw new ValidationError('VIDEO_THUMBNAIL_ERROR', 'Failed to generate video thumbnail', err);
    } finally {
      if (cleanupInput && fs.existsSync(tempInput)) fs.unlinkSync(tempInput);
      if (fs.existsSync(tempOutput)) fs.unlinkSync(tempOutput);
    }
  }
} 