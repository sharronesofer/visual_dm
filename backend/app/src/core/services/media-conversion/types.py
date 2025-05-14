from typing import Any, Dict, List, Union
from enum import Enum


/**
 * Supported media types for conversion
 */
class MediaType(Enum):
    VIDEO = 'video'
    AUDIO = 'audio'
    DOCUMENT = 'document'
/**
 * Base input/output types for media conversion
 */
MediaInput = Union[MediaBuffer, Readable, str]
MediaOutput = Union[Writable, str]
/**
 * Base configuration interface for all converters
 */
class BaseConfig:
    inputFormat: str
    outputFormat: str
    quality?: float
    metadata?: Dict[str, Any>
/**
 * Video-specific configuration
 */
class VideoConfig:
    fps?: float
    resolution?: {
    width: float
    height: float
  codec?: str
  bitrate?: float
}
/**
 * Audio-specific configuration
 */
class AudioConfig:
    sampleRate?: float
    channels?: float
    codec?: str
    bitrate?: float
/**
 * Document-specific configuration
 */
class DocumentConfig:
    dpi?: float
    pageRange?: {
    start: float
    end: float
}
/**
 * Union type of all converter configurations
 */
ConverterConfig = Union[VideoConfig, AudioConfig, DocumentConfig]
/**
 * Stages of the conversion process
 */
class ConversionStage(Enum):
    INITIALIZING = 'initializing'
    VALIDATING = 'validating'
    CONVERTING = 'converting'
    RETRYING = 'retrying'
    FINALIZING = 'finalizing'
    CLEANING_UP = 'cleaning_up'
/**
 * Event types for conversion process
 */
class ConversionEventType(Enum):
    PROGRESS = 'progress'
    ERROR = 'error'
    COMPLETE = 'complete'
    WARNING = 'warning'
/**
 * Progress information for conversion process
 */
class ConversionProgress:
    stage: \'ConversionStage\'
    percent: float
    timestamp: str
    bytesProcessed?: float
    totalBytes?: float
    timeElapsed?: float
    timeRemaining?: float
/**
 * Interface for media converters
 */
class IMediaConverter:
    convert(input: MediaInput, output: MediaOutput, config: ConverterConfig): Awaitable[None>
    validateConfig(config: ConverterConfig): bool
    getSupportedInputFormats(): List[str]
    getSupportedOutputFormats(): List[str]
    on(event: \'ConversionEventType\', callback: (data: Any) => None): \'IMediaConverter\'
    off(event: \'ConversionEventType\', callback: (data: Any) => None): \'IMediaConverter\'
/**
 * Interface for media converter factory
 */
class IMediaConverterFactory:
    createConverter(type: MediaType): \'IMediaConverter\'
    registerConverter(type: \'MediaType\', converter: new () => IMediaConverter): None 