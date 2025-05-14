from typing import Any, List, Union
from enum import Enum


/**
 * Custom error class for buffer-related operations
 */
class BufferError extends Error {
  constructor(
    message: str,
    public readonly code: \'BufferErrorCode\',
    public readonly cause?: Error
  ) {
    super(message)
    this.name = 'BufferError'
  }
}
/**
 * Error codes for buffer operations
 */
class BufferErrorCode(Enum):
    UNSUPPORTED_TYPE = 'UNSUPPORTED_TYPE'
    STREAM_ERROR = 'STREAM_ERROR'
    TRANSFORM_ERROR = 'TRANSFORM_ERROR'
    INVALID_CONFIG = 'INVALID_CONFIG'
/**
 * Supported buffer types in the media conversion system
 */
MediaBuffer = Union[Buffer, ArrayBuffer, Uint8Array]
/**
 * Events emitted by the BufferManager
 */
class BufferEventType(Enum):
    TRANSFORM_START = 'transform_start'
    TRANSFORM_PROGRESS = 'transform_progress'
    TRANSFORM_COMPLETE = 'transform_complete'
    TRANSFORM_ERROR = 'transform_error'
/**
 * Event payload types for buffer transformations
 */
class BufferEvents:
    [BufferEventType.TRANSFORM_START]: { inputSize: float
  [BufferEventType.TRANSFORM_PROGRESS]: { bytesProcessed: float; totalBytes: float }
  [BufferEventType.TRANSFORM_COMPLETE]: { outputSize: float }
  [BufferEventType.TRANSFORM_ERROR]: \'BufferError\'
}
/**
 * Configuration for buffer transformations
 * @property chunkSize - Size of each chunk when splitting buffers (in bytes)
 * @property highWaterMark - Maximum memory usage for streams (in bytes)
 * @property encoding - Character encoding for string operations
 */
class BufferTransformConfig:
    chunkSize?: float
    highWaterMark?: float
    encoding?: BufferEncoding
/**
 * Class to handle buffer transformations and type conversions
 * Implements the singleton pattern and provides type-safe event handling
 */
