import { BaseEntity } from '../services/base/BaseEntity';

/**
 * Collection interface: represents a collection of media assets.
 */
export interface Collection extends BaseEntity {
  name: string;
  description?: string;
  coverImageUrl?: string;
  mediaAssets: string[]; // Array of MediaAsset IDs
  visibility: 'public' | 'private' | 'unlisted';
  metadata?: Record<string, any>;
}

/**
 * Concrete implementation of Collection with management methods and validation.
 */
export class CollectionModel implements Collection {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  isActive: boolean;
  name: string;
  description?: string;
  coverImageUrl?: string;
  mediaAssets: string[];
  visibility: 'public' | 'private' | 'unlisted';
  metadata?: Record<string, any>;

  constructor(data: Collection) {
    this.id = data.id;
    this.createdAt = data.createdAt;
    this.updatedAt = data.updatedAt;
    this.isActive = data.isActive;
    this.name = data.name;
    this.description = data.description;
    this.coverImageUrl = data.coverImageUrl;
    this.mediaAssets = Array.isArray(data.mediaAssets) ? [...data.mediaAssets] : [];
    this.visibility = data.visibility;
    this.metadata = data.metadata ? { ...data.metadata } : {};
    this.validate();
  }

  /**
   * Add a media asset ID to the collection.
   */
  addMediaAsset(id: string): void {
    if (!this.mediaAssets.includes(id)) {
      this.mediaAssets.push(id);
    }
  }

  /**
   * Remove a media asset ID from the collection. Returns true if removed.
   */
  removeMediaAsset(id: string): boolean {
    const idx = this.mediaAssets.indexOf(id);
    if (idx !== -1) {
      this.mediaAssets.splice(idx, 1);
      return true;
    }
    return false;
  }

  /**
   * Check if the collection contains a media asset ID.
   */
  hasMediaAsset(id: string): boolean {
    return this.mediaAssets.includes(id);
  }

  /**
   * Set a metadata field.
   */
  setMetadata(key: string, value: any): void {
    if (!this.metadata) this.metadata = {};
    this.metadata[key] = value;
  }

  /**
   * Get a metadata field.
   */
  getMetadata(key: string): any {
    return this.metadata ? this.metadata[key] : undefined;
  }

  /**
   * Validate the collection fields.
   * Throws an error if validation fails.
   */
  validate() {
    if (!this.name || typeof this.name !== 'string') {
      throw new Error('Collection name is required.');
    }
    const allowedVisibilities = ['public', 'private', 'unlisted'];
    if (!allowedVisibilities.includes(this.visibility)) {
      throw new Error(`Invalid visibility: ${this.visibility}`);
    }
    if (!Array.isArray(this.mediaAssets)) {
      throw new Error('mediaAssets must be an array of IDs.');
    }
    for (const id of this.mediaAssets) {
      if (typeof id !== 'string' || !id) {
        throw new Error('Each mediaAsset ID must be a non-empty string.');
      }
    }
  }
} 