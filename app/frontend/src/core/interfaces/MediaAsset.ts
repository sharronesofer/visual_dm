import { BaseEntity } from './BaseEntity';

export interface MediaAsset extends BaseEntity {
  filename: string;
  path: string;
  mimeType: string;
  size: number;
  metadata: Record<string, any>;
  thumbnailUrl?: string;
} 