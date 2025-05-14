import { Readable } from 'stream';
import { ServiceResponse } from '../base/types';

// Supported thumbnail formats
export type ThumbnailFormat = 'jpeg' | 'png' | 'webp';

// Input types
export type ThumbnailInput = Buffer | Readable | string;

// Options interface with proper types
export interface ThumbnailOptions {
  width: number;
  height: number;
  quality?: number;
  format?: ThumbnailFormat;
  preserveAspectRatio?: boolean;
  timestamp?: number;  // For video thumbnails (position in seconds)
  page?: number;      // For document thumbnails
}

// Result interface
export interface ThumbnailResult {
  data: Buffer;
  width: number;
  height: number;
  format: ThumbnailFormat;
  size: number;
}

// Type guard for Buffer
export function isBuffer(input: ThumbnailInput): input is Buffer {
  return Buffer.isBuffer(input);
}

// Type guard for Readable
export function isReadable(input: ThumbnailInput): input is Readable {
  return input instanceof Readable;
}

// Type guard for string (file path)
export function isFilePath(input: ThumbnailInput): input is string {
  return typeof input === 'string';
}

// Generator interface
export interface ThumbnailGenerator {
  generateThumbnail(input: ThumbnailInput, options: ThumbnailOptions): Promise<ServiceResponse<ThumbnailResult>>;
  canHandle(mimeType: string): boolean;
  getSupportedFormats(): ThumbnailFormat[];
  cleanup?(): Promise<void>;
} 