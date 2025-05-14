import { EventEmitter } from 'events';
import { Readable, Writable } from 'stream';
import { ServiceResponse, ServiceError } from '../base/types';
import { StreamProcessingResult as MediaStreamProcessingResult } from '../types/MediaProcessing';

export { ServiceResponse };

export interface ConversionOptions {
  targetFormat: string;
  format?: string;  // For backward compatibility
  quality?: number;
  compression?: boolean;
  // Video-specific options
  fps?: number;
  width?: number;
  height?: number;
  videoCodec?: string;
  videoBitrate?: string;
  // Audio-specific options
  audioCodec?: string;
  audioBitrate?: string;
  audioChannels?: number;
  sampleRate?: number;
  // Stream processing options
  chunkSize?: number;
  codec?: string;
  preset?: string;
  bitrate?: string | number;
  metadata?: Record<string, string>;
  stripMetadata?: boolean;
  preserveMetadata?: boolean;
  tempDir?: string;
  stripExif?: boolean;
  compressionLevel?: number;
  memoryLimit?: number;
  preserveAspectRatio?: boolean;
}

export interface StreamOptions {
  chunkSize?: number;
  memoryLimit?: number;
  preserveMetadata?: boolean;
  quality?: number;
}

export interface ConversionProgress {
  bytesProcessed: number;
  totalBytes: number;
  percent: number;
  stage: string;
  timeElapsed?: number;
  timeRemaining?: number;
  currentFile?: string;
  memoryUsage: number;
}

export interface ConversionMetadata {
  format: string;
  size: number;
  width?: number;
  height?: number;
  duration?: number;
  bitrate?: string;
  codec?: string;
  fps?: string;
  audioCodec?: string;
  audioChannels?: number;
  audioSampleRate?: number;
  createdAt: Date;
  [key: string]: unknown;
}

export interface ConversionResult {
  data: Buffer;
  format: string;
  size: number;
  duration?: number;
  width?: number;
  height?: number;
  fps?: number;
  bitrate?: string;
  codec?: string;
}

export interface StreamProcessingResult extends MediaStreamProcessingResult {
  format: string;
  size: number;
}

export interface StreamConversionResult extends StreamProcessingResult {
  stream: Readable;
  format: string;
  size: number;
}

export interface ConversionStats {
  inputSize: number;
  outputSize: number;
  conversionTime: number;
  successCount: number;
  failureCount: number;
  totalConversions: number;
  peakMemoryUsage: number;
}

export type ConversionEventHandler<T> = (data: T) => void;

export interface FormatConverter {
  convert(input: Buffer | string, options: ConversionOptions): Promise<ServiceResponse<ConversionResult>>;
  convertStream(
    inputStream: Readable,
    outputStream: Writable,
    options: ConversionOptions
  ): Promise<ServiceResponse<StreamProcessingResult>>;
  getSupportedFormats(): string[];
  getSupportedInputFormats(): string[];
  getSupportedOutputFormats(): string[];
  canConvertTo(format: string): boolean;
  cleanup(): Promise<void>;
}

export abstract class BaseFormatConverter extends EventEmitter implements FormatConverter {
  abstract getSupportedInputFormats(): string[];
  abstract getSupportedOutputFormats(): string[];
  abstract convert(input: Buffer | string, options: ConversionOptions): Promise<ServiceResponse<ConversionResult>>;
  abstract canConvertTo(format: string): boolean;
  
  async cleanup(): Promise<void> {
    // Default implementation - can be overridden by specific converters
  }

  getSupportedFormats(): string[] {
    return [...this.getSupportedInputFormats(), ...this.getSupportedOutputFormats()];
  }

  abstract convertStream(
    inputStream: Readable,
    outputStream: Writable,
    options: ConversionOptions
  ): Promise<ServiceResponse<StreamProcessingResult>>;
}

/**
 * Type-safe event interface for format converters
 */
export interface FormatConverterEvents {
  progress: ConversionProgress;
  error: ServiceError;
  complete: ConversionResult | StreamProcessingResult;
} 