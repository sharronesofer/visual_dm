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
import * as os from 'os';
import { StreamProcessingResult, ConversionMetadata } from '../types/MediaProcessing';

interface FFmpegProgress {
  frames: number;
  currentFps: number;
  currentKbps: number;
  targetSize: number;
  timemark: string;
  percent: number;
}

interface FFmpegFormatOptions {
  [key: string]: {
    videoCodec?: string;
    audioCodec?: string;
    videoBitrate?: string;
    audioBitrate?: string;
    preset?: string;
  };
}

export class VideoFormatConverter extends BaseFormatConverter {
  private readonly supportedInputFormats = [
    'video/mp4',
    'video/webm',
    'video/x-matroska',
    'video/quicktime',
    'video/x-msvideo',
    'video/x-ms-wmv',
    'video/mpeg',
    'video/3gpp'
  ];

  private readonly supportedOutputFormats = [
    'mp4',
    'webm',
    'mkv',
    'mov',
    'avi'
  ];

  private tempDir: string;
  private defaultVideoCodecs: Record<string, string> = {
    mp4: 'libx264',
    webm: 'libvpx-vp9',
    mkv: 'libx264',
    mov: 'libx264',
    avi: 'mpeg4'
  };

  private defaultAudioCodecs: Record<string, string> = {
    mp4: 'aac',
    webm: 'libvorbis',
    mkv: 'aac',
    mov: 'aac',
    avi: 'mp3'
  };

  private startTime: number;
  private conversionStartTime: number;
  private totalDuration: number;

  constructor(tempDir: string = path.join(process.cwd(), 'temp')) {
    super();
    this.tempDir = tempDir;
    this.startTime = Date.now();
    this.conversionStartTime = this.startTime;
    this.totalDuration = 0;
    Object.assign(this.defaultOptions, {
      targetFormat: 'mp4',
      quality: 23, // For x264/x265, lower is better (0-51)
      bitrate: '2M',
      audioBitrate: '128k',
      fps: 30,
      audioChannels: 2,
      sampleRate: 44100
    });
  }

