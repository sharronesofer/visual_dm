import ffmpeg from 'fluent-ffmpeg';
import { promises as fs } from 'fs';
import { BaseMetadataExtractor } from './BaseMetadataExtractor';
import {
  MediaMetadata,
  MetadataExtractionOptions,
  MetadataExtractionResult
} from './MetadataExtractor';
import { ServiceResponse } from '../base/types';

export class VideoMetadataExtractor extends BaseMetadataExtractor {
  private readonly supportedTypes = [
    'video/mp4',
    'video/webm',
    'video/x-matroska',
    'video/quicktime',
    'video/x-msvideo',
    'video/x-ms-wmv',
    'video/mpeg',
    'video/3gpp'
  ];

  public canHandle(mimeType: string): boolean {
    return this.supportedTypes.includes(mimeType.toLowerCase());
  }

  public getSupportedTypes(): string[] {
    return [...this.supportedTypes];
  }

  protected async processExtraction(
    input: Buffer | string,
    options: MetadataExtractionOptions
  ): Promise<ServiceResponse<MetadataExtractionResult>> {
    try {
      // Validate input
      await this.validateInput(input);

      // If input is a buffer, write it to a temporary file
      let tempFilePath: string | undefined;
      if (Buffer.isBuffer(input)) {
        tempFilePath = await this.writeBufferToTemp(input);
        input = tempFilePath;
      }

      try {
        // Extract metadata using FFmpeg
        const ffprobeData = await this.getFfprobeData(input as string);

        // Process video stream metadata
        const videoStream = ffprobeData.streams.find(stream => stream.codec_type === 'video');
        const audioStream = ffprobeData.streams.find(stream => stream.codec_type === 'audio');

        // Create metadata object
        const metadata: MediaMetadata = {
          format: ffprobeData.format.format_name || '',
          mimeType: this.getMimeType(input),
          size: parseInt(String(ffprobeData.format.size || '0')),
          duration: parseFloat(ffprobeData.format.duration || '0'),
          createdAt: new Date(),
          modifiedAt: new Date(),

          // Video-specific metadata
          width: videoStream?.width,
          height: videoStream?.height,
          frameRate: videoStream?.r_frame_rate ? this.calculateFrameRate(videoStream.r_frame_rate) : undefined,
          videoCodec: videoStream?.codec_name,
          videoBitrate: videoStream?.bit_rate ? parseInt(String(videoStream.bit_rate)) : undefined,

          // Audio-specific metadata
          audioCodec: audioStream?.codec_name,
          audioBitrate: audioStream?.bit_rate ? parseInt(String(audioStream.bit_rate)) : undefined,
          audioChannels: audioStream?.channels,
          audioSampleRate: audioStream?.sample_rate ? parseInt(String(audioStream.sample_rate)) : undefined,

          // Additional metadata storage
          custom: {
            totalBitrate: ffprobeData.format.bit_rate ? parseInt(String(ffprobeData.format.bit_rate)) : undefined,
            formatLongName: ffprobeData.format.format_long_name,
            videoProfile: videoStream?.profile,
            pixelFormat: videoStream?.pix_fmt,
            colorSpace: videoStream?.color_space,
            colorRange: videoStream?.color_range,
            audioProfile: audioStream?.profile,
            audioLayout: audioStream?.channel_layout
          }
        };

        const result: MetadataExtractionResult = {
          metadata,
          cached: false,
          extractionTime: 0 // Will be set by base class
        };

        return {
          success: true,
          data: result
        };
      } finally {
        // Clean up temporary file if created
        if (tempFilePath) {
          await this.cleanup(tempFilePath);
        }
      }
    } catch (error) {
      return this.handleError(error);
    }
  }

  private async writeBufferToTemp(buffer: Buffer): Promise<string> {
    const tempFilePath = `${this.tempDir}/video-${Date.now()}.tmp`;
    await fs.mkdir(this.tempDir, { recursive: true });
    await fs.writeFile(tempFilePath, buffer);
    return tempFilePath;
  }

  private async getFfprobeData(filePath: string): Promise<ffmpeg.FfprobeData> {
    return new Promise((resolve, reject) => {
      ffmpeg.ffprobe(filePath, (error: Error | null, metadata: ffmpeg.FfprobeData) => {
        if (error) reject(error);
        else resolve(metadata);
      });
    });
  }

  private calculateFrameRate(rFrameRate: string): number {
    const [numerator, denominator] = rFrameRate.split('/').map(Number);
    return numerator / denominator;
  }
} 