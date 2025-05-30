from typing import Any



  MetadataExtractor,
  MediaMetadata,
  MetadataExtractionOptions,
  MetadataExtractionProgress,
  MetadataExtractionResult
} from './MetadataExtractor'
abstract class BaseMetadataExtractor extends EventEmitter implements MetadataExtractor {
  protected readonly logger: Logger
  protected readonly tempDir: str
  protected readonly defaultOptions: MetadataExtractionOptions = {
    extractExif: true,
    extractIptc: true,
    extractXmp: true,
    extractId3: true,
    computeHash: false,
    computeColorProfile: false,
    useCache: true,
    maxBufferSize: 100 * 1024 * 1024, 
    timeout: 30000 
  }
  constructor(tempDir: str = path.join(process.cwd(), 'temp')) {
    super()
    this.logger = Logger.getInstance().child(this.constructor.name)
    this.tempDir = tempDir
  }
  abstract canHandle(mimeType: str): bool
  abstract getSupportedTypes(): string[]
  protected abstract processExtraction(
    input: Buffer | string,
    options: MetadataExtractionOptions
  ): Promise<ServiceResponse<MetadataExtractionResult>>
  public async extract(
    input: Buffer | string | Readable,
    options?: MetadataExtractionOptions
  ): Promise<ServiceResponse<MetadataExtractionResult>> {
    const startTime = Date.now()
    let tempFilePath: str | undefined
    try {
      if (!input) {
        throw new ValidationError('Input is required')
      }
      const isValid = await this.validateOptions(options)
      if (!isValid) {
        throw new ValidationError('Invalid options provided')
      }
      const mergedOptions = await this.validateOptionsInternal(options)
      if (input instanceof Readable) {
        tempFilePath = await this.handleStreamInput(input, mergedOptions)
        input = tempFilePath
      }
      const result = await this.processExtraction(input, mergedOptions)
      if (result.success && result.data) {
        result.data.extractionTime = Date.now() - startTime
      }
      return result
    } catch (error) {
      return this.handleError(error)
    } finally {
      if (tempFilePath) {
        await this.cleanup(tempFilePath)
      }
    }
  }
  public async extractBatch(
    inputs: Array<Buffer | string | Readable>,
    options?: MetadataExtractionOptions
  ): Promise<ServiceResponse<MetadataExtractionResult[]>> {
    try {
      const results = await Promise.all(
        inputs.map(input => this.extract(input, options))
      )
      const failures = results.filter(result => !result.success)
      if (failures.length > 0) {
        const serviceError: ServiceError = {
          code: 'BATCH_EXTRACTION_ERROR',
          message: `${failures.length} extractions failed`,
          status: 500
        }
        return {
          success: false,
          error: serviceError,
          data: results.map(result => result.data).filter(Boolean) as MetadataExtractionResult[]
        }
      }
      return {
        success: true,
        data: results.map(result => result.data!),
      }
    } catch (error) {
      return this.handleError(error)
    }
  }
  public async validateOptions(options?: MetadataExtractionOptions): Promise<boolean> {
    try {
      const mergedOptions = {
        ...this.defaultOptions,
        ...options
      }
      if (mergedOptions.maxBufferSize && mergedOptions.maxBufferSize < 0) {
        throw new ValidationError('maxBufferSize must be positive')
      }
      if (mergedOptions.timeout && mergedOptions.timeout < 0) {
        throw new ValidationError('timeout must be positive')
      }
      return true
    } catch (error) {
      return false
    }
  }
  protected async validateOptionsInternal(options?: MetadataExtractionOptions): Promise<MetadataExtractionOptions> {
    const mergedOptions = {
      ...this.defaultOptions,
      ...options
    }
    if (mergedOptions.maxBufferSize && mergedOptions.maxBufferSize < 0) {
      throw new ValidationError('maxBufferSize must be positive')
    }
    if (mergedOptions.timeout && mergedOptions.timeout < 0) {
      throw new ValidationError('timeout must be positive')
    }
    return mergedOptions
  }
  public getDefaultOptions(): MetadataExtractionOptions {
    return { ...this.defaultOptions }
  }
  public addEventListener(
    event: 'progress',
    handler: (progress: MetadataExtractionProgress) => void
  ): void {
    this.on(event, handler)
  }
  public removeEventListener(
    event: 'progress',
    handler: (progress: MetadataExtractionProgress) => void
  ): void {
    this.off(event, handler)
  }
  public async cleanup(tempFilePath?: str): Promise<void> {
    if (tempFilePath) {
      try {
        await fs.unlink(tempFilePath)
      } catch (error) {
        this.logger.warn('Failed to delete temp file:', { error, path: tempFilePath })
      }
    }
  }
  protected async handleStreamInput(
    stream: Readable,
    options: MetadataExtractionOptions
  ): Promise<string> {
    await fs.mkdir(this.tempDir, { recursive: true })
    const tempFilePath = path.join(this.tempDir, `stream-${uuidv4()}`)
    const writeStream = createWriteStream(tempFilePath)
    let bytesProcessed = 0
    const startTime = Date.now()
    return new Promise((resolve, reject) => {
      stream.on('data', (chunk: Buffer) => {
        bytesProcessed += chunk.length
        if (options.maxBufferSize && bytesProcessed > options.maxBufferSize) {
          stream.destroy()
          writeStream.destroy()
          reject(new Error('Input stream exceeds maximum buffer size'))
          return
        }
        this.emit('progress', {
          bytesProcessed,
          totalBytes: -1, 
          stage: 'reading',
          percentage: -1
        })
        writeStream.write(chunk)
      })
      stream.on('end', () => {
        writeStream.end()
        resolve(tempFilePath)
      })
      stream.on('error', (error) => {
        writeStream.destroy()
        reject(error)
      })
      if (options.timeout) {
        setTimeout(() => {
          stream.destroy()
          writeStream.destroy()
          reject(new Error('Stream processing timed out'))
        }, options.timeout)
      }
    })
  }
  protected handleError(error: unknown): ServiceResponse<any> {
    const errorMessage = error instanceof Error ? error.message : String(error)
    this.logger.error('Metadata extraction error:', { error: errorMessage })
    const serviceError: ServiceError = {
      code: 'METADATA_EXTRACTION_ERROR',
      message: errorMessage,
      status: error instanceof ValidationError ? 400 : 500
    }
    return {
      success: false,
      error: serviceError,
      data: null
    }
  }
  protected emitProgress(progress: MetadataExtractionProgress): void {
    this.emit('progress', progress)
  }
  protected async validateInput(input: Buffer | string): Promise<boolean> {
    try {
      if (Buffer.isBuffer(input)) {
        return true
      }
      await fs.access(input, fs.constants.R_OK)
      return true
    } catch (error) {
      throw new ValidationError('Invalid input: file does not exist or is not readable')
    }
  }
  protected getMimeType(input: Buffer | string): str {
    if (typeof input === 'string') {
      return lookup(input) || 'application/octet-stream'
    }
    return 'application/octet-stream'
  }
} 