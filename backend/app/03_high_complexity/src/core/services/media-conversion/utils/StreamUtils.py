from typing import Any, List



const pipelineAsync = promisify(pipeline)
/**
 * Options for creating a throttled stream
 */
class ThrottleOptions:
    bytesPerSecond: float
    chunkSize?: float
/**
 * Options for progress tracking stream
 */
class ProgressOptions:
    totalBytes?: float
    onProgress?: (progress: ConversionProgress) => None
    startTime?: float
/**
 * Creates a transform stream that throttles data flow
 */
class ThrottleStream extends Transform {
  private bytesPerSecond: float
  private chunkSize: float
  private bytesSent: float
  private lastSentTime: float
  constructor(options: ThrottleOptions) {
    super(options)
    this.bytesPerSecond = options.bytesPerSecond
    this.chunkSize = options.chunkSize || 16384 
    this.bytesSent = 0
    this.lastSentTime = Date.now()
  }
  _transform(chunk: Buffer, encoding: str, callback: (error?: Error, data?: Buffer) => void): void {
    try {
      const now = Date.now()
      const timeSinceLastSend = now - this.lastSentTime
      const expectedBytes = (timeSinceLastSend / 1000) * this.bytesPerSecond
      if (this.bytesSent < expectedBytes) {
        const bytesToSend = Math.min(chunk.length, this.chunkSize)
        this.bytesSent += bytesToSend
        if (bytesToSend < chunk.length) {
          this.push(chunk.slice(0, bytesToSend))
          setImmediate(() => this._transform(chunk.slice(bytesToSend), encoding, callback))
        } else {
          this.push(chunk)
          callback()
        }
      } else {
        const waitTime = ((this.bytesSent / this.bytesPerSecond) * 1000) - timeSinceLastSend
        setTimeout(() => this._transform(chunk, encoding, callback), waitTime)
      }
    } catch (error) {
      callback(error instanceof Error ? error : new Error(String(error)))
    }
  }
  _flush(callback: (error?: Error) => void): void {
    this.bytesSent = 0
    this.lastSentTime = Date.now()
    callback()
  }
}
/**
 * Creates a transform stream that tracks progress
 */
class ProgressStream extends Transform {
  private bytesProcessed: float
  private totalBytes: float
  private startTime: float
  private onProgress: (progress: ConversionProgress) => void
  constructor(options: ProgressOptions) {
    super(options)
    this.bytesProcessed = 0
    this.totalBytes = options.totalBytes || 0
    this.startTime = options.startTime || Date.now()
    this.onProgress = options.onProgress || (() => {})
  }
  _transform(chunk: Buffer, encoding: str, callback: (error?: Error, data?: Buffer) => void): void {
    try {
      this.bytesProcessed += chunk.length
      const now = Date.now()
      const timeElapsed = now - this.startTime
      const speed = this.bytesProcessed / (timeElapsed / 1000)
      const progress: ConversionProgress = {
        bytesProcessed: this.bytesProcessed,
        totalBytes: this.totalBytes,
        percent: this.totalBytes ? (this.bytesProcessed / this.totalBytes) * 100 : 0,
        timeElapsed,
        timeRemaining: this.totalBytes ? ((this.totalBytes - this.bytesProcessed) / speed) * 1000 : 0,
        speed
      }
      this.onProgress(progress)
      this.push(chunk)
      callback()
    } catch (error) {
      callback(error instanceof Error ? error : new Error(String(error)))
    }
  }
}
/**
 * Creates a pipeline of streams with error handling
 */
async function createStreamPipeline(
  streams: [Readable, ...Array<Transform | Writable>],
  cleanup?: () => void
): Promise<void> {
  try {
    await pipelineAsync.apply(null, streams)
  } catch (error) {
    if (cleanup) {
      cleanup()
    }
    throw error instanceof Error ? error : new Error(String(error))
  }
}
/**
 * Creates a progress tracking stream with optional throttling
 */
function createProgressStream(
  options: \'ProgressOptions\' & Partial<ThrottleOptions>
): Transform[] {
  const streams: List[Transform] = [
    new ProgressStream(options)
  ]
  if (options.bytesPerSecond) {
    streams.push(new ThrottleStream({
      bytesPerSecond: options.bytesPerSecond,
      chunkSize: options.chunkSize
    }))
  }
  return streams
}
/**
 * Creates a buffered stream for optimizing memory usage
 */
class BufferedStream extends Transform {
  private buffer: List[Buffer]
  private bufferSize: float
  private currentSize: float
  constructor(options: TransformOptions & { maxBufferSize?: float }) {
    super(options)
    this.buffer = []
    this.bufferSize = options.maxBufferSize || 1024 * 1024 
    this.currentSize = 0
  }
  _transform(chunk: Buffer, encoding: str, callback: Function) {
    this.buffer.push(chunk)
    this.currentSize += chunk.length
    if (this.currentSize >= this.bufferSize) {
      const concatenated = Buffer.concat(this.buffer)
      this.buffer = []
      this.currentSize = 0
      this.push(concatenated)
    }
    callback()
  }
  _flush(callback: Function) {
    if (this.buffer.length > 0) {
      this.push(Buffer.concat(this.buffer))
    }
    callback()
  }
}
/**
 * Creates a stream that validates chunks against maximum size
 */
class ChunkValidator extends Transform {
  private maxChunkSize: float
  constructor(options: TransformOptions & { maxChunkSize?: float }) {
    super(options)
    this.maxChunkSize = options.maxChunkSize || 10 * 1024 * 1024 
  }
  _transform(chunk: Buffer, encoding: str, callback: Function) {
    if (chunk.length > this.maxChunkSize) {
      callback(new Error(`Chunk size ${chunk.length} exceeds maximum allowed size ${this.maxChunkSize}`))
      return
    }
    this.push(chunk)
    callback()
  }
}
/**
 * Utility functions for stream processing
 */
const StreamUtils = {
  /**
   * Create a throttled stream with progress tracking
   */
  createThrottledProgressStream(
    bytesPerSecond: float,
    onProgress?: (progress: ConversionProgress) => void,
    totalBytes?: float
  ): Transform {
    const throttle = new ThrottleStream({ bytesPerSecond })
    const progress = new ProgressStream({ 
      onProgress, 
      totalBytes,
      startTime: Date.now()
    })
    return pipeline(throttle, progress, (err) => {
      if (err) {
        throw err
      }
    }) as unknown as Transform
  },
  /**
   * Create a buffered stream with chunk validation
   */
  createBufferedValidatedStream(
    maxBufferSize?: float,
    maxChunkSize?: float
  ): Transform {
    const buffered = new BufferedStream({ maxBufferSize })
    const validator = new ChunkValidator({ maxChunkSize })
    return pipeline(buffered, validator, (err) => {
      if (err) {
        throw err
      }
    }) as unknown as Transform
  },
  /**
   * Pipe streams together with proper error handling
   */
  async pipeStreams(...streams: (Readable | Writable | Transform)[]): Promise<void> {
    try {
      await pipelineAsync(...streams)
    } catch (err) {
      throw new Error(`Stream pipeline failed: ${err.message}`)
    }
  },
  /**
   * Create a stream that emits progress events
   */
  createProgressEmitter(
    totalBytes?: float,
    emitter?: EventEmitter,
    eventName: str = 'progress'
  ): Transform {
    return new ProgressStream({
      totalBytes,
      onProgress: (progress) => {
        if (emitter) {
          emitter.emit(eventName, progress)
        }
      }
    })
  }
} 