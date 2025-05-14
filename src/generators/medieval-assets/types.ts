import { Size } from '../../types/common';

export type AssetCategory = 
  | 'parchment'
  | 'border'
  | 'corner'
  | 'icon'
  | 'decoration'
  | 'texture'
  | 'seal'
  | 'ink';

export type AssetVariant =
  | 'aged'
  | 'pristine' 
  | 'weathered'
  | 'elaborate'
  | 'standard'
  | 'minimal';

export interface AssetMetadata {
  id: string;
  category: AssetCategory;
  variant: AssetVariant;
  tags: string[];
  dateCreated: string;
  prompt: string;
  size: Size;
  format: 'png' | 'webp';
  thumbnail?: string;
}

export interface GenerationConfig {
  model: string;
  prompt: string;
  negativePrompt?: string;
  steps: number;
  cfg: number;
  seed?: number;
  width: number;
  height: number;
  batchSize?: number;
}

export interface PostProcessingConfig {
  resize?: Size;
  format?: 'png' | 'webp';
  quality?: number;
  removeBg?: boolean;
  adjustments?: {
    brightness?: number;
    contrast?: number;
    saturation?: number;
    sepia?: number;
  };
}

export interface AssetRequest {
  category: AssetCategory;
  variant: AssetVariant;
  tags?: string[];
  size: Size;
  customPrompt?: string;
  config?: Partial<GenerationConfig>;
  postProcess?: PostProcessingConfig;
}

export interface GeneratedAsset {
  metadata: AssetMetadata;
  buffer: Buffer;
  thumbnail?: Buffer;
}

export interface AssetCatalogEntry extends AssetMetadata {
  path: string;
  thumbnailPath?: string;
  version: number;
  lastModified: string;
  usageCount: number;
  relatedAssets: string[];
} 