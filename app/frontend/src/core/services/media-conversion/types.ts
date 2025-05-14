import { Readable, Writable } from 'stream';
import { MediaBuffer } from './BufferManager';

/**
 * Supported media types for conversion
 */
export enum MediaType {
  VIDEO = 'video',
  AUDIO = 'audio',
  DOCUMENT = 'document'
}

/**
 * Base input/output types for media conversion
 */
export type MediaInput = MediaBuffer | Readable | string;
export type MediaOutput = Writable | string;

/**
 * Base configuration interface for all converters
 */
export interface BaseConfig {
  inputFormat: string;
  outputFormat: string;
  quality?: number;
  metadata?: Record<string, any>;
}

/**
 * Video-specific configuration
 */
export interface VideoConfig extends BaseConfig {
  fps?: number;
  resolution?: {
    width: number;
    height: number;
  };
  codec?: string;
  bitrate?: number;
}

/**
 * Audio-specific configuration
 */
export interface AudioConfig extends BaseConfig {
  sampleRate?: number;
  channels?: number;
  codec?: string;
  bitrate?: number;
}

/**
 * Document-specific configuration
 */
export interface DocumentConfig extends BaseConfig {
  dpi?: number;
  pageRange?: {
    start: number;
    end: number;
  };
}

/**
 * Union type of all converter configurations
 */
export type ConverterConfig = VideoConfig | AudioConfig | DocumentConfig;

/**
 * Stages of the conversion process
 */
export enum ConversionStage {
  INITIALIZING = 'initializing',
  VALIDATING = 'validating',
  CONVERTING = 'converting',
  RETRYING = 'retrying',
  FINALIZING = 'finalizing',
  CLEANING_UP = 'cleaning_up'
}

/**
 * Event types for conversion process
 */
export enum ConversionEventType {
  PROGRESS = 'progress',
  ERROR = 'error',
  COMPLETE = 'complete',
  WARNING = 'warning'
}

/**
 * Progress information for conversion process
 */
export interface ConversionProgress {
  stage: ConversionStage;
  percent: number;
  timestamp: string;
  bytesProcessed?: number;
  totalBytes?: number;
  timeElapsed?: number;
  timeRemaining?: number;
}

/**
 * Interface for media converters
 */
export interface IMediaConverter {
  convert(input: MediaInput, output: MediaOutput, config: ConverterConfig): Promise<void>;
  validateConfig(config: ConverterConfig): boolean;
  getSupportedInputFormats(): string[];
  getSupportedOutputFormats(): string[];
  on(event: ConversionEventType, callback: (data: any) => void): IMediaConverter;
  off(event: ConversionEventType, callback: (data: any) => void): IMediaConverter;
}

/**
 * Interface for media converter factory
 */
export interface IMediaConverterFactory {
  createConverter(type: MediaType): IMediaConverter;
  registerConverter(type: MediaType, converter: new () => IMediaConverter): void;
} 