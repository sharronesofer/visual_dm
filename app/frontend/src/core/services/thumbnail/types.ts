export interface ThumbnailOptions {
  width?: number;
  height?: number;
  quality?: number;
  format?: 'jpeg' | 'png' | 'webp';
  maintainAspectRatio?: boolean;
  timestamp?: number; // For videos
  page?: number; // For documents
}

export interface ThumbnailResult {
  buffer: Buffer;
  width: number;
  height: number;
  format: string;
  size: number;
}

export interface ThumbnailGenerator {
  generate(input: string | Buffer, options?: ThumbnailOptions): Promise<ThumbnailResult>;
  supports(mimeType: string): boolean;
}

export type ServiceResponse<T> =
  | { success: true; data: T }
  | { success: false; error: ServiceError };

export interface ServiceError {
  code: string;
  message: string;
  details?: any;
} 