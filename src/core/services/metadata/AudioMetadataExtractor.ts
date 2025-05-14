import ffmpeg from 'fluent-ffmpeg';
import * as mm from 'music-metadata';
import { promises as fs } from 'fs';
import { BaseMetadataExtractor } from './BaseMetadataExtractor';
import {
  MediaMetadata,
  MetadataExtractionOptions,
  MetadataExtractionResult
} from './MetadataExtractor';
import { ServiceResponse } from '../base/types';

export class AudioMetadataExtractor extends BaseMetadataExtractor {
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
        // Extract metadata using FFmpeg for technical details
        const ffprobeData = await this.getFfprobeData(input as string);
        const audioStream = ffprobeData.streams.find(stream => stream.codec_type === 'audio');

        // Extract metadata using music-metadata for ID3 tags and other format-specific metadata
        const musicMetadata = await this.getMusicMetadata(input);

        // Create metadata object
        const metadata: MediaMetadata = {
          format: ffprobeData.format.format_name || '',
          mimeType: this.getMimeType(input),
          size: parseInt(String(ffprobeData.format.size || '0')),
          duration: parseFloat(ffprobeData.format.duration || '0'),
          createdAt: new Date(),
          modifiedAt: new Date(),

          // Audio-specific metadata
          audioCodec: audioStream?.codec_name,
          audioBitrate: audioStream?.bit_rate ? parseInt(String(audioStream.bit_rate)) : undefined,
          audioChannels: audioStream?.channels,
          audioSampleRate: audioStream?.sample_rate ? parseInt(String(audioStream.sample_rate)) : undefined,

          // Additional metadata storage
          custom: {
            // Technical metadata
            totalBitrate: ffprobeData.format.bit_rate ? parseInt(String(ffprobeData.format.bit_rate)) : undefined,
            formatLongName: ffprobeData.format.format_long_name,
            audioProfile: audioStream?.profile,
            audioLayout: audioStream?.channel_layout,

            // Music metadata
            title: musicMetadata.common.title,
            artist: musicMetadata.common.artist,
            album: musicMetadata.common.album,
            year: musicMetadata.common.year,
            genre: musicMetadata.common.genre,
            trackNumber: musicMetadata.common.track.no,
            totalTracks: musicMetadata.common.track.of,
            discNumber: musicMetadata.common.disk.no,
            totalDiscs: musicMetadata.common.disk.of,
            composer: musicMetadata.common.composer,
            albumArtist: musicMetadata.common.albumartist,
            comment: musicMetadata.common.comment,
            bpm: musicMetadata.common.bpm,
            key: musicMetadata.common.key,
            lyrics: musicMetadata.common.lyrics,
            encodedBy: musicMetadata.common.encodedby,
            encoderSoftware: musicMetadata.common.encodersettings,
            replayGainTrackGain: musicMetadata.common.replaygain_track_gain,
            replayGainAlbumGain: musicMetadata.common.replaygain_album_gain,

            // Format-specific metadata
            container: musicMetadata.format.container,
            codec: musicMetadata.format.codec,
            lossless: musicMetadata.format.lossless,
            numberOfChannels: musicMetadata.format.numberOfChannels,
            bitsPerSample: musicMetadata.format.bitsPerSample,
            sampleRate: musicMetadata.format.sampleRate,
            duration: musicMetadata.format.duration,
            bitrate: musicMetadata.format.bitrate
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
    const tempFilePath = `${this.tempDir}/audio-${Date.now()}.tmp`;
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

  private async getMusicMetadata(input: string | Buffer): Promise<mm.IAudioMetadata> {
    if (Buffer.isBuffer(input)) {
      return mm.parseBuffer(input);
    } else {
      return mm.parseFile(input);
    }
  }
} 