import { BaseThumbnailGenerator } from './base';
import { ThumbnailOptions, ThumbnailResult } from './types';
import { ValidationError } from './errors';
import fs from 'fs';
import os from 'os';
import path from 'path';
import { v4 as uuidv4 } from 'uuid';
// @ts-ignore: No type declarations for pdf2pic
import { fromPath } from 'pdf2pic';

const SUPPORTED_DOCUMENT_TYPES = [
  'application/pdf',
];

export class DocumentThumbnailGenerator extends BaseThumbnailGenerator {
  supports(mimeType: string): boolean {
    return SUPPORTED_DOCUMENT_TYPES.includes(mimeType);
  }

  async generate(input: string | Buffer, options?: ThumbnailOptions): Promise<ThumbnailResult> {
    this.validateInput(input);
    const opts = this.mergeOptions(options);
    const tempDir = os.tmpdir();
    const tempInput = typeof input === 'string' ? input : path.join(tempDir, uuidv4() + '.pdf');
    let cleanupInput = false;
    try {
      if (typeof input !== 'string') {
        fs.writeFileSync(tempInput, input);
        cleanupInput = true;
      }
      const page = opts.page || 1;
      const converter = fromPath(tempInput, {
        density: 100,
        saveFilename: uuidv4(),
        savePath: tempDir,
        format: opts.format || 'png',
        width: opts.width || 200,
        height: opts.height || 200,
      });
      const result = await converter(page);
      const buffer = fs.readFileSync(result.path);
      const sharp = await import('sharp');
      const metadata = await sharp.default(buffer).metadata();
      return {
        buffer,
        width: metadata.width || opts.width || 0,
        height: metadata.height || opts.height || 0,
        format: metadata.format || opts.format || 'png',
        size: buffer.length,
      };
    } catch (err) {
      throw new ValidationError('DOCUMENT_THUMBNAIL_ERROR', 'Failed to generate document thumbnail', err);
    } finally {
      if (cleanupInput && fs.existsSync(tempInput)) fs.unlinkSync(tempInput);
    }
  }
} 