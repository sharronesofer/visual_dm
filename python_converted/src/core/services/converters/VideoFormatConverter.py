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
class FFmpegFormatOptions:
    [key: str]: {
    videoCodec?: str
    audioCodec?: str
    videoBitrate?: str
    audioBitrate?: str
    preset?: str
}
class VideoFormatConverter extends BaseFormatConverter {
  private readonly supportedInputFormats = [
    'video/mp4',
    'video/webm',
    'video/x-matroska',
    'video/quicktime',
    'video/x-msvideo',
    'video/x-ms-wmv',
    'video/mpeg',
    'video/3gpp'
  ]
  private readonly supportedOutputFormats = [
    'mp4',
    'webm',
    'mkv',
    'mov',
    'avi'
  ]
  private tempDir: str
  private defaultVideoCodecs: Record<string, string> = {
    mp4: 'libx264',
    webm: 'libvpx-vp9',
    mkv: 'libx264',
    mov: 'libx264',
    avi: 'mpeg4'
  }
  private defaultAudioCodecs: Record<string, string> = {
    mp4: 'aac',
    webm: 'libvorbis',
    mkv: 'aac',
    mov: 'aac',
    avi: 'mp3'
  }
  private startTime: float
  private conversionStartTime: float
  private totalDuration: float
  constructor(tempDir: str = path.join(process.cwd(), 'temp')) {
    super()
    this.tempDir = tempDir
    this.startTime = Date.now()
    this.conversionStartTime = this.startTime
    this.totalDuration = 0
    Object.assign(this.defaultOptions, {
      targetFormat: 'mp4',
      quality: 23, 
      bitrate: '2M',
      audioBitrate: '128k',
      fps: 30,
      audioChannels: 2,
      sampleRate: 44100
    })
  }
  private handleError(error: unknown): ServiceResponse<ConversionResult> {
    const errorMessage = error instanceof Error ? error.message : String(error)
    this.logger.error('Video conversion error:', { error: errorMessage })
    const serviceError: ServiceError = {
      code: 'VIDEO_CONVERSION_ERROR',
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
    if (mergedOptions.fps && (mergedOptions.fps < 1 || mergedOptions.fps > 240)) {
      throw new Error('Frame rate must be between 1 and 240 fps')
    }
    if (mergedOptions.bitrate && !/^\d+[kKmM]$/.test(mergedOptions.bitrate)) {
      throw new Error('Invalid bitrate format. Use format like "2M", "800k", etc.')
    }
    if (mergedOptions.audioBitrate && !/^\d+[kKmM]$/.test(mergedOptions.audioBitrate)) {
      throw new Error('Invalid audio bitrate format. Use format like "128k", "320k", etc.')
    }
    if (mergedOptions.width && (mergedOptions.width < 1 || mergedOptions.width > 7680)) {
      throw new Error('Width must be between 1 and 7680 pixels')
    }
    if (mergedOptions.height && (mergedOptions.height < 1 || mergedOptions.height > 4320)) {
      throw new Error('Height must be between 1 and 4320 pixels')
    }
    if (mergedOptions.quality !== undefined) {
      const format = mergedOptions.targetFormat.toLowerCase()
      if (['mp4', 'mkv', 'mov'].includes(format)) {
        if (mergedOptions.quality < 0 || mergedOptions.quality > 51) {
          throw new Error('CRF quality must be between 0 and 51 (lower is better)')
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
      const metadata = await this.getVideoMetadata(tempInputPath)
      const totalDuration = parseFloat(metadata.format?.duration?.toString() || '0')
      const frameRate = options.fps || 
        (metadata.streams?.[0]?.r_frame_rate ? 
          parseFloat(metadata.streams[0].r_frame_rate.split('/')[0]) / 
          parseFloat(metadata.streams[0].r_frame_rate.split('/')[1]) : 
          30
        )
      const totalFrames = Math.ceil(totalDuration * frameRate)
      const format = options.targetFormat.toLowerCase()
      let command = ffmpeg(tempInputPath)
      command = command.videoCodec(options.videoCodec || this.defaultVideoCodecs[format])
      command = command.audioCodec(options.audioCodec || this.defaultAudioCodecs[format])
      if (options.bitrate) {
        command = command.videoBitrate(options.bitrate)
      }
      if (options.audioBitrate) {
        command = command.audioBitrate(options.audioBitrate)
      }
      if (options.fps) {
        command = command.fps(options.fps)
      }
      if (options.width || options.height) {
        command = command.size(`${options.width || '?'}x${options.height || '?'}`)
      }
      if (options.audioChannels) {
        command = command.audioChannels(options.audioChannels)
      }
      if (options.sampleRate) {
        command = command.audioFrequency(options.sampleRate)
      }
      if (options.quality && ['mp4', 'mkv', 'mov'].includes(format)) {
        command = command.addOption('-crf', options.quality.toString())
      }
      if (options.preset) {
        command = command.addOption('-preset', options.preset)
      }
      let processedBytes = 0
      await new Promise<void>((resolve, reject) => {
        const ffmpegCommand = command.output(tempOutputPath!)
        ffmpegCommand.on('error', (err: Error) => {
          this.logger.error('FFmpeg conversion error:', err)
          reject(new ServiceError('CONVERSION_ERROR', `FFmpeg conversion failed: ${err.message}`, { format, options }))
        })
        ffmpegCommand.on('end', () => resolve())
        (ffmpegCommand as any).on('progress', (progress: FFmpegProgress) => {
          processedBytes = Math.floor((progress.frames / totalFrames) * (metadata.format?.size || 0))
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
          if (!outputStream.write(buffer)) {
            readStream.pause()
            outputStream.once('drain', () => readStream.resume())
          }
        })
        readStream.on('end', () => {
          outputStream.end()
          resolve()
        })
        readStream.on('error', (err) => {
          this.logger.error('Stream read error:', err)
          reject(new ServiceError('STREAM_READ_ERROR', `Failed to read converted video: ${err.message}`))
        })
        outputStream.on('error', (err) => {
          this.logger.error('Stream write error:', err)
          reject(new ServiceError('STREAM_WRITE_ERROR', `Failed to write converted video: ${err.message}`))
        })
      })
      const outputMetadata = await this.getVideoMetadata(tempOutputPath)
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
      const metadata = await this.getVideoMetadata(inputPath)
      const originalFormat = metadata.format?.format_name || 'unknown'
      const totalDuration = parseFloat(metadata.format?.duration?.toString() || '0')
      const frameRate = validatedOptions.fps || 
        (metadata.streams?.[0]?.r_frame_rate ? 
          parseFloat(metadata.streams[0].r_frame_rate.split('/')[0]) / 
          parseFloat(metadata.streams[0].r_frame_rate.split('/')[1]) : 
          30
        )
      const totalFrames = Math.ceil(totalDuration * frameRate)
      const format = validatedOptions.targetFormat.toLowerCase()
      let command = ffmpeg(inputPath)
      try {
        command = command.videoCodec(validatedOptions.videoCodec || this.defaultVideoCodecs[format])
        command = command.audioCodec(validatedOptions.audioCodec || this.defaultAudioCodecs[format])
        if (validatedOptions.bitrate) {
          command = command.videoBitrate(validatedOptions.bitrate)
        }
        if (validatedOptions.audioBitrate) {
          command = command.audioBitrate(validatedOptions.audioBitrate)
        }
        if (validatedOptions.fps) {
          command = command.fps(validatedOptions.fps)
        }
        if (validatedOptions.width || validatedOptions.height) {
          command = command.size(`${validatedOptions.width || '?'}x${validatedOptions.height || '?'}`)
        }
        if (validatedOptions.audioChannels) {
          command = command.audioChannels(validatedOptions.audioChannels)
        }
        if (validatedOptions.sampleRate) {
          command = command.audioFrequency(validatedOptions.sampleRate)
        }
        if (validatedOptions.quality && ['mp4', 'mkv', 'mov'].includes(format)) {
          command = command.addOption('-crf', validatedOptions.quality.toString())
        }
        if (validatedOptions.preset) {
          command = command.addOption('-preset', validatedOptions.preset)
        }
        (command as any).on('progress', (progress: FFmpegProgress) => {
          const bytesProcessed = Math.floor((progress.frames / totalFrames) * (metadata.format?.size || 0))
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
        const outputMetadata = await this.getVideoMetadata(outputPath)
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
  private async getVideoMetadata(filePath: str): Promise<ffmpeg.FfprobeData> {
    return new Promise((resolve, reject) => {
      ffmpeg.ffprobe(filePath, (error: Error | null, metadata: ffmpeg.FfprobeData) => {
        if (error) reject(error)
        else resolve(metadata)
      })
    })
  }
  protected updateStats(
    success: bool,
    input: str | Buffer | Readable,
    output: Buffer | Writable | null,
    conversionTime: float
  ): void {
    this.stats.totalConversions++
    if (success) {
      this.stats.successCount++
    } else {
      this.stats.failureCount++
    }
    if (!(input instanceof Readable) && !(output instanceof Writable)) {
      this.stats.inputSize += Buffer.isBuffer(input) ? input.length : 0
      this.stats.outputSize += output && Buffer.isBuffer(output) ? output.length : 0
    }
    this.stats.conversionTime = conversionTime
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
        const formatOptions: \'FFmpegFormatOptions\' = {
          mp4: Dict[str, Any],
          webm: Dict[str, Any],
          mov: Dict[str, Any],
          mkv: Dict[str, Any],
        }
        const formatOption = formatOptions[format]
        this.conversionStartTime = Date.now()
        const command = ffmpeg(tempInputPath)
          .format(format)
          .videoCodec(options.videoCodec || formatOption.videoCodec)
          .audioCodec(options.audioCodec || formatOption.audioCodec)
          .videoBitrate(options.videoBitrate || this.defaultOptions.videoBitrate)
          .audioBitrate(options.audioBitrate || this.defaultOptions.audioBitrate)
        if (options.fps) {
          command.fps(options.fps)
        }
        if (options.width || options.height) {
          command.size(`${options.width || '?'}x${options.height || '?'}`)
        }
        if (formatOption.preset) {
          command.preset(formatOption.preset)
        }
        const metadata = await new Promise<ffmpeg.FfprobeData>((resolve, reject) => {
          ffmpeg.ffprobe(tempInputPath, (err, data) => {
            if (err) reject(err)
            else resolve(data)
          })
        })
        this.totalDuration = metadata.format.duration || 0
        command.on('progress', (progress) => {
          const bytesProcessed = Math.floor((progress.percent || 0) * metadata.format.size!)
          this.emit('progress', {
            bytesProcessed,
            totalBytes: metadata.format.size!,
          })
        })
        await new Promise<void>((resolve, reject) => {
          command
            .save(tempOutputPath)
            .on('end', resolve)
            .on('error', reject)
        })
        const conversionTime = Date.now() - this.conversionStartTime
        const outputMetadata = await new Promise<ffmpeg.FfprobeData>((resolve, reject) => {
          ffmpeg.ffprobe(tempOutputPath, (err, data) => {
            if (err) reject(err)
            else resolve(data)
          })
        })
        const outputFileStream = createReadStream(tempOutputPath)
        const chunkSize = Math.max(
          options.chunkSize || this.defaultOptions.chunkSize,
          1024 
        )
        let bytesProcessed = 0
        const totalBytes = outputMetadata.format.size!
        await new Promise<void>((resolve, reject) => {
          outputFileStream.on('data', (chunk: Buffer) => {
            bytesProcessed += chunk.length
            this.emit('progress', {
              bytesProcessed,
              totalBytes,
            })
            if (!outputStream.write(chunk)) {
              outputFileStream.pause()
              outputStream.once('drain', () => {
                outputFileStream.resume()
              })
            }
          })
          outputFileStream.on('end', resolve)
          outputFileStream.on('error', reject)
        })
        outputStream.end()
        const conversionMetadata: ConversionMetadata = {
          format,
          width: outputMetadata.streams[0]?.width || 0,
          height: outputMetadata.streams[0]?.height || 0,
          channels: outputMetadata.streams[1]?.channels || 0,
          bitrate: outputMetadata.format.bit_rate?.toString(),
          codec: outputMetadata.streams[0]?.codec_name,
          duration: outputMetadata.format.duration,
          size: totalBytes,
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
          'Failed to process video stream',
          { error }
        ),
        data: null,
      }
    }
  }
} 