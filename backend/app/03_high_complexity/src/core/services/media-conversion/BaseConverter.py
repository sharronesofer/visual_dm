from typing import Any, List



  IMediaConverter,
  ConversionEventType,
  ConversionProgress,
  ConversionStage,
  BaseConfig,
  MediaInput,
  MediaOutput,
  ConverterConfig as MediaConverterConfig
} from './types'
/**
 * Event payload types for media conversion
 */
class ConverterEvents:
    [ConversionEventType.PROGRESS]: ConversionProgress
    [ConversionEventType.ERROR]: Error
    [ConversionEventType.COMPLETE]: None
    [ConversionEventType.WARNING]: str
/**
 * Abstract base class for all media converters
 * Implements common functionality and event handling
 */
abstract class BaseConverter extends TypedEventEmitter<ConverterEvents> implements IMediaConverter {
  protected supportedInputFormats: List[string] = []
  protected supportedOutputFormats: List[string] = []
  protected readonly bufferManager: BufferManager
  constructor() {
    super()
    this.bufferManager = BufferManager.getInstance()
  }
  /**
   * Abstract method to be implemented by specific converters
   */
  public abstract convert(
    input: MediaInput,
    output: MediaOutput,
    config: BaseConfig
  ): Promise<void>
  /**
   * Get list of supported input formats
   */
  public getSupportedInputFormats(): string[] {
    return [...this.supportedInputFormats]
  }
  /**
   * Get list of supported output formats
   */
  public getSupportedOutputFormats(): string[] {
    return [...this.supportedOutputFormats]
  }
  /**
   * Validate the conversion configuration
   */
  public validateConfig(config: MediaConverterConfig): bool {
    if (!config.inputFormat || !config.outputFormat) {
      return false
    }
    if (!this.supportedInputFormats.includes(config.inputFormat.toLowerCase())) {
      return false
    }
    if (!this.supportedOutputFormats.includes(config.outputFormat.toLowerCase())) {
      return false
    }
    if (config.quality !== undefined && (config.quality < 0 || config.quality > 100)) {
      return false
    }
    return true
  }
  /**
   * Protected helper method to emit progress updates
   */
  protected emitProgress(stage: ConversionStage, percent: float): void {
    const progress: ConversionProgress = {
      stage,
      percent,
      timestamp: new Date().toISOString()
    }
    this.emit(ConversionEventType.PROGRESS, progress)
  }
  /**
   * Protected helper method to emit errors
   */
  protected emitError(error: Error): void {
    this.emit(ConversionEventType.ERROR, error)
  }
  /**
   * Protected helper method to emit completion
   */
  protected emitComplete(): void {
    this.emit(ConversionEventType.COMPLETE, undefined)
  }
  /**
   * Protected helper method to emit warnings
   */
  protected emitWarning(warning: str): void {
    this.emit(ConversionEventType.WARNING, warning)
  }
  /**
   * Protected helper method to create a readable stream from input
   */
  protected async createInputStream(input: MediaInput, config?: BufferTransformConfig): Promise<Readable> {
    if (input instanceof Readable) {
      return input
    }
    if (typeof input === 'string') {
      const fs = require('fs')
      return fs.createReadStream(input, {
        highWaterMark: config?.highWaterMark,
        encoding: config?.encoding
      })
    }
    return this.bufferManager.createReadableStream(input as MediaBuffer, config)
  }
  /**
   * Protected helper method to create a writable stream from output
   */
  protected createOutputStream(output: MediaOutput, config?: BufferTransformConfig): Writable {
    if (output instanceof Writable) {
      return output
    }
    if (typeof output === 'string') {
      const fs = require('fs')
      return fs.createWriteStream(output, {
        highWaterMark: config?.highWaterMark,
        encoding: config?.encoding
      })
    }
    return this.bufferManager.createWritableStream(config)
  }
  /**
   * Protected helper method to calculate progress
   */
  protected calculateProgress(
    bytesProcessed: float,
    totalBytes: float,
    startTime: float
  ): ConversionProgress {
    const timeElapsed = (Date.now() - startTime) / 1000
    const percent = (bytesProcessed / totalBytes) * 100
    let timeRemaining: float | undefined
    if (percent > 0) {
      const bytesPerSecond = bytesProcessed / timeElapsed
      const remainingBytes = totalBytes - bytesProcessed
      timeRemaining = remainingBytes / bytesPerSecond
    }
    return {
      stage: ConversionStage.CONVERTING,
      percent,
      timestamp: new Date().toISOString(),
      bytesProcessed,
      totalBytes,
      timeElapsed,
      timeRemaining
    }
  }
  /**
   * Protected helper method to convert input to buffer
   */
  protected async toBuffer(input: MediaInput): Promise<Buffer> {
    if (Buffer.isBuffer(input)) {
      return input
    }
    if (input instanceof Readable) {
      return this.bufferManager.streamToBuffer(input)
    }
    if (typeof input === 'string') {
      const fs = require('fs').promises
      return fs.readFile(input)
    }
    return this.bufferManager.toBuffer(input as MediaBuffer)
  }
} 