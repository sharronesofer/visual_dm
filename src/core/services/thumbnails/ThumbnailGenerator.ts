import { Readable } from 'stream';
import { ServiceResponse } from '../types/Service';

export interface ThumbnailOptions {
  width: number;
  height: number;
  quality?: number;
  format?: string;
  timestamp?: number;  // For video thumbnails (position in seconds)
  page?: number;      // For document thumbnails
}

export interface ThumbnailResult {
  data: Buffer;
  width: number;
  height: number;
  format: string;
  size: number;
}

export interface ThumbnailGenerator {
  generateThumbnail(input: Buffer | Readable, options: ThumbnailOptions): Promise<ServiceResponse<ThumbnailResult>>;
  canHandle(mimeType: string): boolean;
  getSupportedFormats(): string[];
  cleanup?(): Promise<void>;
} 