from typing import Any, Dict, List


/**
 * Audio converter implementation using FFmpeg
 */
class AudioConverter extends BaseConverter {
  private readonly defaultAudioCodecs: Record<string, string> = {
    mp3: 'libmp3lame',
    wav: 'pcm_s16le',
    ogg: 'libvorbis',
    aac: 'aac',
    m4a: 'aac',
    opus: 'libopus'
  }
  private tempDir: str
  protected logger: Logger
  private retryHandler: RetryHandler
  constructor(
    tempDir: str = path.join(process.cwd(), 'temp'),
    retryConfig?: Partial<RetryConfig>
  ) {
    super()
    this.tempDir = tempDir
    this.logger = new Logger({ minLevel: LogLevel.INFO })
    this.retryHandler = new RetryHandler(retryConfig)
    this.supportedInputFormats = [
      'mp3', 'wav', 'aac', 'ogg', 'm4a', 'flac',
      'wma', 'aiff', 'opus', 'ac3', 'webm'
    ]
    this.supportedOutputFormats = [
      'mp3', 'wav', 'aac', 'ogg', 'm4a', 'flac',
      'opus'
    ]
  }
  /**
   * Convert audio from one format to another using FFmpeg
   */
  public async convert(
    input: str | Readable,
    output: str | Writable,
    config: ConverterConfig
  ): Promise<void> {
    if (!this.validateConfig(config)) {
      throw new ValidationError('Invalid configuration')
    }
    const audioConfig = config as AudioConverterConfig
    let inputPath: str | undefined
    let outputPath: str | undefined
    let isTemporaryInput = false
    let isTemporaryOutput = false
    try {
      this.emitProgress({
        percent: 0,
        bytesProcessed: 0,
        timeElapsed: 0,
        stage: ConversionStage.INITIALIZING,
        details: Dict[str, Any]
      })
      await fsPromises.mkdir(this.tempDir, { recursive: true })
      if (typeof input === 'string') {
        await fsPromises.access(input).catch(() => {
          throw new ValidationError(`Input file not accessible: ${input}`)
        })
        inputPath = input
      } else {
        inputPath = path.join(this.tempDir, `input-${uuidv4()}`)
        isTemporaryInput = true
        await this.streamToFile(input, inputPath)
      }
      if (typeof output === 'string') {
        outputPath = output
      } else {
        outputPath = path.join(this.tempDir, `output-${uuidv4()}.${audioConfig.outputFormat}`)
        isTemporaryOutput = true
      }
      this.emitProgress({
        percent: 0,
        bytesProcessed: 0,
        timeElapsed: 0,
        stage: ConversionStage.VALIDATING,
        details: Dict[str, Any]
      })
      const metadata = await this.getMetadata(inputPath)
      const totalDuration = parseFloat(metadata.format?.duration || '0')
      await this.retryHandler.withRetry(
        async () => {
          await this.runFFmpeg(inputPath!, outputPath!, audioConfig, totalDuration)
        },
        {
          operationName: 'Audio conversion',
          cleanupFn: async () => {
            if (isTemporaryOutput && outputPath) {
              try {
                await fsPromises.unlink(outputPath)
              } catch (error) {
                if ((error as NodeJS.ErrnoException).code !== 'ENOENT') {
                  this.logger.warn('Error cleaning up temporary output file', { error })
                }
              }
            }
          },
          onRetry: async (error, attempt) => {
            this.emitProgress({
              percent: 0,
              timeElapsed: 0,
              bytesProcessed: 0,
              stage: ConversionStage.RETRYING,
              details: Dict[str, Any]
            })
          }
        }
      )
      this.emitProgress({
        percent: 100,
        bytesProcessed: metadata.format?.size || 0,
        totalBytes: metadata.format?.size || 0,
        timeElapsed: totalDuration,
        stage: ConversionStage.FINALIZING,
        details: Dict[str, Any]
      })
      if (isTemporaryOutput && outputPath) {
        const outputStream = output as Writable
        await this.fileToStream(outputPath, outputStream)
      }
      this.emitComplete()
    } catch (error) {
      const conversionError = new ConversionError(
        'Audio conversion failed',
        'CONVERSION_ERROR',
        {
          originalError: error,
          inputFormat: audioConfig.inputFormat,
          outputFormat: audioConfig.outputFormat,
          details: error instanceof Error ? error.message : String(error)
        }
      )
      this.logger.error('Conversion failed', { error: conversionError })
      throw conversionError
    } finally {
      this.emitProgress({
        percent: 100,
        bytesProcessed: 0,
        timeElapsed: 0,
        stage: ConversionStage.CLEANING_UP
      })
      try {
        if (isTemporaryInput && inputPath) {
          await fsPromises.unlink(inputPath)
        }
        if (isTemporaryOutput && outputPath) {
          await fsPromises.unlink(outputPath)
        }
      } catch (cleanupError) {
        this.logger.warn('Error cleaning up temporary files', {
          error: cleanupError
        })
      }
    }
  }
  /**
   * Run FFmpeg command with the specified configuration
   */
  private async runFFmpeg(
    inputPath: str,
    outputPath: str,
    config: AudioConverterConfig,
    totalDuration: float
  ): Promise<void> {
    return new Promise<void>((resolve, reject) => {
      const args = this.buildFFmpegArgs(config, inputPath, outputPath)
      const ffmpeg = spawn('ffmpeg', args)
      let lastProgress = 0
      ffmpeg.stderr.on('data', (data: Buffer) => {
        const output = data.toString()
        const timeMatch = output.match(/time=(\d+:\d+:\d+.\d+)/)
        if (timeMatch) {
          const time = this.timeToSeconds(timeMatch[1])
          const percent = Math.min(Math.round((time / totalDuration) * 100), 100)
          if (percent > lastProgress + 1 || percent === 100) {
            lastProgress = percent
            this.emitProgress({
              percent,
              bytesProcessed: Math.floor((percent / 100) * fs.statSync(inputPath).size),
              totalBytes: fs.statSync(inputPath).size,
              timeElapsed: time,
              timeRemaining: totalDuration - time,
              stage: ConversionStage.CONVERTING,
              details: Dict[str, Any]
            })
          }
        }
      })
      ffmpeg.on('error', (error: Error) => {
        reject(new ProcessError('FFmpeg process error', {
          command: 'ffmpeg',
          args,
          error: error.message
        }))
      })
      ffmpeg.on('exit', (code: float) => {
        if (code === 0) {
          resolve()
        } else {
          reject(new ProcessError('FFmpeg process failed', {
            command: 'ffmpeg',
            args,
            exitCode: code
          }))
        }
      })
    })
  }
  /**
   * Build FFmpeg command arguments based on configuration
   */
  private buildFFmpegArgs(config: AudioConverterConfig, inputPath: str, outputPath: str): string[] {
    const args: List[string] = [
      '-i', inputPath,
      '-y'  
    ]
    const format = config.outputFormat.toLowerCase()
    const codec = config.codec || this.defaultAudioCodecs[format]
    if (codec) {
      args.push('-c:a', codec)
    }
    if (config.channels) {
      args.push('-ac', config.channels.toString())
    }
    if (config.sampleRate) {
      args.push('-ar', config.sampleRate.toString())
    }
    if (config.bitrate) {
      args.push('-b:a', config.bitrate)
    }
    if (config.normalize) {
      args.push('-filter:a', 'loudnorm')
    }
    if (config.quality !== undefined) {
      const formatQuality = this.getFormatSpecificQuality(format, config.quality)
      if (formatQuality.flag && formatQuality.value !== null) {
        args.push(formatQuality.flag, formatQuality.value.toString())
      }
    }
    args.push(outputPath)
    return args
  }
  /**
   * Get format-specific quality settings
   */
  private getFormatSpecificQuality(format: str, quality: float): {
    flag: str
    value: float | null
  } {
    switch (format.toLowerCase()) {
      case 'mp3':
        return {
          flag: '-q:a',
          value: Math.round(9 - (quality / 100) * 9)
        }
      case 'ogg':
        return {
          flag: '-q:a',
          value: Math.round((quality / 100) * 10)
        }
      default:
        return {
          flag: '',
          value: null
        }
    }
  }
  /**
   * Convert time string (HH:MM:SS.ms) to seconds
   */
  private timeToSeconds(time: str): float {
    const parts = time.split(':').map(parseFloat)
    return parts[0] * 3600 + parts[1] * 60 + parts[2]
  }
  /**
   * Convert seconds to timestamp string
   */
  private secondsToTimestamp(seconds: float): str {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = Math.floor(seconds % 60)
    const ms = Math.floor((seconds % 1) * 100)
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}.${ms.toString().padStart(2, '0')}`
  }
  /**
   * Get audio metadata using FFprobe
   */
  private async getMetadata(filePath: str): Promise<any> {
    return new Promise((resolve, reject) => {
      const ffprobe = spawn('ffprobe', [
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        '-show_streams',
        filePath
      ])
      let output = ''
      ffprobe.stdout.on('data', (data) => {
        output += data
      })
      ffprobe.on('close', (code) => {
        if (code === 0) {
          try {
            resolve(JSON.parse(output))
          } catch (error) {
            reject(new ProcessError('Failed to parse FFprobe output', {
              command: 'ffprobe',
              output
            }))
          }
        } else {
          reject(new ProcessError('FFprobe process failed', {
            command: 'ffprobe',
            exitCode: code
          }))
        }
      })
      ffprobe.on('error', (err) => {
        reject(new ProcessError('FFprobe process error', {
          command: 'ffprobe',
          error: err
        }))
      })
    })
  }
  /**
   * Stream to file utility
   */
  private async streamToFile(stream: Readable, filePath: str): Promise<void> {
    return new Promise((resolve, reject) => {
      const writeStream = fs.createWriteStream(filePath)
      stream.pipe(writeStream)
      writeStream.on('finish', resolve)
      writeStream.on('error', reject)
      stream.on('error', reject)
    })
  }
  /**
   * File to stream utility
   */
  private async fileToStream(filePath: str, outputStream: Writable): Promise<void> {
    return new Promise((resolve, reject) => {
      const readStream = fs.createReadStream(filePath)
      readStream.pipe(outputStream)
      outputStream.on('finish', resolve)
      outputStream.on('error', reject)
      readStream.on('error', reject)
    })
  }
  /**
   * Override validateConfig to add audio-specific validation
   */
  public validateConfig(config: ConverterConfig): bool {
    if (!super.validateConfig(config)) {
      return false
    }
    const audioConfig = config as AudioConverterConfig
    if (audioConfig.channels !== undefined &&
        (!Number.isInteger(audioConfig.channels) ||
         audioConfig.channels < 1 ||
         audioConfig.channels > 8)) {
      return false
    }
    if (audioConfig.sampleRate !== undefined &&
        (!Number.isInteger(audioConfig.sampleRate) ||
         audioConfig.sampleRate < 8000 ||
         audioConfig.sampleRate > 192000 ||
         ![8000, 11025, 22050, 44100, 48000, 96000, 192000].includes(audioConfig.sampleRate))) {
      return false
    }
    if (audioConfig.bitrate && !this.isValidBitrate(audioConfig.bitrate)) {
      return false
    }
    if (audioConfig.quality !== undefined &&
        (typeof audioConfig.quality !== 'number' ||
         audioConfig.quality < 0 ||
         audioConfig.quality > 100)) {
      return false
    }
    return true
  }
  /**
   * Validate bitrate format (e.g., '320k', '128k')
   */
  private isValidBitrate(bitrate: str): bool {
    return /^\d+[kM]$/i.test(bitrate)
  }
} 