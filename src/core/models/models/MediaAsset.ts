import { BaseEntity } from '../services/base/BaseEntity';

/**
 * MediaAsset interface: represents a media file in the system.
 */
export interface MediaAsset extends BaseEntity {
  title: string;
  description?: string;
  fileUrl: string;
  fileType: string;
  fileSize: number; // bytes
  duration?: number; // seconds (for audio/video)
  dimensions?: { width: number; height: number }; // for images/video
  metadata?: Record<string, any>;
}

/**
 * Concrete implementation of MediaAsset with validation logic.
 */
export class MediaAssetModel implements MediaAsset {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  isActive: boolean;
  title: string;
  description?: string;
  fileUrl: string;
  fileType: string;
  fileSize: number;
  duration?: number;
  dimensions?: { width: number; height: number };
  metadata?: Record<string, any>;

  constructor(data: MediaAsset) {
    this.id = data.id;
    this.createdAt = data.createdAt;
    this.updatedAt = data.updatedAt;
    this.isActive = data.isActive;
    this.title = data.title;
    this.description = data.description;
    this.fileUrl = data.fileUrl;
    this.fileType = data.fileType;
    this.fileSize = data.fileSize;
    this.duration = data.duration;
    this.dimensions = data.dimensions;
    this.metadata = data.metadata;
    this.validate();
  }

  /**
   * Validate the media asset fields.
   * Throws an error if validation fails.
   */
  validate() {
    if (!this.title || !this.fileUrl || !this.fileType || typeof this.fileSize !== 'number') {
      throw new Error('Missing required MediaAsset fields.');
    }
    if (this.fileSize < 0) {
      throw new Error('fileSize must be non-negative.');
    }
    // Example: restrict fileType to common types
    const allowedTypes = ['image/png', 'image/jpeg', 'image/gif', 'video/mp4', 'audio/mpeg', 'application/pdf'];
    if (!allowedTypes.includes(this.fileType)) {
      throw new Error(`Unsupported fileType: ${this.fileType}`);
    }
    if (this.dimensions) {
      if (typeof this.dimensions.width !== 'number' || typeof this.dimensions.height !== 'number') {
        throw new Error('dimensions must include width and height as numbers.');
      }
    }
  }
} 