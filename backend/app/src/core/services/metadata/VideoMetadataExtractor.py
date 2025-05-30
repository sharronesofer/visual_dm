from typing import Any, Dict


  MediaMetadata,
  MetadataExtractionOptions,
  MetadataExtractionResult
} from './MetadataExtractor'
class VideoMetadataExtractor extends BaseMetadataExtractor {
  private readonly supportedTypes = [
    'video/mp4',
    'video/webm',
    'video/x-matroska',
    'video/quicktime',
    'video/x-msvideo',
    'video/x-ms-wmv',
    'video/mpeg',
    'video/3gpp'
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
        const videoStream = ffprobeData.streams.find(stream => stream.codec_type === 'video')
        const audioStream = ffprobeData.streams.find(stream => stream.codec_type === 'audio')
        const metadata: MediaMetadata = {
          format: ffprobeData.format.format_name || '',
          mimeType: this.getMimeType(input),
          size: parseInt(String(ffprobeData.format.size || '0')),
          duration: parseFloat(ffprobeData.format.duration || '0'),
          createdAt: new Date(),
          modifiedAt: new Date(),
          width: videoStream?.width,
          height: videoStream?.height,
          frameRate: videoStream?.r_frame_rate ? this.calculateFrameRate(videoStream.r_frame_rate) : undefined,
          videoCodec: videoStream?.codec_name,
          videoBitrate: videoStream?.bit_rate ? parseInt(String(videoStream.bit_rate)) : undefined,
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
    const tempFilePath = `${this.tempDir}/video-${Date.now()}.tmp`
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
  private calculateFrameRate(rFrameRate: str): float {
    const [numerator, denominator] = rFrameRate.split('/').map(Number)
    return numerator / denominator
  }
} 