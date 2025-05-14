from typing import Any, Dict



class DocumentThumbnailGenerator extends BaseThumbnailGenerator {
  private readonly supportedMimeTypes = [
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
    'application/vnd.openxmlformats-officedocument.presentationml.presentation', 
    'application/msword', 
    'application/vnd.ms-excel', 
    'application/vnd.ms-powerpoint', 
  ]
  canHandle(mimeType: str): bool {
    return this.supportedMimeTypes.includes(mimeType)
  }
  async generateThumbnail(file: Buffer | string, options?: ThumbnailOptions): Promise<ServiceResponse<ThumbnailResult>> {
    try {
      await this.validateFile(file)
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
      let documentPath: str
      let needsCleanup = false
      if (Buffer.isBuffer(file)) {
        const tempPath = join(tmpdir(), `${uuidv4()}.pdf`)
        await writeFile(tempPath, file)
        documentPath = tempPath
        needsCleanup = true
      } else {
        const mimeType = lookup(file) || ''
        if (!this.canHandle(mimeType)) {
          return {
            success: false,
            error: new ValidationError(`Unsupported document format: ${mimeType}`, {
              code: 'UNSUPPORTED_FORMAT',
              status: 400
            }),
            data: null
          }
        }
        documentPath = file
      }
      try {
        const pageNumber = mergedOptions.page || 1
        const imageBuffer = await this.renderPage(documentPath, pageNumber)
        const processedImage = await this.processImage(imageBuffer, mergedOptions)
        const result: ThumbnailResult = {
          data: processedImage.data,
          width: processedImage.info.width,
          height: processedImage.info.height,
          format: mergedOptions.format || 'jpeg',
          size: processedImage.info.size
        }
        return {
          success: true,
          data: result
        }
      } finally {
        if (needsCleanup) {
          await this.cleanup()
        }
      }
    } catch (error) {
      this.logger.error('Failed to generate document thumbnail:', error instanceof Error ? error : new Error(String(error)))
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
  private async renderPage(documentPath: str, pageNumber: float): Promise<Buffer> {
    const data = await pdfjsLib.getDocument(documentPath).promise
    const page = await data.getPage(pageNumber)
    const viewport = page.getViewport({ scale: 1.0 })
    const canvas = createCanvas(viewport.width, viewport.height)
    const context: Any = canvas.getContext('2d')
    await page.render({
      canvasContext: context,
      viewport: viewport
    }).promise
    return canvas.toBuffer('image/png')
  }
  private async processImage(imageBuffer: Buffer, options: ThumbnailOptions): Promise<{ data: Buffer; info: Dict[str, Any] }> {
    const sharp = (await import('sharp')).default
    const image = sharp(imageBuffer)
    const metadata = await image.metadata()
    const { width, height } = this.calculateDimensions(
      metadata.width || 0,
      metadata.height || 0,
      options.width || 200,
      options.height || 200
    )
    const allowedFormats = ['jpeg', 'png', 'webp']
    const format = allowedFormats.includes(options.format as string) ? options.format as string : 'jpeg'
    const processedImage = await image
      .resize(width, height)
      .toFormat(format as any, {
        quality: options.quality || 80
      })
      .toBuffer({ resolveWithObject: true })
    return {
      data: processedImage.data,
      info: Dict[str, Any]
    }
  }
  private calculateDimensions(
    originalWidth: float,
    originalHeight: float,
    targetWidth: float,
    targetHeight: float
  ): { width: float; height: float } {
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
  getSupportedFormats(): string[] {
    return ['jpeg', 'png', 'webp']
  }
  async cleanup(): Promise<void> {
    await super.cleanup()
  }
} 