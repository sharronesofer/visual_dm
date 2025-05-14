import { Readable, Writable } from 'stream';
import { BaseEntity } from './service';

/**
 * Supported media types
 */
export enum MediaType {
  IMAGE = 'image',
  VIDEO = 'video',
  AUDIO = 'audio',
  DOCUMENT = 'document'
}

/**
 * Media format interface
 */
export interface MediaFormat {
  mimeType: string;
  extension: string;
  type: MediaType;
}

/**
 * Media metadata interface
 */
export interface MediaMetadata {
  width?: number;
  height?: number;
  duration?: number;
  size: number;
  format: MediaFormat;
  [key: string]: any;
}

/**
 * Media entity interface
 */
export interface Media extends BaseEntity {
  filename: string;
  path: string;
  metadata: MediaMetadata;
  type: MediaType;
  thumbnailPath?: string;
}

/**
 * Media processing status
 */
export enum MediaProcessingStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed'
}

/**
 * Media processing options
 */
export interface MediaProcessingOptions {
  quality?: number;
  format?: string;
  width?: number;
  height?: number;
  preserveAspectRatio?: boolean;
  metadata?: Record<string, any>;
}

/**
 * Media processing result
 */
export interface MediaProcessingResult {
  data: Buffer;
  metadata: MediaMetadata;
  status: MediaProcessingStatus;
  error?: Error;
}

/**
 * Media input types
 */
export type MediaInput = Buffer | Readable | string;

/**
 * Media output types
 */
export type MediaOutput = Buffer | Writable | string;

/**
 * Media conversion configuration
 */
export interface MediaConversionConfig {
  inputFormat: string;
  outputFormat: string;
  quality?: number;
  metadata?: Record<string, any>;
  options?: MediaProcessingOptions;
}

/**
 * Media conversion progress
 */
export interface MediaConversionProgress {
  bytesProcessed: number;
  totalBytes: number;
  percent: number;
  stage: string;
  timestamp: number;
}

/**
 * Media validation result
 */
export interface MediaValidationResult {
  isValid: boolean;
  errors?: string[];
  metadata?: MediaMetadata;
}

/**
 * Media storage configuration
 */
export interface MediaStorageConfig {
  basePath: string;
  createThumbnails?: boolean;
  thumbnailOptions?: MediaProcessingOptions;
  preserveOriginal?: boolean;
  maxSize?: number;
  allowedTypes?: MediaType[];
  allowedFormats?: string[];
}

/**
 * Type guard for Buffer
 */
export function isBuffer(input: MediaInput): input is Buffer {
  return Buffer.isBuffer(input);
}

/**
 * Type guard for Readable
 */
export function isReadable(input: MediaInput): input is Readable {
  return input instanceof Readable;
}

/**
 * Type guard for file path
 */
export function isFilePath(input: MediaInput): input is string {
  return typeof input === 'string' && input.includes('/');
} 