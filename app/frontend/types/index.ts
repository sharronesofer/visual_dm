export interface MediaAsset {
  id: string;
  filename: string;
  mimeType: string;
  type: 'image' | 'video' | 'audio' | 'document';
  size: number;
  width?: number;
  height?: number;
  duration?: number;
  thumbnailUrl: string | null;
  createdAt?: string;
  updatedAt?: string;
  metadata?: Record<string, unknown>;
} 