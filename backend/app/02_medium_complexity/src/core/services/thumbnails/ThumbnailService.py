from typing import Any, List



class ThumbnailServiceConfig:
    cache?: ThumbnailCacheConfig
class ThumbnailService {
  private readonly generators: List[ThumbnailGenerator]
  private readonly logger: Logger
  private readonly cache: ThumbnailCache
  constructor(config?: ThumbnailServiceConfig) {
    this.generators = [
      new ImageThumbnailGenerator(),
      new VideoThumbnailGenerator(),
      new AudioThumbnailGenerator(),
      new DocumentThumbnailGenerator()
    ]
    this.logger = Logger.getInstance().child('ThumbnailService')
    this.cache = new ThumbnailCache(config?.cache)
  }
  async initialize(): Promise<void> {
    await this.cache.initialize()
  }
  async generateThumbnail(file: Buffer | string, options?: ThumbnailOptions): Promise<ServiceResponse<ThumbnailResult>> {
    try {
      const cachedResult = await this.cache.get(file, options || {})
      if (cachedResult) {
        this.logger.debug('Thumbnail found in cache')
        return {
          success: true,
          data: cachedResult
        }
      }
      let mimeType: str
      if (typeof file === 'string') {
        mimeType = lookup(file) || ''
      } else {
        const fileType = await import('file-type')
        const type = await fileType.fileTypeFromBuffer(file)
        mimeType = type?.mime || ''
      }
      if (!mimeType) {
        return {
          success: false,
          error: new ValidationError('Could not determine file type', {
            code: 'UNKNOWN_TYPE',
            status: 400
          }),
          data: null
        }
      }
      const generator = this.findGenerator(mimeType)
      if (!generator) {
        return {
          success: false,
          error: new ValidationError(`Unsupported file type: ${mimeType}`, {
            code: 'UNSUPPORTED_TYPE',
            status: 400
          }),
          data: null
        }
      }
      const result = await generator.generateThumbnail(file, options)
      if (result.success && result.data) {
        await this.cache.set(file, options || {}, result.data)
      }
      return result
    } catch (error) {
      this.logger.error('Failed to generate thumbnail', error instanceof Error ? error : undefined, {
        error: error instanceof Error ? error.message : 'Unknown error'
      })
      return {
        success: false,
        error: new ValidationError('Failed to generate thumbnail', {
          code: 'GENERATION_ERROR',
          status: 500
        }),
        data: null
      }
    }
  }
  private findGenerator(mimeType: str): ThumbnailGenerator | undefined {
    return this.generators.find(generator => generator.canHandle(mimeType))
  }
  async cleanup(): Promise<void> {
    await Promise.all([
      ...this.generators.map(generator => generator.cleanup()),
      this.cache.clear()
    ])
  }
} 