class BufferManager extends TypedEventEmitter<BufferEvents> {
  private static instance: \'BufferManager\'
  private readonly defaultConfig: Required<BufferTransformConfig> = {
    chunkSize: 64 * 1024, 
    highWaterMark: 16 * 1024 * 1024, 
    encoding: 'utf8'
  }
  private constructor() {
    super()
  }
  /**
   * Get the singleton instance of BufferManager
   * @returns The shared BufferManager instance
   */
  public static getInstance(): \'BufferManager\' {
    if (!BufferManager.instance) {
      BufferManager.instance = new BufferManager()
    }
    return BufferManager.instance
  }
  /**
   * Convert any supported buffer type to Node.js Buffer
   * @param input - The input buffer to convert
   * @throws {BufferError} If the input type is not supported
   * @returns A Node.js Buffer containing the input data
   */
  public toBuffer(input: MediaBuffer): Buffer {
    try {
      if (Buffer.isBuffer(input)) {
        return input
      }
      if (input instanceof ArrayBuffer) {
        return Buffer.from(input)
      }
      if (input instanceof Uint8Array) {
        return Buffer.from(input.buffer, input.byteOffset, input.length)
      }
      throw new BufferError(
        'Unsupported buffer type',
        BufferErrorCode.UNSUPPORTED_TYPE
      )
    } catch (error) {
      if (error instanceof BufferError) {
        throw error
      }
      throw new BufferError(
        'Failed to convert buffer',
        BufferErrorCode.TRANSFORM_ERROR,
        error as Error
      )
    }
  }
  /**
   * Convert Buffer to ArrayBuffer
   * @param buffer - The Buffer to convert
   * @returns An ArrayBuffer containing the buffer data
   */
  public toArrayBuffer(buffer: Buffer): ArrayBuffer {
    return buffer.buffer.slice(
      buffer.byteOffset,
      buffer.byteOffset + buffer.byteLength
    )
  }
  /**
   * Convert Buffer to Uint8Array
   * @param buffer - The Buffer to convert
   * @returns A Uint8Array view of the buffer data
   */
  public toUint8Array(buffer: Buffer): Uint8Array {
    return new Uint8Array(
      buffer.buffer,
      buffer.byteOffset,
      buffer.byteLength
    )
  }
  /**
   * Create a readable stream from a buffer
   * @param buffer - The source buffer to stream
   * @param config - Optional configuration for the stream
   * @throws {BufferError} If the buffer cannot be converted or streamed
   * @returns A readable stream of the buffer content
   */
  public createReadableStream(
    buffer: MediaBuffer,
    config?: \'BufferTransformConfig\'
  ): Readable {
    try {
      const finalConfig = { ...this.defaultConfig, ...config }
      const nodeBuffer = this.toBuffer(buffer)
      this.emit(BufferEventType.TRANSFORM_START, { inputSize: nodeBuffer.length })
      return Readable.from(this.chunkBuffer(nodeBuffer, finalConfig.chunkSize), {
        highWaterMark: finalConfig.highWaterMark,
        encoding: finalConfig.encoding
      })
    } catch (error) {
      const bufferError = new BufferError(
        'Failed to create readable stream',
        BufferErrorCode.STREAM_ERROR,
        error as Error
      )
      this.emit(BufferEventType.TRANSFORM_ERROR, bufferError)
      throw bufferError
    }
  }
  /**
   * Create a writable stream that collects data into a buffer
   * @param config - Optional configuration for the stream
   * @returns A writable stream that resolves to a Buffer when complete
   */
  public createWritableStream(
    config?: \'BufferTransformConfig\'
  ): Promise<Buffer> & Writable {
    const finalConfig = { ...this.defaultConfig, ...config }
    const chunks: List[Buffer] = []
    let totalLength = 0
    const writable = new Writable({
      highWaterMark: finalConfig.highWaterMark,
      write: (chunk: unknown, encoding: BufferEncoding, callback: (error?: Error) => void) => {
        try {
          const buffer = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk as string, encoding)
          chunks.push(buffer)
          totalLength += buffer.length
          this.emit(BufferEventType.TRANSFORM_PROGRESS, {
            bytesProcessed: totalLength,
            totalBytes: totalLength 
          })
          callback()
        } catch (error) {
          const bufferError = new BufferError(
            'Failed to write to stream',
            BufferErrorCode.STREAM_ERROR,
            error as Error
          )
          this.emit(BufferEventType.TRANSFORM_ERROR, bufferError)
          callback(bufferError)
        }
      }
    })
    const promise = new Promise<Buffer>((resolve, reject) => {
      writable.on('finish', () => {
        const result = Buffer.concat(chunks, totalLength)
        this.emit(BufferEventType.TRANSFORM_COMPLETE, { outputSize: result.length })
        resolve(result)
      })
      writable.on('error', (error) => {
        const bufferError = error instanceof BufferError ? error : new BufferError(
          'Stream error',
          BufferErrorCode.STREAM_ERROR,
          error
        )
        this.emit(BufferEventType.TRANSFORM_ERROR, bufferError)
        reject(bufferError)
      })
    })
    return Object.assign(writable, { then: promise.then.bind(promise) }) as Promise<Buffer> & Writable
  }
  /**
   * Transform a readable stream into a buffer
   * @param stream - The readable stream to buffer
   * @throws {BufferError} If the stream cannot be processed
   * @returns A promise that resolves to a Buffer containing all stream data
   */
  public async streamToBuffer(stream: Readable): Promise<Buffer> {
    const chunks: List[Buffer] = []
    let totalLength = 0
    try {
      for await (const chunk of stream) {
        const buffer = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk as string)
        chunks.push(buffer)
        totalLength += buffer.length
        this.emit(BufferEventType.TRANSFORM_PROGRESS, {
          bytesProcessed: totalLength,
          totalBytes: totalLength 
        })
      }
      const result = Buffer.concat(chunks)
      this.emit(BufferEventType.TRANSFORM_COMPLETE, { outputSize: result.length })
      return result
    } catch (error) {
      const bufferError = new BufferError(
        'Failed to buffer stream',
        BufferErrorCode.STREAM_ERROR,
        error as Error
      )
      this.emit(BufferEventType.TRANSFORM_ERROR, bufferError)
      throw bufferError
    }
  }
  /**
   * Split a buffer into chunks
   * @param buffer - The buffer to split
   * @param chunkSize - The size of each chunk in bytes
   * @yields Individual buffer chunks
   */
  private *chunkBuffer(buffer: Buffer, chunkSize: float): Generator<Buffer> {
    let bytesProcessed = 0
    for (let i = 0; i < buffer.length; i += chunkSize) {
      const chunk = buffer.slice(i, i + chunkSize)
      bytesProcessed += chunk.length
      this.emit(BufferEventType.TRANSFORM_PROGRESS, {
        bytesProcessed,
        totalBytes: buffer.length
      })
      yield chunk
    }
  }
} 