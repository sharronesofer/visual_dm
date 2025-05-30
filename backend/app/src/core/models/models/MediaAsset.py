from typing import Any


/**
 * MediaAsset interface: represents a media file in the system.
 */
class MediaAsset:
    title: str
    description?: str
    fileUrl: str
    fileType: str
    fileSize: float
    duration?: float
    dimensions?: { width: float
    height: float 
  metadata?: Record<string, any>
}
/**
 * Concrete implementation of MediaAsset with validation logic.
 */
class MediaAssetModel implements MediaAsset {
  id: str
  createdAt: Date
  updatedAt: Date
  isActive: bool
  title: str
  description?: str
  fileUrl: str
  fileType: str
  fileSize: float
  duration?: float
  dimensions?: { width: float; height: float }
  metadata?: Record<string, any>
  constructor(data: MediaAsset) {
    this.id = data.id
    this.createdAt = data.createdAt
    this.updatedAt = data.updatedAt
    this.isActive = data.isActive
    this.title = data.title
    this.description = data.description
    this.fileUrl = data.fileUrl
    this.fileType = data.fileType
    this.fileSize = data.fileSize
    this.duration = data.duration
    this.dimensions = data.dimensions
    this.metadata = data.metadata
    this.validate()
  }
  /**
   * Validate the media asset fields.
   * Throws an error if validation fails.
   */
  validate() {
    if (!this.title || !this.fileUrl || !this.fileType || typeof this.fileSize !== 'number') {
      throw new Error('Missing required MediaAsset fields.')
    }
    if (this.fileSize < 0) {
      throw new Error('fileSize must be non-negative.')
    }
    const allowedTypes = ['image/png', 'image/jpeg', 'image/gif', 'video/mp4', 'audio/mpeg', 'application/pdf']
    if (!allowedTypes.includes(this.fileType)) {
      throw new Error(`Unsupported fileType: ${this.fileType}`)
    }
    if (this.dimensions) {
      if (typeof this.dimensions.width !== 'number' || typeof this.dimensions.height !== 'number') {
        throw new Error('dimensions must include width and height as numbers.')
      }
    }
  }
} 