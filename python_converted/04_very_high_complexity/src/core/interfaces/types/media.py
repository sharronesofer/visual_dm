from typing import Any, Dict, List, Union
from enum import Enum



/**
 * Supported media types
 */
class MediaType(Enum):
    IMAGE = 'image'
    VIDEO = 'video'
    AUDIO = 'audio'
    DOCUMENT = 'document'
/**
 * Media format interface
 */
class MediaFormat:
    mimeType: str
    extension: str
    type: \'MediaType\'
/**
 * Media metadata interface
 */
class MediaMetadata:
    width?: float
    height?: float
    duration?: float
    size: float
    format: \'MediaFormat\'
    [key: str]: Any
/**
 * Media entity interface
 */
class Media:
    filename: str
    path: str
    metadata: \'MediaMetadata\'
    type: \'MediaType\'
    thumbnailPath?: str
/**
 * Media processing status
 */
class MediaProcessingStatus(Enum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'
/**
 * Media processing options
 */
class MediaProcessingOptions:
    quality?: float
    format?: str
    width?: float
    height?: float
    preserveAspectRatio?: bool
    metadata?: Dict[str, Any>
/**
 * Media processing result
 */
class MediaProcessingResult:
    data: Buffer
    metadata: \'MediaMetadata\'
    status: \'MediaProcessingStatus\'
    error?: Error
/**
 * Media input types
 */
MediaInput = Union[Buffer, Readable, str]
/**
 * Media output types
 */
MediaOutput = Union[Buffer, Writable, str]
/**
 * Media conversion configuration
 */
class MediaConversionConfig:
    inputFormat: str
    outputFormat: str
    quality?: float
    metadata?: Dict[str, Any>
    options?: \'MediaProcessingOptions\'
/**
 * Media conversion progress
 */
class MediaConversionProgress:
    bytesProcessed: float
    totalBytes: float
    percent: float
    stage: str
    timestamp: float
/**
 * Media validation result
 */
class MediaValidationResult:
    isValid: bool
    errors?: List[str]
    metadata?: \'MediaMetadata\'
/**
 * Media storage configuration
 */
class MediaStorageConfig:
    basePath: str
    createThumbnails?: bool
    thumbnailOptions?: \'MediaProcessingOptions\'
    preserveOriginal?: bool
    maxSize?: float
    allowedTypes?: List[MediaType]
    allowedFormats?: List[str]
/**
 * Type guard for Buffer
 */
function isBuffer(input: MediaInput): input is Buffer {
  return Buffer.isBuffer(input)
}
/**
 * Type guard for Readable
 */
function isReadable(input: MediaInput): input is Readable {
  return input instanceof Readable
}
/**
 * Type guard for file path
 */
function isFilePath(input: MediaInput): input is string {
  return typeof input === 'string' && input.includes('/')
} 