  private handleError(error: unknown): ServiceResponse<ConversionResult> {
    const errorMessage = error instanceof Error ? error.message : String(error);
    this.logger.error('Video conversion error:', { error: errorMessage });
    const serviceError: ServiceError = {
      code: 'VIDEO_CONVERSION_ERROR',
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

    // Validate video-specific options
    if (mergedOptions.fps && (mergedOptions.fps < 1 || mergedOptions.fps > 240)) {
      throw new Error('Frame rate must be between 1 and 240 fps');
    }

    if (mergedOptions.bitrate && !/^\d+[kKmM]$/.test(mergedOptions.bitrate)) {
      throw new Error('Invalid bitrate format. Use format like "2M", "800k", etc.');
    }

    if (mergedOptions.audioBitrate && !/^\d+[kKmM]$/.test(mergedOptions.audioBitrate)) {
      throw new Error('Invalid audio bitrate format. Use format like "128k", "320k", etc.');
    }

    if (mergedOptions.width && (mergedOptions.width < 1 || mergedOptions.width > 7680)) {
      throw new Error('Width must be between 1 and 7680 pixels');
    }

    if (mergedOptions.height && (mergedOptions.height < 1 || mergedOptions.height > 4320)) {
      throw new Error('Height must be between 1 and 4320 pixels');
    }

    if (mergedOptions.quality !== undefined) {
      const format = mergedOptions.targetFormat.toLowerCase();
      if (['mp4', 'mkv', 'mov'].includes(format)) {
        if (mergedOptions.quality < 0 || mergedOptions.quality > 51) {
          throw new Error('CRF quality must be between 0 and 51 (lower is better)');
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

      // Get video metadata for progress tracking
      const metadata = await this.getVideoMetadata(tempInputPath);
      const totalDuration = parseFloat(metadata.format?.duration?.toString() || '0');
      const frameRate = options.fps || 
        (metadata.streams?.[0]?.r_frame_rate ? 
          parseFloat(metadata.streams[0].r_frame_rate.split('/')[0]) / 
          parseFloat(metadata.streams[0].r_frame_rate.split('/')[1]) : 
          30
        );
      const totalFrames = Math.ceil(totalDuration * frameRate);

      // Configure FFmpeg command
      const format = options.targetFormat.toLowerCase();
      let command = ffmpeg(tempInputPath);

      // Set video codec
      command = command.videoCodec(options.videoCodec || this.defaultVideoCodecs[format]);

      // Set audio codec
      command = command.audioCodec(options.audioCodec || this.defaultAudioCodecs[format]);

      // Set video bitrate if specified
      if (options.bitrate) {
        command = command.videoBitrate(options.bitrate);
      }

      // Set audio bitrate if specified
      if (options.audioBitrate) {
        command = command.audioBitrate(options.audioBitrate);
      }

      // Set frame rate if specified
      if (options.fps) {
        command = command.fps(options.fps);
      }

      // Set size if specified
      if (options.width || options.height) {
        command = command.size(`${options.width || '?'}x${options.height || '?'}`);
      }

      // Set audio channels if specified
      if (options.audioChannels) {
        command = command.audioChannels(options.audioChannels);
      }

      // Set audio sample rate if specified
      if (options.sampleRate) {
        command = command.audioFrequency(options.sampleRate);
      }

      // Set quality (CRF for x264/x265)
      if (options.quality && ['mp4', 'mkv', 'mov'].includes(format)) {
        command = command.addOption('-crf', options.quality.toString());
      }

      // Set preset if specified
      if (options.preset) {
        command = command.addOption('-preset', options.preset);
      }

      // Process the video and write to output stream
      let processedBytes = 0;
      await new Promise<void>((resolve, reject) => {
        const ffmpegCommand = command.output(tempOutputPath!);
        
        // Add event handlers in the correct order
        ffmpegCommand.on('error', (err: Error) => {
          this.logger.error('FFmpeg conversion error:', err);
          reject(new ServiceError('CONVERSION_ERROR', `FFmpeg conversion failed: ${err.message}`, { format, options }));
        });
        ffmpegCommand.on('end', () => resolve());
        
        // Add progress handler
        (ffmpegCommand as any).on('progress', (progress: FFmpegProgress) => {
          processedBytes = Math.floor((progress.frames / totalFrames) * (metadata.format?.size || 0));
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
          if (!outputStream.write(buffer)) {
            // Handle backpressure
            readStream.pause();
            outputStream.once('drain', () => readStream.resume());
          }
        });
        readStream.on('end', () => {
          outputStream.end();
          resolve();
        });
        readStream.on('error', (err) => {
          this.logger.error('Stream read error:', err);
          reject(new ServiceError('STREAM_READ_ERROR', `Failed to read converted video: ${err.message}`));
        });
        outputStream.on('error', (err) => {
          this.logger.error('Stream write error:', err);
          reject(new ServiceError('STREAM_WRITE_ERROR', `Failed to write converted video: ${err.message}`));
        });
      });

      // Get output metadata
      const outputMetadata = await this.getVideoMetadata(tempOutputPath);
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
            width: outputMetadata.streams?.[0]?.width,
            height: outputMetadata.streams?.[0]?.height,
            duration: outputMetadata.format?.duration,
            bitrate: outputMetadata.format?.bit_rate,
            codec: outputMetadata.streams?.[0]?.codec_name,
            fps: outputMetadata.streams?.[0]?.r_frame_rate,
            audioCodec: outputMetadata.streams?.[1]?.codec_name,
            audioChannels: outputMetadata.streams?.[1]?.channels,
            audioSampleRate: outputMetadata.streams?.[1]?.sample_rate,
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
      const metadata = await this.getVideoMetadata(inputPath);
      const originalFormat = metadata.format?.format_name || 'unknown';
      const totalDuration = parseFloat(metadata.format?.duration?.toString() || '0');
      const frameRate = validatedOptions.fps || 
        (metadata.streams?.[0]?.r_frame_rate ? 
          parseFloat(metadata.streams[0].r_frame_rate.split('/')[0]) / 
          parseFloat(metadata.streams[0].r_frame_rate.split('/')[1]) : 
          30
        );
      const totalFrames = Math.ceil(totalDuration * frameRate);

      // Configure FFmpeg command
      const format = validatedOptions.targetFormat.toLowerCase();
      let command = ffmpeg(inputPath);

      try {
        // Set video codec
        command = command.videoCodec(validatedOptions.videoCodec || this.defaultVideoCodecs[format]);

        // Set audio codec
        command = command.audioCodec(validatedOptions.audioCodec || this.defaultAudioCodecs[format]);

        // Set video bitrate if specified
        if (validatedOptions.bitrate) {
          command = command.videoBitrate(validatedOptions.bitrate);
        }

        // Set audio bitrate if specified
        if (validatedOptions.audioBitrate) {
          command = command.audioBitrate(validatedOptions.audioBitrate);
        }

        // Set frame rate if specified
        if (validatedOptions.fps) {
          command = command.fps(validatedOptions.fps);
        }

        // Set size if specified
        if (validatedOptions.width || validatedOptions.height) {
          command = command.size(`${validatedOptions.width || '?'}x${validatedOptions.height || '?'}`);
        }

        // Set audio channels if specified
        if (validatedOptions.audioChannels) {
          command = command.audioChannels(validatedOptions.audioChannels);
        }

        // Set audio sample rate if specified
        if (validatedOptions.sampleRate) {
          command = command.audioFrequency(validatedOptions.sampleRate);
        }

        // Set quality (CRF for x264/x265)
        if (validatedOptions.quality && ['mp4', 'mkv', 'mov'].includes(format)) {
          command = command.addOption('-crf', validatedOptions.quality.toString());
        }

        // Set preset if specified
        if (validatedOptions.preset) {
          command = command.addOption('-preset', validatedOptions.preset);
        }

        // Add progress handler
        (command as any).on('progress', (progress: FFmpegProgress) => {
          const bytesProcessed = Math.floor((progress.frames / totalFrames) * (metadata.format?.size || 0));
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

        // Convert the video
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
        const outputMetadata = await this.getVideoMetadata(outputPath);

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
              width: outputMetadata.streams?.[0]?.width,
              height: outputMetadata.streams?.[0]?.height,
              duration: outputMetadata.format?.duration,
              bitrate: outputMetadata.format?.bit_rate,
              codec: outputMetadata.streams?.[0]?.codec_name,
              fps: outputMetadata.streams?.[0]?.r_frame_rate,
              audioCodec: outputMetadata.streams?.[1]?.codec_name,
              audioChannels: outputMetadata.streams?.[1]?.channels,
              audioSampleRate: outputMetadata.streams?.[1]?.sample_rate,
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

  private async getVideoMetadata(filePath: string): Promise<ffmpeg.FfprobeData> {
    return new Promise((resolve, reject) => {
      ffmpeg.ffprobe(filePath, (error: Error | null, metadata: ffmpeg.FfprobeData) => {
        if (error) reject(error);
        else resolve(metadata);
      });
    });
  }

  protected updateStats(
    success: boolean,
    input: string | Buffer | Readable,
    output: Buffer | Writable | null,
    conversionTime: number
  ): void {
    this.stats.totalConversions++;
    if (success) {
      this.stats.successCount++;
    } else {
      this.stats.failureCount++;
    }
    // For stream-based operations, we don't track input/output sizes
    if (!(input instanceof Readable) && !(output instanceof Writable)) {
      this.stats.inputSize += Buffer.isBuffer(input) ? input.length : 0;
      this.stats.outputSize += output && Buffer.isBuffer(output) ? output.length : 0;
    }
    this.stats.conversionTime = conversionTime;
  }

  public async convertStream(
    inputStream: Readable,
    outputStream: Writable,
    options: ConversionOptions
  ): Promise<ServiceResponse<StreamProcessingResult>> {
    try {
      this.startTime = Date.now();

      // Validate formats
      const format = options.targetFormat.toLowerCase();
      if (!this.supportedOutputFormats.includes(format)) {
        throw new ServiceError(
          'UnsupportedFormat',
          `Unsupported output format: ${format}`,
          { supportedFormats: this.supportedOutputFormats }
        );
      }

      // Create temporary files for processing
      const tempDir = options.tempDir || os.tmpdir();
      const tempInputPath = path.join(tempDir, `input-${Date.now()}.tmp`);
      const tempOutputPath = path.join(tempDir, `output-${Date.now()}.${format}`);

      try {
        // Write input stream to temporary file
        const writeStream = createWriteStream(tempInputPath);
        await new Promise<void>((resolve, reject) => {
          inputStream.pipe(writeStream)
            .on('finish', resolve)
            .on('error', reject);
        });

        // Configure conversion options based on format
        const formatOptions: FFmpegFormatOptions = {
          mp4: {
            videoCodec: 'libx264',
            audioCodec: 'aac',
            preset: options.preset || 'medium',
          },
          webm: {
            videoCodec: 'libvpx-vp9',
            audioCodec: 'libopus',
          },
          mov: {
            videoCodec: 'libx264',
            audioCodec: 'aac',
            preset: options.preset || 'medium',
          },
          mkv: {
            videoCodec: 'libx264',
            audioCodec: 'aac',
            preset: options.preset || 'medium',
          },
        };

        const formatOption = formatOptions[format];

        // Start conversion timing
        this.conversionStartTime = Date.now();

        // Process the video using ffmpeg
        const command = ffmpeg(tempInputPath)
          .format(format)
          .videoCodec(options.videoCodec || formatOption.videoCodec)
          .audioCodec(options.audioCodec || formatOption.audioCodec)
          .videoBitrate(options.videoBitrate || this.defaultOptions.videoBitrate)
          .audioBitrate(options.audioBitrate || this.defaultOptions.audioBitrate);

        if (options.fps) {
          command.fps(options.fps);
        }

        if (options.width || options.height) {
          command.size(`${options.width || '?'}x${options.height || '?'}`);
        }

        if (formatOption.preset) {
          command.preset(formatOption.preset);
        }

        // Get video metadata and duration
        const metadata = await new Promise<ffmpeg.FfprobeData>((resolve, reject) => {
          ffmpeg.ffprobe(tempInputPath, (err, data) => {
            if (err) reject(err);
            else resolve(data);
          });
        });

        this.totalDuration = metadata.format.duration || 0;

        // Set up progress tracking
        command.on('progress', (progress) => {
          const bytesProcessed = Math.floor((progress.percent || 0) * metadata.format.size!);
          this.emit('progress', {
            bytesProcessed,
            totalBytes: metadata.format.size!,
          });
        });

        // Process the video
        await new Promise<void>((resolve, reject) => {
          command
            .save(tempOutputPath)
            .on('end', resolve)
            .on('error', reject);
        });

        // Calculate conversion time
        const conversionTime = Date.now() - this.conversionStartTime;

        // Get output file metadata
        const outputMetadata = await new Promise<ffmpeg.FfprobeData>((resolve, reject) => {
          ffmpeg.ffprobe(tempOutputPath, (err, data) => {
            if (err) reject(err);
            else resolve(data);
          });
        });

        // Stream the output file in chunks
        const outputFileStream = createReadStream(tempOutputPath);
        const chunkSize = Math.max(
          options.chunkSize || this.defaultOptions.chunkSize,
          1024 // Minimum 1KB chunks
        );

        let bytesProcessed = 0;
        const totalBytes = outputMetadata.format.size!;

        await new Promise<void>((resolve, reject) => {
          outputFileStream.on('data', (chunk: Buffer) => {
            bytesProcessed += chunk.length;
            
            // Emit progress
            this.emit('progress', {
              bytesProcessed,
              totalBytes,
            });

            // Write chunk to output stream with backpressure handling
            if (!outputStream.write(chunk)) {
              outputFileStream.pause();
              outputStream.once('drain', () => {
                outputFileStream.resume();
              });
            }
          });

          outputFileStream.on('end', resolve);
          outputFileStream.on('error', reject);
        });

        // End the output stream
        outputStream.end();

        // Prepare metadata
        const conversionMetadata: ConversionMetadata = {
          format,
          width: outputMetadata.streams[0]?.width || 0,
          height: outputMetadata.streams[0]?.height || 0,
          channels: outputMetadata.streams[1]?.channels || 0,
          bitrate: outputMetadata.format.bit_rate?.toString(),
          codec: outputMetadata.streams[0]?.codec_name,
          duration: outputMetadata.format.duration,
          size: totalBytes,
        };

        return {
          success: true,
          data: {
            bytesProcessed,
            totalBytes,
            processingTime: Date.now() - this.startTime,
            conversionTime,
            originalFormat: metadata.format.format_name || 'unknown',
            metadata: conversionMetadata,
          },
        };
      } finally {
        // Clean up temporary files
        await fs.unlink(tempInputPath).catch(() => {});
        if (await fs.access(tempOutputPath).then(() => true, () => false)) {
          await fs.unlink(tempOutputPath).catch(() => {});
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
      };
    }
  }
} 