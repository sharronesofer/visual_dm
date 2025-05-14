from typing import Any, Dict


class ImageThumbnailGenerator extends BaseThumbnailGenerator {
  private readonly supportedMimeTypes = [
    'image/jpeg',
    'image/png',
    'image/webp',
    'image/tiff',
    'image/gif'
  ]
  canHandle(mimeType: str): bool {
    return this.supportedMimeTypes.includes(mimeType)
  }
  getSupportedFormats(): string[] {
    return this.supportedMimeTypes
  }
  protected async validateFile(file: Buffer | string): Promise<boolean> {
    try {
      if (!file) {
        throw new ValidationError('No file provided', {
          code: 'MISSING_FILE',
          status: 400
        })
      }
      if (typeof file === 'string') {
        const mimeType = lookup(file)
        if (!mimeType || !this.canHandle(mimeType)) {
          throw new ValidationError(`Unsupported image format: ${mimeType}`, {
            code: 'UNSUPPORTED_FORMAT',
            status: 400
          })
        }
      } else if (!Buffer.isBuffer(file)) {
        throw new ValidationError('Invalid file format: must be a Buffer or file path', {
          code: 'INVALID_FILE',
          status: 400
        })
      }
      return true
    } catch (error) {
      if (error instanceof Error) {
        this.logger.error('File validation failed:', error)
      } else {
        this.logger.error('File validation failed with unknown error')
      }
      return false
    }
  }
  protected mergeWithDefaultOptions(options?: ThumbnailOptions): ThumbnailOptions {
    return {
      ...this.getDefaultOptions(),
      ...options
    }
  }
  async generateThumbnail(file: Buffer | string, options?: ThumbnailOptions): Promise<ServiceResponse<ThumbnailResult>> {
    try {
      if (!(await this.validateFile(file))) {
        return {
          success: false,
          error: new ValidationError('Invalid file', {
            code: 'INVALID_FILE',
            status: 400
          }),
          data: null
        }
      }
      const mergedOptions = this.mergeWithDefaultOptions(options)
      if (!(await this.validateOptions(mergedOptions))) {
        return {
          success: false,
          error: new ValidationError('Invalid thumbnail options', {
            code: 'INVALID_OPTIONS',
            status: 400
          }),
          data: null
        }
      }
      let imageBuffer: Buffer
      let originalFormat: str
      if (typeof file === 'string') {
        const mimeType = lookup(file) || ''
        if (!this.canHandle(mimeType)) {
          return {
            success: false,
            error: new ValidationError(`Unsupported image format: ${mimeType}`, {
              code: 'UNSUPPORTED_FORMAT',
              status: 400
            }),
            data: null
          }
        }
        imageBuffer = await sharp(file).toBuffer()
        originalFormat = mimeType.split('/')[1]
      } else {
        const metadata = await sharp(file).metadata()
        if (!metadata.format || !this.canHandle(`image/${metadata.format}`)) {
          return {
            success: false,
            error: new ValidationError('Unsupported image format', {
              code: 'UNSUPPORTED_FORMAT',
              status: 400
            }),
            data: null
          }
        }
        imageBuffer = file
        originalFormat = metadata.format
      }
      const sharpInstance = sharp(imageBuffer)
      const metadata = await sharpInstance.metadata()
      const { width, height } = this.calculateDimensions(
        metadata.width || 0,
        metadata.height || 0,
        mergedOptions.width || 200,
        mergedOptions.height || 200,
        mergedOptions.preserveAspectRatio
      )
      const processedImage = await sharpInstance
        .resize(width, height, {
          fit: mergedOptions.preserveAspectRatio ? 'inside' : 'fill'
        })
        .toFormat(mergedOptions.format || 'jpeg', {
          quality: mergedOptions.quality || 80
        })
        .toBuffer({ resolveWithObject: true })
      const result: ThumbnailResult = {
        data: processedImage.data,
        metadata: Dict[str, Any]
      }
      return {
        success: true,
        data: result
      }
    } catch (error) {
      if (error instanceof Error) {
        this.logger.error('Failed to generate image thumbnail:', error)
      } else {
        this.logger.error('Failed to generate image thumbnail with unknown error')
      }
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
  private calculateDimensions(
    originalWidth: float,
    originalHeight: float,
    targetWidth: float,
    targetHeight: float,
    preserveAspectRatio: bool = true
  ): { width: float; height: float } {
    if (!preserveAspectRatio) {
      return { width: targetWidth, height: targetHeight }
    }
    const aspectRatio = originalWidth / originalHeight
    let width = targetWidth
    let height = targetHeight
    if (targetWidth / targetHeight > aspectRatio) {
      width = Math.round(targetHeight * aspectRatio)
    } else {
      height = Math.round(targetWidth / aspectRatio)
    }
    return { width, height }
  }
} 