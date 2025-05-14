import { ServiceResponse } from '../base/types';
import { Readable } from 'stream';

export interface MediaMetadata {
  // Common metadata fields
  format: string;
  mimeType: string;
  size: number;
  createdAt?: Date;
  modifiedAt?: Date;
  title?: string;
  description?: string;
  author?: string;
  copyright?: string;
  keywords?: string[];
  
  // Image-specific metadata
  width?: number;
  height?: number;
  colorSpace?: string;
  colorProfile?: string;
  orientation?: number;
  dpi?: number;
  hasAlpha?: boolean;
  
  // Video-specific metadata
  duration?: number;
  frameRate?: number;
  videoCodec?: string;
  videoBitrate?: number;
  audioCodec?: string;
  audioBitrate?: number;
  audioChannels?: number;
  audioSampleRate?: number;
  
  // Audio-specific metadata
  album?: string;
  artist?: string;
  genre?: string;
  trackNumber?: number;
  year?: number;
  
  // Document-specific metadata
  pageCount?: number;
  wordCount?: number;
  lineCount?: number;
  characterCount?: number;
  documentType?: string;
  application?: string;
  
  // Raw metadata storage
  exif?: Record<string, any>;
  iptc?: Record<string, any>;
  xmp?: Record<string, any>;
  id3?: Record<string, any>;
  custom?: Record<string, any>;
}

export interface MetadataExtractionOptions {
  type?: string;
  includeExif?: boolean;
  includeIptc?: boolean;
  includeXmp?: boolean;
  includeIcc?: boolean;
  raw?: boolean;
}

export interface MetadataExtractionProgress {
  bytesProcessed: number;
  totalBytes: number;
  stage: string;
  percentage: number;
}

export interface MetadataExtractionResult {
  metadata: MediaMetadata;
  cached: boolean;
  extractionTime: number;
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

export interface MetadataExtractor {
  /**
   * Check if this extractor can handle the given file type
   */
  canHandle(mimeType: string): boolean;
  
  /**
   * Get list of supported file types
   */
  getSupportedTypes(): string[];
  
  /**
   * Extract metadata from a file
   */
  extract(
    input: Buffer | string | Readable,
    options?: MetadataExtractionOptions
  ): Promise<ServiceResponse<MetadataExtractionResult>>;
  
  /**
   * Extract metadata from multiple files
   */
  extractBatch(
    inputs: Array<Buffer | string | Readable>,
    options?: MetadataExtractionOptions
  ): Promise<ServiceResponse<MetadataExtractionResult[]>>;
  
  /**
   * Validate extraction options
   */
  validateOptions(options?: MetadataExtractionOptions): Promise<boolean>;
  
  /**
   * Get default extraction options
   */
  getDefaultOptions(): MetadataExtractionOptions;
  
  /**
   * Add event listener for progress updates
   */
  addEventListener(
    event: 'progress',
    handler: (progress: MetadataExtractionProgress) => void
  ): void;
  
  /**
   * Remove event listener
   */
  removeEventListener(
    event: 'progress',
    handler: (progress: MetadataExtractionProgress) => void
  ): void;
  
  /**
   * Clean up resources
   */
  cleanup(): Promise<void>;

  /**
   * Check if the extractor can handle the given input format
   */
  canExtractFrom(mimeType: string): boolean;

  /**
   * Get list of supported input formats
   */
  getSupportedFormats(): string[];

  /**
   * Extract metadata from input
   */
  extract(input: Buffer | string, options: MetadataExtractionOptions): Promise<ServiceResponse<MetadataResult>>;

  /**
   * Extract metadata from input stream
   */
  extractFromStream(inputStream: Readable, options?: MetadataExtractionOptions): Promise<ServiceResponse<any>>;
} 