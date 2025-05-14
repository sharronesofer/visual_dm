import { BaseEntity } from './BaseEntity';
import { MediaAsset } from './MediaAsset';

export interface Collection extends BaseEntity {
  name: string;
  description?: string;
  assets: MediaAsset[];
  tags: string[];
} 