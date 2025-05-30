from typing import Any, Dict, List



class VideoConverter extends BaseFormatConverter {
  private readonly inputFormats = ['mp4', 'avi', 'mov', 'mkv', 'webm', 'flv']
  private readonly outputFormats = ['mp4', 'webm', 'mov']
  private readonly defaultOptions: ConversionOptions = {
    targetFormat: 'mp4',
    quality: 80, 
    compressionLevel: 6, 
    chunkSize: 1024 * 1024, 
    preserveMetadata: false,
    preserveAspectRatio: true
  }
  private readonly presetMap: Dict[str, Any] = {
    0: 'ultrafast',
    1: 'superfast',
    2: 'veryfast',
    3: 'faster',
    4: 'fast',
    5: 'medium',
    6: 'slow',
    7: 'slower',
    8: 'veryslow',
    9: 'placebo'
  }
  public getSupportedInputFormats(): string[] {
    return [...this.inputFormats]
  }
  public getSupportedOutputFormats(): string[] {
    return [...this.outputFormats]
  }
  public canConvertTo(format: str): bool {
    return this.outputFormats.includes(format.toLowerCase())
  }
  private async validateInput(input: Buffer | string): Promise<void> {
    if (typeof input === 'string') {
      try {
        await fs.access(input)
      } catch {
        throw new ServiceError('InvalidInput', 'Input file does not exist', { input })
      }
    } else if (!Buffer.isBuffer(input)) {
      throw new ServiceError('InvalidInput', 'Input must be a Buffer or file path', { input })
    }
  }
  private async validateOptions(options: ConversionOptions): Promise<ConversionOptions> {
    const mergedOptions = { ...this.defaultOptions, ...options }
    if (!mergedOptions.targetFormat) {
      throw new ServiceError('InvalidOptions', 'Target format is required')
    }
    if (!this.canConvertTo(mergedOptions.targetFormat)) {
      throw new ServiceError(
        'UnsupportedFormat',
        `Unsupported output format: ${mergedOptions.targetFormat}`,
        { supportedFormats: this.outputFormats }
      )
    }
    return mergedOptions
  }
  private getVideoCodec(format: str): str {
    switch (format.toLowerCase()) {
      case 'mp4':
        return 'libx264'
      case 'webm':
        return 'libvpx-vp9'
      case 'mov':
        return 'libx264'
      default:
        return 'libx264'
    }
  }
  private getAudioCodec(format: str): str {
    switch (format.toLowerCase()) {
      case 'mp4':
        return 'aac'
      case 'webm':
        return 'libopus'
      case 'mov':
        return 'aac'
      default:
        return 'aac'
    }
  }
  private async getVideoMetadata(input: str): Promise<ffmpeg.FfprobeData> {
    return new Promise((resolve, reject) => {
      ffmpeg.ffprobe(input, (err, metadata) => {
        if (err) reject(err)
        else resolve(metadata)
      })
    })
  }
  public async convert(
    input: Buffer | string,
    options: ConversionOptions
  ): Promise<ServiceResponse<ConversionResult>> {
    let tempInputPath: str | undefined
    try {
      await this.validateInput(input)
      const mergedOptions = await this.validateOptions(options)
      if (Buffer.isBuffer(input)) {
        const tempDir = mergedOptions.tempDir || os.tmpdir()
        tempInputPath = path.join(tempDir, `input-${uuidv4()}`)
        await fs.writeFile(tempInputPath, input)
      }
      const inputPath = tempInputPath || (input as string)
      const metadata = await this.getVideoMetadata(inputPath)
      const originalFormat = path.extname(inputPath).slice(1) || 'unknown'
      const chunks: List[Buffer] = []
      const outputStream = new Writable({
        write(chunk: Buffer, encoding, callback) {
          chunks.push(chunk)
          callback()
        }
      })
      const command = ffmpeg(inputPath)
        .videoCodec(this.getVideoCodec(mergedOptions.targetFormat))
        .audioCodec(this.getAudioCodec(mergedOptions.targetFormat))
        .format(mergedOptions.targetFormat)
      if (mergedOptions.width || mergedOptions.height) {
        command.size(`${mergedOptions.width || '?'}x${mergedOptions.height || '?'}`)
      }
      const crf = Math.round(51 - ((mergedOptions.quality || 80) / 100 * 51))
      command.addOption('-crf', crf.toString())
      const preset = this.presetMap[mergedOptions.compressionLevel || 6] || 'medium'
      command.addOption('-preset', preset)
      if (mergedOptions.preserveAspectRatio) {
        command.addOption('-aspect', 'a')
      }
      await new Promise<void>((resolve, reject) => {
        command
          .on('error', (err) => reject(err))
          .on('end', () => resolve())
          .pipe(outputStream, { end: true })
      })
      const data = Buffer.concat(chunks)
      const videoStream = metadata.streams.find(s => s.codec_type === 'video')
      const result: ConversionResult = {
        data,
        format: mergedOptions.targetFormat,
        size: data.length,
        width: videoStream?.width || 0,
        height: videoStream?.height || 0
      }
      return {
        success: true,
        data: result
      }
    } catch (error) {
      return {
        success: false,
        error: error instanceof ServiceError ? error : new ServiceError(
          'ConversionError',
          'Failed to convert video',
          { error }
        ),
        data: null
      }
    } finally {
      if (tempInputPath) {
        await fs.unlink(tempInputPath).catch(() => {})
      }
    }
  }
  public async convertStream(
    inputStream: Readable,
    outputStream: Writable,
    options: ConversionOptions
  ): Promise<ServiceResponse<StreamProcessingResult>> {
    let tempInputPath: str | undefined
    let tempOutputPath: str | undefined
    const startTime = Date.now()
    try {
      const mergedOptions = await this.validateOptions(options)
      const tempDir = mergedOptions.tempDir || os.tmpdir()
      tempInputPath = path.join(tempDir, `input-${uuidv4()}`)
      tempOutputPath = path.join(tempDir, `output-${uuidv4()}.${mergedOptions.targetFormat}`)
      const writeStream = fs_sync.createWriteStream(tempInputPath)
      let bytesProcessed = 0
      await new Promise<void>((resolve, reject) => {
        inputStream.on('data', (chunk: Buffer) => {
          bytesProcessed += chunk.length
          writeStream.write(chunk)
          this.emit('progress', { bytesProcessed })
        })
        inputStream.on('end', () => {
          writeStream.end()
          resolve()
        })
        inputStream.on('error', reject)
        writeStream.on('error', reject)
      })
      const metadata = await this.getVideoMetadata(tempInputPath)
      const originalFormat = metadata.format?.format_name?.split(',')[0] || 'unknown'
      const command = ffmpeg(tempInputPath)
        .videoCodec(this.getVideoCodec(mergedOptions.targetFormat))
        .audioCodec(this.getAudioCodec(mergedOptions.targetFormat))
        .format(mergedOptions.targetFormat)
      if (mergedOptions.width || mergedOptions.height) {
        command.size(`${mergedOptions.width || '?'}x${mergedOptions.height || '?'}`)
      }
      const crf = Math.round(51 - ((mergedOptions.quality || 80) / 100 * 51))
      command.addOption('-crf', crf.toString())
      const preset = this.presetMap[mergedOptions.compressionLevel || 6] || 'medium'
      command.addOption('-preset', preset)
      if (mergedOptions.preserveAspectRatio) {
        command.addOption('-aspect', 'a')
      }
      await new Promise<void>((resolve, reject) => {
        command
          .on('error', (err) => reject(err))
          .on('end', () => resolve())
          .save(tempOutputPath!)
      })
      const readStream = fs_sync.createReadStream(tempOutputPath!, {
        highWaterMark: mergedOptions.chunkSize
      })
      let totalBytes = 0
      await new Promise<void>((resolve, reject) => {
        readStream.on('data', (chunk: str | Buffer) => {
          const buffer = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk)
          totalBytes += buffer.length
          if (!outputStream.write(buffer)) {
            readStream.pause()
          }
        })
        outputStream.on('drain', () => {
          readStream.resume()
        })
        readStream.on('end', () => {
          outputStream.end()
          resolve()
        })
        readStream.on('error', reject)
        outputStream.on('error', reject)
      })
      const endTime = Date.now()
      const processingTime = endTime - startTime
      return {
        success: true,
        data: Dict[str, Any]
      }
    } catch (error) {
      return {
        success: false,
        error: error instanceof ServiceError ? error : new ServiceError(
          'StreamConversionError',
          'Failed to convert video stream',
          { error }
        ),
        data: null
      }
    } finally {
      if (tempInputPath) {
        await fs.unlink(tempInputPath).catch(() => {})
      }
      if (tempOutputPath) {
        await fs.unlink(tempOutputPath).catch(() => {})
      }
    }
  }
  public async cleanup(): Promise<void> {
  }
} 