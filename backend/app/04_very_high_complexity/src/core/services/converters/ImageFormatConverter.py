from typing import Any, Dict
from enum import Enum



  ConversionOptions, 
  ConversionResult, 
  StreamConversionResult 
} from './FormatConverter'
class ImageConversionOptions:
    compressionLevel?: float
class ExtendedConversionOptions:
    compressionLevel?: float
class SharpFormatOptions:
    jpeg: sharp.JpegOptions
    png: sharp.PngOptions
    webp: sharp.WebpOptions
    avif: sharp.AvifOptions
    tiff: sharp.TiffOptions
class ImageFormatConverter extends BaseFormatConverter {
  private readonly supportedInputFormats = [
    'jpeg', 'jpg', 'png', 'webp', 'avif', 'tiff', 'gif'
  ]
  private readonly supportedOutputFormats = [
    'jpeg', 'jpg', 'png', 'webp', 'avif', 'tiff'
  ]
  private readonly tempDir: str
  protected readonly defaultOptions: \'ExtendedConversionOptions\'
  private startTime: float
  private conversionStartTime: float
  constructor(tempDir: str = path.join(process.cwd(), 'temp')) {
    super()
    this.tempDir = tempDir
    this.defaultOptions = {
      targetFormat: '',
      quality: 80,
      compressionLevel: 6,
      chunkSize: 64 * 1024, 
    }
    this.startTime = Date.now()
    this.conversionStartTime = this.startTime
  }
  canConvertFrom(mimeType: str): bool {
    return this.supportedInputFormats.includes(mimeType.toLowerCase())
  }
  canConvertTo(format: str): bool {
    return this.supportedOutputFormats.includes(format.toLowerCase())
  }
  getSupportedInputFormats(): string[] {
    return this.supportedInputFormats
  }
  getSupportedOutputFormats(): string[] {
    return this.supportedOutputFormats
  }
  protected async validateOptions(options?: ConversionOptions): Promise<ExtendedConversionOptions> {
    const mergedOptions = await super.validateOptions(options)
    return {
      ...mergedOptions,
      compressionLevel: (options as ExtendedConversionOptions)?.compressionLevel || this.defaultOptions.compressionLevel
    }
  }
  async convert(input: Buffer | string, options?: ConversionOptions): Promise<ServiceResponse<ConversionResult>> {
    try {
      await this.validateInput(input)
      const mergedOptions = await this.validateOptions(options)
      let inputBuffer: Buffer
      if (typeof input === 'string') {
        inputBuffer = await fs.readFile(input)
      } else {
        inputBuffer = input
      }
      const startTime = Date.now()
      let pipeline = sharp(inputBuffer)
      const metadata = await pipeline.metadata()
      const originalFormat = metadata.format || 'unknown'
      if (mergedOptions.width || mergedOptions.height) {
        pipeline = pipeline.resize({
          width: mergedOptions.width,
          height: mergedOptions.height,
          fit: 'inside',
          withoutEnlargement: true
        })
      }
      let formatOptions: Any = {}
      switch (mergedOptions.targetFormat.toLowerCase()) {
        case 'jpeg':
          formatOptions = {
            quality: mergedOptions.quality,
            mozjpeg: true
          }
          break
        case 'png':
          formatOptions = {
            compressionLevel: mergedOptions.compressionLevel,
            palette: true
          }
          break
        case 'webp':
          formatOptions = {
            quality: mergedOptions.quality,
            lossless: false
          }
          break
        case 'tiff':
          formatOptions = {
            quality: mergedOptions.quality,
            compression: 'jpeg'
          }
          break
        case 'avif':
          formatOptions = {
            quality: mergedOptions.quality,
            lossless: false,
            effort: 4
          }
          break
      }
      pipeline = pipeline.toFormat(mergedOptions.targetFormat as keyof sharp.FormatEnum, formatOptions)
      const outputBuffer = await pipeline.toBuffer({ resolveWithObject: true })
      const endTime = Date.now()
      this.updateStats(true, input, outputBuffer.data, endTime - startTime)
      return {
        success: true,
        data: Dict[str, Any],
          originalFormat,
          conversionTime: endTime - startTime
        }
      }
    } catch (error) {
      this.logger.error('Image conversion failed:', error)
      return {
        success: false,
        data: null,
        error: new ServiceError('IMAGE_CONVERSION_ERROR', error instanceof Error ? error.message : String(error))
      }
    }
  }
  async cleanup(): Promise<void> {
    await super.cleanup()
  }
  protected async processStream(
    inputStream: Readable,
    outputStream: Writable,
    options: ConversionOptions,
    onProgress: (bytesProcessed: float) => void
  ): Promise<ServiceResponse<StreamConversionResult>> {
    let tempInputPath: str | undefined
    let tempOutputPath: str | undefined
    const startTime = Date.now()
    try {
      await fs.mkdir(this.tempDir, { recursive: true })
      tempInputPath = path.join(this.tempDir, `stream-input-${uuidv4()}`)
      tempOutputPath = path.join(this.tempDir, `stream-output-${uuidv4()}.${options.targetFormat}`)
      const writeStream = createWriteStream(tempInputPath)
      let bytesWritten = 0
      await new Promise<void>((resolve, reject) => {
        inputStream.on('data', (chunk: Buffer | string) => {
          const buffer = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk)
          bytesWritten += buffer.length
          onProgress(bytesWritten)
          writeStream.write(buffer)
        })
        inputStream.on('end', () => {
          writeStream.end()
          resolve()
        })
        inputStream.on('error', reject)
        writeStream.on('error', reject)
      })
      let pipeline = sharp(tempInputPath)
      const metadata = await pipeline.metadata()
      const originalFormat = metadata.format || 'unknown'
      if (options.width || options.height) {
        pipeline = pipeline.resize({
          width: options.width,
          height: options.height,
          fit: 'inside',
          withoutEnlargement: true
        })
      }
      let formatOptions: Any = {}
      const imageOptions = await this.validateOptions(options)
      switch (options.targetFormat.toLowerCase()) {
        case 'jpeg':
          formatOptions = {
            quality: options.quality,
            mozjpeg: true
          }
          break
        case 'png':
          formatOptions = {
            compressionLevel: imageOptions.compressionLevel,
            palette: true
          }
          break
        case 'webp':
          formatOptions = {
            quality: options.quality,
            lossless: false
          }
          break
        case 'tiff':
          formatOptions = {
            quality: options.quality,
            compression: 'jpeg'
          }
          break
        case 'avif':
          formatOptions = {
            quality: options.quality,
            lossless: false,
            effort: 4
          }
          break
      }
      pipeline = pipeline.toFormat(options.targetFormat as keyof sharp.FormatEnum, formatOptions)
      await pipeline.toFile(tempOutputPath)
      const readStream = createReadStream(tempOutputPath, {
        highWaterMark: options.chunkSize || this.defaultOptions.chunkSize
      })
      await new Promise<void>((resolve, reject) => {
        readStream.on('data', (chunk: Buffer | string) => {
          const buffer = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk)
          outputStream.write(buffer)
        })
        readStream.on('end', () => {
          outputStream.end()
          resolve()
        })
        readStream.on('error', reject)
        outputStream.on('error', reject)
      })
      const outputMetadata = await sharp(tempOutputPath).metadata()
      const stats = await fs.stat(tempOutputPath)
      const endTime = Date.now()
      const conversionTime = endTime - startTime
      this.updateStats(true, inputStream, outputStream, conversionTime)
      return {
        success: true,
        data: Dict[str, Any],
          originalFormat,
          conversionTime
        }
      }
    } catch (error) {
      this.logger.error('Stream processing failed:', error)
      return {
        success: false,
        data: null,
        error: new ServiceError('STREAM_PROCESSING_ERROR', error instanceof Error ? error.message : String(error))
      }
    } finally {
      try {
        if (tempInputPath) {
          await fs.unlink(tempInputPath)
        }
        if (tempOutputPath) {
          await fs.unlink(tempOutputPath)
        }
      } catch (cleanupError) {
        this.logger.warn('Error cleaning up temporary files:', cleanupError)
      }
    }
  }
  public async convertStream(
    inputStream: Readable,
    outputStream: Writable,
    options: ConversionOptions
  ): Promise<ServiceResponse<StreamProcessingResult>> {
    try {
      this.startTime = Date.now()
      const format = options.targetFormat.toLowerCase()
      if (!this.supportedOutputFormats.includes(format)) {
        throw new ServiceError(
          'UnsupportedFormat',
          `Unsupported output format: ${format}`,
          { supportedFormats: this.supportedOutputFormats }
        )
      }
      const tempDir = options.tempDir || os.tmpdir()
      const tempInputPath = path.join(tempDir, `input-${Date.now()}.tmp`)
      const tempOutputPath = path.join(tempDir, `output-${Date.now()}.${format}`)
      try {
        const writeStream = createWriteStream(tempInputPath)
        await new Promise<void>((resolve, reject) => {
          inputStream.pipe(writeStream)
            .on('finish', resolve)
            .on('error', reject)
        })
        const sharpInstance = sharp(tempInputPath)
        const formatOptions: Partial<SharpFormatOptions> = {
          jpeg: Dict[str, Any],
          png: Dict[str, Any],
          webp: Dict[str, Any],
          avif: Dict[str, Any],
          tiff: Dict[str, Any],
        }
        const formatKey = format === 'jpg' ? 'jpeg' : format
        const formatOption = formatOptions[formatKey as keyof SharpFormatOptions]
        if (formatOption) {
          sharpInstance.toFormat(formatKey as keyof sharp.FormatEnum, formatOption)
        } else {
          sharpInstance.toFormat(formatKey as keyof sharp.FormatEnum)
        }
        if (options.width || options.height) {
          sharpInstance.resize(options.width, options.height, {
            fit: 'inside',
            withoutEnlargement: true,
          })
        }
        this.conversionStartTime = Date.now()
        const metadata = await sharpInstance.metadata()
        const outputBuffer = await sharpInstance.toBuffer()
        const conversionTime = Date.now() - this.conversionStartTime
        const chunkSize = Math.max(
          options.chunkSize || this.defaultOptions.chunkSize,
          1024 
        )
        let bytesProcessed = 0
        for (let i = 0; i < outputBuffer.length; i += chunkSize) {
          const chunk = outputBuffer.slice(i, Math.min(i + chunkSize, outputBuffer.length))
          bytesProcessed += chunk.length
          this.emit('progress', {
            bytesProcessed,
            totalBytes: outputBuffer.length,
          })
          if (!outputStream.write(chunk)) {
            await new Promise(resolve => outputStream.once('drain', resolve))
          }
        }
        outputStream.end()
        const conversionMetadata: ConversionMetadata = {
          format: metadata.format || format,
          width: metadata.width || 0,
          height: metadata.height || 0,
          channels: metadata.channels || 0,
          size: outputBuffer.length,
          codec: metadata.compression || undefined,
          bitrate: undefined,
          duration: undefined,
        }
        return {
          success: true,
          data: Dict[str, Any],
        }
      } finally {
        await fs.unlink(tempInputPath).catch(() => {})
        if (await fs.access(tempOutputPath).then(() => true, () => false)) {
          await fs.unlink(tempOutputPath).catch(() => {})
        }
      }
    } catch (error) {
      return {
        success: false,
        error: error instanceof ServiceError ? error : new ServiceError(
          'ProcessingError',
          'Failed to process image stream',
          { error }
        ),
        data: null,
      }
    }
  }
} 