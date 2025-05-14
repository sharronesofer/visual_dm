from typing import Any, Dict


  MediaMetadata,
  MetadataExtractionOptions,
  MetadataExtractionResult
} from './MetadataExtractor'
class AudioMetadataExtractor extends BaseMetadataExtractor {
  private readonly supportedTypes = [
    'audio/mpeg',
    'audio/mp4',
    'audio/ogg',
    'audio/wav',
    'audio/x-wav',
    'audio/webm',
    'audio/flac',
    'audio/x-flac',
    'audio/aac',
    'audio/x-m4a'
  ]
  public canHandle(mimeType: str): bool {
    return this.supportedTypes.includes(mimeType.toLowerCase())
  }
  public getSupportedTypes(): string[] {
    return [...this.supportedTypes]
  }
  protected async processExtraction(
    input: Buffer | string,
    options: MetadataExtractionOptions
  ): Promise<ServiceResponse<MetadataExtractionResult>> {
    try {
      await this.validateInput(input)
      let tempFilePath: str | undefined
      if (Buffer.isBuffer(input)) {
        tempFilePath = await this.writeBufferToTemp(input)
        input = tempFilePath
      }
      try {
        const ffprobeData = await this.getFfprobeData(input as string)
        const audioStream = ffprobeData.streams.find(stream => stream.codec_type === 'audio')
        const musicMetadata = await this.getMusicMetadata(input)
        const metadata: MediaMetadata = {
          format: ffprobeData.format.format_name || '',
          mimeType: this.getMimeType(input),
          size: parseInt(String(ffprobeData.format.size || '0')),
          duration: parseFloat(ffprobeData.format.duration || '0'),
          createdAt: new Date(),
          modifiedAt: new Date(),
          audioCodec: audioStream?.codec_name,
          audioBitrate: audioStream?.bit_rate ? parseInt(String(audioStream.bit_rate)) : undefined,
          audioChannels: audioStream?.channels,
          audioSampleRate: audioStream?.sample_rate ? parseInt(String(audioStream.sample_rate)) : undefined,
          custom: Dict[str, Any]
        }
        const result: MetadataExtractionResult = {
          metadata,
          cached: false,
          extractionTime: 0 
        }
        return {
          success: true,
          data: result
        }
      } finally {
        if (tempFilePath) {
          await this.cleanup(tempFilePath)
        }
      }
    } catch (error) {
      return this.handleError(error)
    }
  }
  private async writeBufferToTemp(buffer: Buffer): Promise<string> {
    const tempFilePath = `${this.tempDir}/audio-${Date.now()}.tmp`
    await fs.mkdir(this.tempDir, { recursive: true })
    await fs.writeFile(tempFilePath, buffer)
    return tempFilePath
  }
  private async getFfprobeData(filePath: str): Promise<ffmpeg.FfprobeData> {
    return new Promise((resolve, reject) => {
      ffmpeg.ffprobe(filePath, (error: Error | null, metadata: ffmpeg.FfprobeData) => {
        if (error) reject(error)
        else resolve(metadata)
      })
    })
  }
  private async getMusicMetadata(input: str | Buffer): Promise<mm.IAudioMetadata> {
    if (Buffer.isBuffer(input)) {
      return mm.parseBuffer(input)
    } else {
      return mm.parseFile(input)
    }
  }
} 