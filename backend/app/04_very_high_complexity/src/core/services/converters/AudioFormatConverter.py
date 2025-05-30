from typing import Any, Dict



  ConversionOptions, 
  ConversionResult, 
  ConversionProgress,
  StreamConversionResult
} from './FormatConverter'
class FFmpegProgress:
    frames: float
    currentFps: float
    currentKbps: float
    targetSize: float
    timemark: str
    percent: float
class AudioFormatConverter extends BaseFormatConverter {
  private readonly supportedInputFormats = [
    'audio/mpeg',
    'audio/mp3',
    'audio/wav',
    'audio/x-wav',
    'audio/ogg',
    'audio/flac',
    'audio/aac',
    'audio/x-m4a',
    'audio/webm'
  ]
  private readonly supportedOutputFormats = [
    'mp3',
    'wav',
    'ogg',
    'flac',
    'aac',
    'm4a'
  ]
  private tempDir: str
  private defaultAudioCodecs: Record<string, string> = {
    mp3: 'libmp3lame',
    wav: 'pcm_s16le',
    ogg: 'libvorbis',
    flac: 'flac',
    aac: 'aac',
    m4a: 'aac'
  }
  constructor(tempDir: str = path.join(process.cwd(), 'temp')) {
    super()
    this.tempDir = tempDir
    Object.assign(this.defaultOptions, {
      targetFormat: 'mp3',
      bitrate: '128k',
      channels: 2,
      sampleRate: 44100,
      quality: 4 
    })
  }
  private handleError(error: unknown): ServiceResponse<ConversionResult> {
    const errorMessage = error instanceof Error ? error.message : String(error)
    this.logger.error('Audio conversion error:', { error: errorMessage })
    const serviceError: ServiceError = {
      code: 'AUDIO_CONVERSION_ERROR',
      message: errorMessage,
      status: 500
    }
    return {
      success: false,
      error: serviceError,
      data: null
    }
  }
  private mergeWithDefaultOptions(options?: ConversionOptions): ConversionOptions {
    return {
      ...this.defaultOptions,
      ...options
    }
  }
  private emitProgress(progress: ConversionProgress): void {
    this.emit('progress', progress)
  }
  protected async validateInput(input: Buffer | string): Promise<void> {
    try {
      if (Buffer.isBuffer(input)) {
        const mimeType = lookup(Buffer.from(input).toString('hex', 0, 8)) || 'application/octet-stream'
        if (!this.canConvertFrom(mimeType)) {
          throw new Error(`Unsupported input format: ${mimeType}`)
        }
      } else {
        await fs.access(input)
        const mimeType = lookup(input)
        if (!mimeType || !this.canConvertFrom(mimeType)) {
          throw new Error(`Unsupported input format: ${mimeType || 'unknown'}`)
        }
      }
    } catch (error) {
      this.logger.error('Input validation failed:', error)
      throw error
    }
  }
  protected async validateOptions(options?: ConversionOptions): Promise<ConversionOptions> {
    const mergedOptions = this.mergeWithDefaultOptions(options)
    if (!mergedOptions.targetFormat || !this.canConvertTo(mergedOptions.targetFormat)) {
      throw new Error(`Unsupported target format: ${mergedOptions.targetFormat}`)
    }
    if (mergedOptions.bitrate && !/^\d+[kKmM]$/.test(mergedOptions.bitrate)) {
      throw new Error('Invalid bitrate format. Use format like "128k", "320k", etc.')
    }
    if (mergedOptions.channels && (mergedOptions.channels < 1 || mergedOptions.channels > 8)) {
      throw new Error('Channels must be between 1 and 8')
    }
    if (mergedOptions.sampleRate && ![8000, 11025, 22050, 44100, 48000, 96000].includes(mergedOptions.sampleRate)) {
      throw new Error('Invalid sample rate. Use standard values: 8000, 11025, 22050, 44100, 48000, or 96000')
    }
    if (mergedOptions.quality !== undefined) {
      const format = mergedOptions.targetFormat.toLowerCase()
      if (['mp3', 'ogg'].includes(format)) {
        if (mergedOptions.quality < 0 || mergedOptions.quality > 9) {
          throw new Error('Quality (VBR) must be between 0 and 9 (lower is better)')
        }
      }
    }
    return mergedOptions
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
      const metadata = await this.getAudioMetadata(tempInputPath)
      const totalDuration = parseFloat(metadata.format?.duration?.toString() || '0')
      const format = options.targetFormat.toLowerCase()
      let command = ffmpeg(tempInputPath)
      command = command.audioCodec(options.audioCodec || this.defaultAudioCodecs[format])
      if (options.bitrate) {
        command = command.audioBitrate(options.bitrate)
      }
      if (options.channels) {
        command = command.audioChannels(options.channels)
      }
      if (options.sampleRate) {
        command = command.audioFrequency(options.sampleRate)
      }
      if (options.quality !== undefined && ['mp3', 'ogg'].includes(format)) {
        if (format === 'mp3') {
          command = command.addOption('-qscale:a', options.quality.toString())
        } else if (format === 'ogg') {
          command = command.addOption('-q:a', options.quality.toString())
        }
      }
      let processedBytes = 0
      await new Promise<void>((resolve, reject) => {
        const ffmpegCommand = command.output(tempOutputPath!)
        ffmpegCommand.on('error', (err: Error) => reject(err))
        ffmpegCommand.on('end', () => resolve())
        (ffmpegCommand as any).on('progress', (progress: FFmpegProgress) => {
          processedBytes = Math.floor((progress.percent || 0) * (metadata.format?.size || 0) / 100)
          onProgress(processedBytes)
        })
        ffmpegCommand.run()
      })
      const readStream = createReadStream(tempOutputPath!, {
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
      const outputMetadata = await this.getAudioMetadata(tempOutputPath)
      const endTime = Date.now()
      const conversionTime = endTime - startTime
      this.updateStats(true, inputStream, outputStream, conversionTime)
      return {
        success: true,
        data: Dict[str, Any],
          originalFormat: metadata.format?.format_name || 'unknown',
          conversionTime
        }
      }
    } catch (error) {
      this.logger.error('Stream processing failed:', error)
      const serviceError: ServiceError = {
        code: 'STREAM_PROCESSING_ERROR',
        message: error instanceof Error ? error.message : String(error),
        status: 500
      }
      return {
        success: false,
        error: serviceError,
        data: null
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
  async convert(input: Buffer | string, options?: ConversionOptions): Promise<ServiceResponse<ConversionResult>> {
    let inputPath: str | undefined
    let outputPath: str | undefined
    const startTime = Date.now()
    try {
      await this.validateInput(input)
      const validatedOptions = await this.validateOptions(options)
      await fs.mkdir(this.tempDir, { recursive: true })
      if (Buffer.isBuffer(input)) {
        inputPath = path.join(this.tempDir, `input-${uuidv4()}`)
        await fs.writeFile(inputPath, input)
      } else {
        inputPath = input
      }
      if (!inputPath) {
        return this.handleError('Failed to create input file')
      }
      outputPath = path.join(this.tempDir, `output-${uuidv4()}.${validatedOptions.targetFormat}`)
      const metadata = await this.getAudioMetadata(inputPath)
      const originalFormat = metadata.format?.format_name || 'unknown'
      const format = validatedOptions.targetFormat.toLowerCase()
      let command = ffmpeg(inputPath)
      try {
        command = command.audioCodec(validatedOptions.audioCodec || this.defaultAudioCodecs[format])
        if (validatedOptions.bitrate) {
          command = command.audioBitrate(validatedOptions.bitrate)
        }
        if (validatedOptions.channels) {
          command = command.audioChannels(validatedOptions.channels)
        }
        if (validatedOptions.sampleRate) {
          command = command.audioFrequency(validatedOptions.sampleRate)
        }
        if (validatedOptions.quality !== undefined && ['mp3', 'ogg'].includes(format)) {
          if (format === 'mp3') {
            command = command.addOption('-qscale:a', validatedOptions.quality.toString())
          } else if (format === 'ogg') {
            command = command.addOption('-q:a', validatedOptions.quality.toString())
          }
        }
        (command as any).on('progress', (progress: FFmpegProgress) => {
          const bytesProcessed = Math.floor((progress.percent || 0) * (metadata.format?.size || 0) / 100)
          this.emitProgress({
            bytesProcessed,
            totalBytes: metadata.format?.size || 0,
            percent: progress.percent || 0,
            stage: 'converting',
            timeElapsed: progress.timemark ? this.timemarkToSeconds(progress.timemark) : 0,
            timeRemaining: progress.targetSize ? (progress.targetSize - (progress.targetSize * (progress.percent || 0) / 100)) / 100 : undefined,
            currentFile: outputPath
          })
        })
        await new Promise<void>((resolve, reject) => {
          command
            .output(outputPath!)
            .on('end', () => resolve())
            .on('error', (err: Error) => reject(err))
            .run()
        })
        const outputBuffer = await fs.readFile(outputPath)
        const endTime = Date.now()
        const conversionTime = endTime - startTime
        const outputMetadata = await this.getAudioMetadata(outputPath)
        this.updateStats(true, input, outputBuffer, conversionTime)
        return {
          success: true,
          data: Dict[str, Any],
            originalFormat,
            conversionTime
          }
        }
      } catch (ffmpegError) {
        return this.handleError(`FFmpeg error: ${ffmpegError}`)
      }
    } catch (error) {
      return this.handleError(error)
    } finally {
      try {
        if (Buffer.isBuffer(input) && inputPath) {
          await fs.unlink(inputPath)
        }
        if (outputPath) {
          await fs.unlink(outputPath)
        }
      } catch (error) {
        this.logger.warn('Error cleaning up temp files:', error)
      }
    }
  }
  async cleanup(): Promise<void> {
    await super.cleanup()
    try {
      const files = await fs.readdir(this.tempDir)
      if (files.length === 0) {
        await fs.rmdir(this.tempDir)
      }
    } catch (error) {
      this.logger.warn('Error cleaning up temp directory:', error)
    }
  }
  private async getAudioMetadata(filePath: str): Promise<ffmpeg.FfprobeData> {
    return new Promise((resolve, reject) => {
      ffmpeg.ffprobe(filePath, (error: Error | null, metadata: ffmpeg.FfprobeData) => {
        if (error) reject(error)
        else resolve(metadata)
      })
    })
  }
  private timemarkToSeconds(timemark: str): float {
    const parts = timemark.split(':')
    return parseInt(parts[0]) * 3600 + parseInt(parts[1]) * 60 + parseFloat(parts[2])
  }
  public canConvertFrom(mimeType: str): bool {
    return this.supportedInputFormats.includes(mimeType.toLowerCase())
  }
  public canConvertTo(format: str): bool {
    return this.supportedOutputFormats.includes(format.toLowerCase())
  }
  public getSupportedInputFormats(): string[] {
    return [...this.supportedInputFormats]
  }
  public getSupportedOutputFormats(): string[] {
    return [...this.supportedOutputFormats]
  }
} 