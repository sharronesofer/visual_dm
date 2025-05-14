import { lookup } from 'mime-types';
import { join } from 'path';
import { tmpdir } from 'os';
import { v4 as uuidv4 } from 'uuid';
import { writeFile } from 'fs/promises';
import * as pdfjsLib from 'pdfjs-dist';
import { createCanvas } from 'canvas';
import { BaseThumbnailGenerator } from './BaseThumbnailGenerator';
import { ThumbnailOptions, ThumbnailResult } from './ThumbnailGenerator';
import { ServiceResponse } from '../base/types';
import { ValidationError } from '../../errors/ValidationError';

export class DocumentThumbnailGenerator extends BaseThumbnailGenerator {
  private readonly supportedMimeTypes = [
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document', // docx
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', // xlsx
    'application/vnd.openxmlformats-officedocument.presentationml.presentation', // pptx
    'application/msword', // doc
    'application/vnd.ms-excel', // xls
    'application/vnd.ms-powerpoint', // ppt
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

      let documentPath: string;
      let needsCleanup = false;

      if (Buffer.isBuffer(file)) {
        // If file is a buffer, write it to a temporary file
        const tempPath = join(tmpdir(), `${uuidv4()}.pdf`);
        await writeFile(tempPath, file);
        documentPath = tempPath;
        needsCleanup = true;
      } else {
        const mimeType = lookup(file) || '';
        if (!this.canHandle(mimeType)) {
          return {
            success: false,
            error: new ValidationError(`Unsupported document format: ${mimeType}`, {
              code: 'UNSUPPORTED_FORMAT',
              status: 400
            }),
            data: null
          };
        }
        documentPath = file;
      }

      try {
        const pageNumber = mergedOptions.page || 1;
        const imageBuffer = await this.renderPage(documentPath, pageNumber);

        // Process the rendered page using sharp
        const processedImage = await this.processImage(imageBuffer, mergedOptions);

        const result: ThumbnailResult = {
          data: processedImage.data,
          width: processedImage.info.width,
          height: processedImage.info.height,
          format: mergedOptions.format || 'jpeg',
          size: processedImage.info.size
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
      this.logger.error('Failed to generate document thumbnail:', error instanceof Error ? error : new Error(String(error)));
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

  private async renderPage(documentPath: string, pageNumber: number): Promise<Buffer> {
    // Load the PDF document
    const data = await pdfjsLib.getDocument(documentPath).promise;

    // Get the specified page
    const page = await data.getPage(pageNumber);

    // Set the viewport for rendering
    const viewport = page.getViewport({ scale: 1.0 });

    // Create a canvas for rendering
    const canvas = createCanvas(viewport.width, viewport.height);
    const context: any = canvas.getContext('2d');

    // Render the page to the canvas
    await page.render({
      canvasContext: context,
      viewport: viewport
    }).promise;

    // Convert canvas to buffer
    return canvas.toBuffer('image/png');
  }

  private async processImage(imageBuffer: Buffer, options: ThumbnailOptions): Promise<{ data: Buffer; info: { width: number; height: number; size: number } }> {
    const sharp = (await import('sharp')).default;
    const image = sharp(imageBuffer);
    const metadata = await image.metadata();

    const { width, height } = this.calculateDimensions(
      metadata.width || 0,
      metadata.height || 0,
      options.width || 200,
      options.height || 200
    );

    const allowedFormats = ['jpeg', 'png', 'webp'];
    const format = allowedFormats.includes(options.format as string) ? options.format as string : 'jpeg';

    const processedImage = await image
      .resize(width, height)
      .toFormat(format as any, {
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
    targetHeight: number
  ): { width: number; height: number } {
    // Always preserve aspect ratio
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

  getSupportedFormats(): string[] {
    return ['jpeg', 'png', 'webp'];
  }

  async cleanup(): Promise<void> {
    // Implement cleanup logic for temporary files
    await super.cleanup();
  }
} 