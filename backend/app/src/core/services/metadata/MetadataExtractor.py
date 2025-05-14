from typing import Any, Dict, List, Union


class MediaMetadata:
    format: str
    mimeType: str
    size: float
    createdAt?: Date
    modifiedAt?: Date
    title?: str
    description?: str
    author?: str
    copyright?: str
    keywords?: List[str]
    width?: float
    height?: float
    colorSpace?: str
    colorProfile?: str
    orientation?: float
    dpi?: float
    hasAlpha?: bool
    duration?: float
    frameRate?: float
    videoCodec?: str
    videoBitrate?: float
    audioCodec?: str
    audioBitrate?: float
    audioChannels?: float
    audioSampleRate?: float
    album?: str
    artist?: str
    genre?: str
    trackNumber?: float
    year?: float
    pageCount?: float
    wordCount?: float
    lineCount?: float
    characterCount?: float
    documentType?: str
    application?: str
    exif?: Dict[str, Any>
    iptc?: Dict[str, Any>
    xmp?: Dict[str, Any>
    id3?: Dict[str, Any>
    custom?: Dict[str, Any>
class MetadataExtractionOptions:
    type?: str
    includeExif?: bool
    includeIptc?: bool
    includeXmp?: bool
    includeIcc?: bool
    raw?: bool
class MetadataExtractionProgress:
    bytesProcessed: float
    totalBytes: float
    stage: str
    percentage: float
class MetadataExtractionResult:
    metadata: \'MediaMetadata\'
    cached: bool
    extractionTime: float
class MetadataResult:
    format: str
    size: float
    width?: float
    height?: float
    duration?: float
    bitrate?: float
    codec?: str
    fps?: float
    rotation?: float
    createdAt?: Date
    modifiedAt?: Date
    exif?: Dict[str, Any>
    iptc?: Dict[str, Any>
    xmp?: Dict[str, Any>
    icc?: Dict[str, Any>
    raw?: Dict[str, Any>
class MetadataExtractor:
    /**
   * Check if this extractor can handle the given file type
   */
  canHandle(mimeType: str): bool
    /**
   * Get list of supported file types
   */
  getSupportedTypes(): List[str]
    /**
   * Extract metadata from a file
   */
  extract(
    input: Union[Buffer, str, Readable,
    options?: \'MetadataExtractionOptions\'
  ): Awaitable[ServiceResponse<MetadataExtractionResult>>]
    /**
   * Extract metadata from multiple files
   */
  extractBatch(
    inputs: Union[List[Buffer, str, Readable>,
    options?: \'MetadataExtractionOptions\'
  ): Awaitable[ServiceResponse<MetadataExtractionResult[]>>]
    /**
   * Validate extraction options
   */
  validateOptions(options?: MetadataExtractionOptions): Awaitable[bool>
    /**
   * Get default extraction options
   */
  getDefaultOptions(): \'MetadataExtractionOptions\'
    /**
   * Add event listener for progress updates
   */
  addEventListener(
    event: 'progress',
    handler: (progress: MetadataExtractionProgress) => None
  ): None
    /**
   * Remove event listener
   */
  removeEventListener(
    event: 'progress',
    handler: (progress: MetadataExtractionProgress) => None
  ): None
    /**
   * Clean up resources
   */
  cleanup(): Awaitable[None>
    /**
   * Check if the extractor can handle the given input format
   */
  canExtractFrom(mimeType: str): bool
    /**
   * Get list of supported input formats
   */
  getSupportedFormats(): List[str]
    /**
   * Extract metadata from input
   */
  extract(input: Union[Buffer, str, options: MetadataExtractionOptions): Awaitable[ServiceResponse<MetadataResult>>]
    /**
   * Extract metadata from input stream
   */
  extractFromStream(inputStream: Readable, options?: MetadataExtractionOptions): Awaitable[ServiceResponse<Any>> 