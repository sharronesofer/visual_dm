from typing import Any, Dict, List, Union



{ ServiceResponse }
class ConversionOptions:
    targetFormat: str
    format?: str
    quality?: float
    compression?: bool
    fps?: float
    width?: float
    height?: float
    videoCodec?: str
    videoBitrate?: str
    audioCodec?: str
    audioBitrate?: str
    audioChannels?: float
    sampleRate?: float
    chunkSize?: float
    codec?: str
    preset?: str
    bitrate?: Union[str, float]
    metadata?: Dict[str, str>
    stripMetadata?: bool
    preserveMetadata?: bool
    tempDir?: str
    stripExif?: bool
    compressionLevel?: float
    memoryLimit?: float
    preserveAspectRatio?: bool
class StreamOptions:
    chunkSize?: float
    memoryLimit?: float
    preserveMetadata?: bool
    quality?: float
class ConversionProgress:
    bytesProcessed: float
    totalBytes: float
    percent: float
    stage: str
    timeElapsed?: float
    timeRemaining?: float
    currentFile?: str
    memoryUsage: float
class ConversionMetadata:
    format: str
    size: float
    width?: float
    height?: float
    duration?: float
    bitrate?: str
    codec?: str
    fps?: str
    audioCodec?: str
    audioChannels?: float
    audioSampleRate?: float
    createdAt: Date
    [key: str]: unknown
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
class StreamProcessingResult:
    format: str
    size: float
class StreamConversionResult:
    stream: Readable
    format: str
    size: float
class ConversionStats:
    inputSize: float
    outputSize: float
    conversionTime: float
    successCount: float
    failureCount: float
    totalConversions: float
    peakMemoryUsage: float
type ConversionEventHandler<T> = (data: T) => void
class FormatConverter:
    convert(input: Union[Buffer, str, options: ConversionOptions): Awaitable[ServiceResponse<ConversionResult>>]
    convertStream(
    inputStream: Readable,
    outputStream: Writable,
    options: \'ConversionOptions\'
  ): Awaitable[ServiceResponse<StreamProcessingResult>>
    getSupportedFormats(): List[str]
    getSupportedInputFormats(): List[str]
    getSupportedOutputFormats(): List[str]
    canConvertTo(format: str): bool
    cleanup(): Awaitable[None>
abstract class BaseFormatConverter extends EventEmitter implements FormatConverter {
  abstract getSupportedInputFormats(): string[]
  abstract getSupportedOutputFormats(): string[]
  abstract convert(input: Buffer | string, options: ConversionOptions): Promise<ServiceResponse<ConversionResult>>
  abstract canConvertTo(format: str): bool
  async cleanup(): Promise<void> {
  }
  getSupportedFormats(): string[] {
    return [...this.getSupportedInputFormats(), ...this.getSupportedOutputFormats()]
  }
  abstract convertStream(
    inputStream: Readable,
    outputStream: Writable,
    options: \'ConversionOptions\'
  ): Promise<ServiceResponse<StreamProcessingResult>>
}
/**
 * Type-safe event interface for format converters
 */
class FormatConverterEvents:
    progress: \'ConversionProgress\'
    error: ServiceError
    complete: Union[ConversionResult, StreamProcessingResult] 