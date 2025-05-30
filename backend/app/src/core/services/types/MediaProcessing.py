from typing import Any, Dict, List, Union
from enum import Enum


class ProcessingJobStatus(Enum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'
class ProcessingProgress:
    thumbnail: float
    conversion: float
    metadata: float
    overall: float
    total: float
class ProcessingStats:
    totalJobs: float
    completedJobs: float
    failedJobs: float
    averageProcessingTime: float
    peakMemoryUsage: float
    currentMemoryUsage: float
class ThumbnailOptions:
    format?: str
    width?: float
    height?: float
    quality?: float
    fit?: Union['cover', 'contain', 'fill', 'inside', 'outside']
    position?: Union['top', 'right top', 'right', 'right bottom', 'bottom', 'left bottom', 'left', 'left top', 'center']
    background?: str
    progressive?: bool
    withMetadata?: bool
class ThumbnailResult:
    data: Buffer
    format: str
    width: float
    height: float
    size: float
class ConversionOptions:
    targetFormat: str
    quality?: float
    width?: float
    height?: float
    fps?: float
    bitrate?: str
    codec?: str
    preset?: str
    metadata?: Dict[str, str>
class ConversionResult:
    data: Buffer
    format: str
    size: float
    duration?: float
    width?: float
    height?: float
    fps?: float
    bitrate?: str
    codec?: str
class MetadataExtractionOptions:
    type?: str
    includeExif?: bool
    includeIptc?: bool
    includeXmp?: bool
    includeIcc?: bool
    raw?: bool
class MetadataExtractionResult:
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
class MediaProcessingOptions:
    thumbnail?: \'ThumbnailOptions\'
    conversion?: \'ConversionOptions\'
    metadata?: \'MetadataExtractionOptions\'
class MediaProcessingResult:
    processingTime: float
    thumbnail?: \'ThumbnailResult\'
    conversion?: \'ConversionResult\'
    metadata?: \'MetadataResult\'
class ProcessingJob:
    id: str
    input: Union[Buffer, str]
    options: \'MediaProcessingOptions\'
    status: \'ProcessingJobStatus\'
    progress: \'ProcessingProgress\'
    startTime: float
    endTime?: float
    processingTime?: float
    error?: ServiceError
    result?: \'MediaProcessingResult\'
class StreamProcessingOptions:
    chunkSize?: float
    maxParallel?: float
    expectedSize?: float
    conversion: \'ConversionOptions\'
class StreamProcessingResult:
    bytesProcessed: float
    totalBytes: float
    originalFormat: str
    memoryUsage?: {
    peak: float
    final: float
}
class ProcessingPlugin:
    id: str
    name: str
    version: str
    type: str
    initialize(): Awaitable[None>
    process(input: Union[Buffer, str, options: Any): Awaitable[Any>]
    cleanup(): Awaitable[None>
    getSupportedFormats(): List[str]
class PluginManager:
    loadPlugins(directory: str): Awaitable[ProcessingPlugin[]>
    unloadPlugin(pluginId: str): Awaitable[None>
    getLoadedPlugins(): Awaitable[ProcessingPlugin[]>
    getPlugins(): List[ProcessingPlugin] 