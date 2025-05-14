import ffmpeg from 'fluent-ffmpeg';
import { promises as fs } from 'fs';
import { createReadStream, createWriteStream } from 'fs';
import { lookup } from 'mime-types';
import { v4 as uuidv4 } from 'uuid';
import path from 'path';
import { BaseFormatConverter } from './BaseFormatConverter';
import { 
  ConversionOptions, 
  ConversionResult, 
  ConversionProgress,
  StreamConversionResult
} from './FormatConverter';
import { ServiceResponse, ServiceError } from '../base/types';
import { Readable, Writable } from 'stream';

interface FFmpegProgress {
  frames: number;
  currentFps: number;
  currentKbps: number;
  targetSize: number;
  timemark: string;
  percent: number;
}

export class AudioFormatConverter extends BaseFormatConverter {
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
  ];

  private readonly supportedOutputFormats = [
    'mp3',
    'wav',
    'ogg',
    'flac',
    'aac',
    'm4a'
  ];

  private tempDir: string;
  private defaultAudioCodecs: Record<string, string> = {
    mp3: 'libmp3lame',
    wav: 'pcm_s16le',
    ogg: 'libvorbis',
    flac: 'flac',
    aac: 'aac',
    m4a: 'aac'
  };

  constructor(tempDir: string = path.join(process.cwd(), 'temp')) {
    super();
    this.tempDir = tempDir;
    Object.assign(this.defaultOptions, {
      targetFormat: 'mp3',
      bitrate: '128k',
      channels: 2,
      sampleRate: 44100,
      quality: 4 // For formats that support VBR (0-9, lower is better)
    });
  }

  private handleError(error: unknown): ServiceResponse<ConversionResult> {
    const errorMessage = error instanceof Error ? error.message : String(error);
    this.logger.error('Audio conversion error:', { error: errorMessage });
    const serviceError: ServiceError = {
      code: 'AUDIO_CONVERSION_ERROR',
      message: errorMessage,
      status: 500
    };
    return {
      success: false,
      error: serviceError,
      data: null
    };
  }

  private mergeWithDefaultOptions(options?: ConversionOptions): ConversionOptions {
    return {
      ...this.defaultOptions,
      ...options
    };
  }

  private emitProgress(progress: ConversionProgress): void {
    this.emit('progress', progress);
  }

  protected async validateInput(input: Buffer | string): Promise<void> {
    try {
      if (Buffer.isBuffer(input)) {
        // For buffers, we'll try to detect the MIME type
        const mimeType = lookup(Buffer.from(input).toString('hex', 0, 8)) || 'application/octet-stream';
        if (!this.canConvertFrom(mimeType)) {
          throw new Error(`Unsupported input format: ${mimeType}`);
        }
      } else {
        // For file paths, check if file exists and has valid MIME type
        await fs.access(input);
        const mimeType = lookup(input);
        if (!mimeType || !this.canConvertFrom(mimeType)) {
          throw new Error(`Unsupported input format: ${mimeType || 'unknown'}`);
        }
      }
    } catch (error) {
      this.logger.error('Input validation failed:', error);
      throw error;
    }
  }

  protected async validateOptions(options?: ConversionOptions): Promise<ConversionOptions> {
    const mergedOptions = this.mergeWithDefaultOptions(options);

    // Validate target format
    if (!mergedOptions.targetFormat || !this.canConvertTo(mergedOptions.targetFormat)) {
      throw new Error(`Unsupported target format: ${mergedOptions.targetFormat}`);
    }

    // Validate audio-specific options
    if (mergedOptions.bitrate && !/^\d+[kKmM]$/.test(mergedOptions.bitrate)) {
      throw new Error('Invalid bitrate format. Use format like "128k", "320k", etc.');
    }

    if (mergedOptions.channels && (mergedOptions.channels < 1 || mergedOptions.channels > 8)) {
      throw new Error('Channels must be between 1 and 8');
    }

    if (mergedOptions.sampleRate && ![8000, 11025, 22050, 44100, 48000, 96000].includes(mergedOptions.sampleRate)) {
      throw new Error('Invalid sample rate. Use standard values: 8000, 11025, 22050, 44100, 48000, or 96000');
    }

    if (mergedOptions.quality !== undefined) {
      const format = mergedOptions.targetFormat.toLowerCase();
      if (['mp3', 'ogg'].includes(format)) {
        if (mergedOptions.quality < 0 || mergedOptions.quality > 9) {
          throw new Error('Quality (VBR) must be between 0 and 9 (lower is better)');
        }
      }
    }

    return mergedOptions;
  }

  protected async processStream(
    inputStream: Readable,
    outputStream: Writable,
    options: ConversionOptions,
    onProgress: (bytesProcessed: number) => void
  ): Promise<ServiceResponse<StreamConversionResult>> {
    let tempInputPath: string | undefined;
    let tempOutputPath: string | undefined;
    const startTime = Date.now();

    try {
      // Create temp directory if it doesn't exist
      await fs.mkdir(this.tempDir, { recursive: true });

      // Create temporary files for input and output
      tempInputPath = path.join(this.tempDir, `stream-input-${uuidv4()}`);
      tempOutputPath = path.join(this.tempDir, `stream-output-${uuidv4()}.${options.targetFormat}`);

      // Write input stream to temporary file
      const writeStream = createWriteStream(tempInputPath);
      let bytesWritten = 0;

      await new Promise<void>((resolve, reject) => {
        inputStream.on('data', (chunk: Buffer | string) => {
          const buffer = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk);
          bytesWritten += buffer.length;
          onProgress(bytesWritten);
          writeStream.write(buffer);
        });
        inputStream.on('end', () => {
          writeStream.end();
          resolve();
        });
        inputStream.on('error', reject);
        writeStream.on('error', reject);
      });

      // Get audio metadata for progress tracking
      const metadata = await this.getAudioMetadata(tempInputPath);
      const totalDuration = parseFloat(metadata.format?.duration?.toString() || '0');

      // Configure FFmpeg command
      const format = options.targetFormat.toLowerCase();
      let command = ffmpeg(tempInputPath);

      // Set audio codec
      command = command.audioCodec(options.audioCodec || this.defaultAudioCodecs[format]);

      // Set audio bitrate if specified
      if (options.bitrate) {
        command = command.audioBitrate(options.bitrate);
      }

      // Set audio channels if specified
      if (options.channels) {
        command = command.audioChannels(options.channels);
      }

      // Set audio sample rate if specified
      if (options.sampleRate) {
        command = command.audioFrequency(options.sampleRate);
      }

      // Set quality (VBR) for supported formats
      if (options.quality !== undefined && ['mp3', 'ogg'].includes(format)) {
        if (format === 'mp3') {
          command = command.addOption('-qscale:a', options.quality.toString());
        } else if (format === 'ogg') {
          command = command.addOption('-q:a', options.quality.toString());
        }
      }

      // Process the audio and write to output stream
      let processedBytes = 0;
      await new Promise<void>((resolve, reject) => {
        const ffmpegCommand = command.output(tempOutputPath!);
        
        // Add event handlers in the correct order
        ffmpegCommand.on('error', (err: Error) => reject(err));
        ffmpegCommand.on('end', () => resolve());
        
        // Add progress handler
        (ffmpegCommand as any).on('progress', (progress: FFmpegProgress) => {
          processedBytes = Math.floor((progress.percent || 0) * (metadata.format?.size || 0) / 100);
          onProgress(processedBytes);
        });

        ffmpegCommand.run();
      });

      // Read the output file in chunks and write to output stream
      const readStream = createReadStream(tempOutputPath!, {
        highWaterMark: options.chunkSize || this.defaultOptions.chunkSize
      });

      await new Promise<void>((resolve, reject) => {
        readStream.on('data', (chunk: Buffer | string) => {
          const buffer = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk);
          outputStream.write(buffer);
        });
        readStream.on('end', () => {
          outputStream.end();
          resolve();
        });
        readStream.on('error', reject);
        outputStream.on('error', reject);
      });

      // Get output metadata
      const outputMetadata = await this.getAudioMetadata(tempOutputPath);
      const endTime = Date.now();
      const conversionTime = endTime - startTime;

      // Update stats
      this.updateStats(true, inputStream, outputStream, conversionTime);

      return {
        success: true,
        data: {
          metadata: {
            format: options.targetFormat,
            size: outputMetadata.format?.size || 0,
            duration: outputMetadata.format?.duration,
            channels: outputMetadata.streams?.[0]?.channels,
            sampleRate: outputMetadata.streams?.[0]?.sample_rate,
            bitrate: outputMetadata.format?.bit_rate,
            createdAt: new Date()
          },
          originalFormat: metadata.format?.format_name || 'unknown',
          conversionTime
        }
      };

    } catch (error) {
      this.logger.error('Stream processing failed:', error);
      const serviceError: ServiceError = {
        code: 'STREAM_PROCESSING_ERROR',
        message: error instanceof Error ? error.message : String(error),
        status: 500
      };
      return {
        success: false,
        error: serviceError,
        data: null
      };
    } finally {
      // Clean up temporary files
      try {
        if (tempInputPath) {
          await fs.unlink(tempInputPath);
        }
        if (tempOutputPath) {
          await fs.unlink(tempOutputPath);
        }
      } catch (cleanupError) {
        this.logger.warn('Error cleaning up temporary files:', cleanupError);
      }
    }
  }

  async convert(input: Buffer | string, options?: ConversionOptions): Promise<ServiceResponse<ConversionResult>> {
    let inputPath: string | undefined;
    let outputPath: string | undefined;
    const startTime = Date.now();

    try {
      // Validate input and options
      await this.validateInput(input);
      const validatedOptions = await this.validateOptions(options);

      // Create temp directory if it doesn't exist
      await fs.mkdir(this.tempDir, { recursive: true });

      // Write input to temp file if it's a buffer
      if (Buffer.isBuffer(input)) {
        inputPath = path.join(this.tempDir, `input-${uuidv4()}`);
        await fs.writeFile(inputPath, input);
      } else {
        // If input is a path, just use it directly
        inputPath = input;
      }

      if (!inputPath) {
        return this.handleError('Failed to create input file');
      }

      outputPath = path.join(this.tempDir, `output-${uuidv4()}.${validatedOptions.targetFormat}`);

      // Get original format and metadata
      const metadata = await this.getAudioMetadata(inputPath);
      const originalFormat = metadata.format?.format_name || 'unknown';

      // Configure FFmpeg command
      const format = validatedOptions.targetFormat.toLowerCase();
      let command = ffmpeg(inputPath);

      try {
        // Set audio codec
        command = command.audioCodec(validatedOptions.audioCodec || this.defaultAudioCodecs[format]);

        // Set audio bitrate if specified
        if (validatedOptions.bitrate) {
          command = command.audioBitrate(validatedOptions.bitrate);
        }

        // Set audio channels if specified
        if (validatedOptions.channels) {
          command = command.audioChannels(validatedOptions.channels);
        }

        // Set audio sample rate if specified
        if (validatedOptions.sampleRate) {
          command = command.audioFrequency(validatedOptions.sampleRate);
        }

        // Set quality (VBR) for supported formats
        if (validatedOptions.quality !== undefined && ['mp3', 'ogg'].includes(format)) {
          if (format === 'mp3') {
            command = command.addOption('-qscale:a', validatedOptions.quality.toString());
          } else if (format === 'ogg') {
            command = command.addOption('-q:a', validatedOptions.quality.toString());
          }
        }

        // Add progress handler
        (command as any).on('progress', (progress: FFmpegProgress) => {
          const bytesProcessed = Math.floor((progress.percent || 0) * (metadata.format?.size || 0) / 100);
          this.emitProgress({
            bytesProcessed,
            totalBytes: metadata.format?.size || 0,
            percent: progress.percent || 0,
            stage: 'converting',
            timeElapsed: progress.timemark ? this.timemarkToSeconds(progress.timemark) : 0,
            timeRemaining: progress.targetSize ? (progress.targetSize - (progress.targetSize * (progress.percent || 0) / 100)) / 100 : undefined,
            currentFile: outputPath
          });
        });

        // Convert the audio
        await new Promise<void>((resolve, reject) => {
          command
            .output(outputPath!)
            .on('end', () => resolve())
            .on('error', (err: Error) => reject(err))
            .run();
        });

        // Read the output file
        const outputBuffer = await fs.readFile(outputPath);
        const endTime = Date.now();
        const conversionTime = endTime - startTime;

        // Get output metadata
        const outputMetadata = await this.getAudioMetadata(outputPath);

        // Update conversion stats
        this.updateStats(true, input, outputBuffer, conversionTime);

        // Return the result
        return {
          success: true,
          data: {
            data: outputBuffer,
            metadata: {
              format: validatedOptions.targetFormat,
              size: outputBuffer.length,
              duration: outputMetadata.format?.duration,
              channels: outputMetadata.streams?.[0]?.channels,
              sampleRate: outputMetadata.streams?.[0]?.sample_rate,
              bitrate: outputMetadata.format?.bit_rate,
              createdAt: new Date()
            },
            originalFormat,
            conversionTime
          }
        };
      } catch (ffmpegError) {
        return this.handleError(`FFmpeg error: ${ffmpegError}`);
      }
    } catch (error) {
      return this.handleError(error);
    } finally {
      // Clean up temp files
      try {
        if (Buffer.isBuffer(input) && inputPath) {
          await fs.unlink(inputPath);
        }
        if (outputPath) {
          await fs.unlink(outputPath);
        }
      } catch (error) {
        this.logger.warn('Error cleaning up temp files:', error);
      }
    }
  }

  async cleanup(): Promise<void> {
    await super.cleanup();
    // Clean up temp directory if empty
    try {
      const files = await fs.readdir(this.tempDir);
      if (files.length === 0) {
        await fs.rmdir(this.tempDir);
      }
    } catch (error) {
      this.logger.warn('Error cleaning up temp directory:', error);
    }
  }

  private async getAudioMetadata(filePath: string): Promise<ffmpeg.FfprobeData> {
    return new Promise((resolve, reject) => {
      ffmpeg.ffprobe(filePath, (error: Error | null, metadata: ffmpeg.FfprobeData) => {
        if (error) reject(error);
        else resolve(metadata);
      });
    });
  }

  private timemarkToSeconds(timemark: string): number {
    const parts = timemark.split(':');
    return parseInt(parts[0]) * 3600 + parseInt(parts[1]) * 60 + parseFloat(parts[2]);
  }

  public canConvertFrom(mimeType: string): boolean {
    return this.supportedInputFormats.includes(mimeType.toLowerCase());
  }

  public canConvertTo(format: string): boolean {
    return this.supportedOutputFormats.includes(format.toLowerCase());
  }

  public getSupportedInputFormats(): string[] {
    return [...this.supportedInputFormats];
  }

  public getSupportedOutputFormats(): string[] {
    return [...this.supportedOutputFormats];
  }
} 