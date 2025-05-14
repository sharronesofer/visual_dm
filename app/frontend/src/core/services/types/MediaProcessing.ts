import { ServiceError } from '../base/types';
import { Readable } from 'stream';

export enum ProcessingJobStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

export interface ProcessingProgress {
  thumbnail: number;
  conversion: number;
  metadata: number;
  overall: number;
  total: number;
}

export interface ProcessingStats {
  totalJobs: number;
  completedJobs: number;
  failedJobs: number;
  averageProcessingTime: number;
  peakMemoryUsage: number;
  currentMemoryUsage: number;
}

export interface ThumbnailOptions {
  format?: string;
  width?: number;
  height?: number;
  quality?: number;
  fit?: 'cover' | 'contain' | 'fill' | 'inside' | 'outside';
  position?: 'top' | 'right top' | 'right' | 'right bottom' | 'bottom' | 'left bottom' | 'left' | 'left top' | 'center';
  background?: string;
  progressive?: boolean;
  withMetadata?: boolean;
}

export interface ThumbnailResult {
  data: Buffer;
  format: string;
  width: number;
  height: number;
  size: number;
}

export interface ConversionOptions {
  targetFormat: string;
  quality?: number;
  width?: number;
  height?: number;
  fps?: number;
  bitrate?: string;
  codec?: string;
  preset?: string;
  metadata?: Record<string, string>;
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

export interface MetadataExtractionOptions {
  type?: string;
  includeExif?: boolean;
  includeIptc?: boolean;
  includeXmp?: boolean;
  includeIcc?: boolean;
  raw?: boolean;
}

export interface MetadataExtractionResult {
  width?: number;
  height?: number;
  duration?: number;
  bitrate?: number;
  codec?: string;
  fps?: number;
  rotation?: number;
  createdAt?: Date;
  modifiedAt?: Date;
  exif?: Record<string, any>;
  iptc?: Record<string, any>;
  xmp?: Record<string, any>;
  icc?: Record<string, any>;
  raw?: Record<string, any>;
}

export interface MetadataResult {
  format: string;
  size: number;
  width?: number;
  height?: number;
  duration?: number;
  bitrate?: number;
  codec?: string;
  fps?: number;
  rotation?: number;
  createdAt?: Date;
  modifiedAt?: Date;
  exif?: Record<string, any>;
  iptc?: Record<string, any>;
  xmp?: Record<string, any>;
  icc?: Record<string, any>;
  raw?: Record<string, any>;
}

export interface MediaProcessingOptions {
  thumbnail?: ThumbnailOptions;
  conversion?: ConversionOptions;
  metadata?: MetadataExtractionOptions;
}

export interface MediaProcessingResult {
  processingTime: number;
  thumbnail?: ThumbnailResult;
  conversion?: ConversionResult;
  metadata?: MetadataResult;
}

export interface ProcessingJob {
  id: string;
  input: Buffer | string;
  options: MediaProcessingOptions;
  status: ProcessingJobStatus;
  progress: ProcessingProgress;
  startTime: number;
  endTime?: number;
  processingTime?: number;
  error?: ServiceError;
  result?: MediaProcessingResult;
}

export interface StreamProcessingOptions extends MediaProcessingOptions {
  chunkSize?: number;
  maxParallel?: number;
  expectedSize?: number;
  conversion: ConversionOptions;
}

export interface StreamProcessingResult extends MediaProcessingResult {
  bytesProcessed: number;
  totalBytes: number;
  originalFormat: string;
  memoryUsage?: {
    peak: number;
    final: number;
  };
}

export interface ProcessingPlugin {
  id: string;
  name: string;
  version: string;
  type: string;
  initialize(): Promise<void>;
  process(input: Buffer | string, options: any): Promise<any>;
  cleanup(): Promise<void>;
  getSupportedFormats(): string[];
}

export interface PluginManager {
  loadPlugins(directory: string): Promise<ProcessingPlugin[]>;
  unloadPlugin(pluginId: string): Promise<void>;
  getLoadedPlugins(): Promise<ProcessingPlugin[]>;
  getPlugins(): ProcessingPlugin[];
} 