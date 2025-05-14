import { spawn } from 'child_process';
import { Readable, Writable } from 'stream';
import { promises as fsPromises } from 'fs';
import * as fs from 'fs';
import * as path from 'path';
import { v4 as uuidv4 } from 'uuid';
import { BaseConverter } from './BaseConverter';
import { AudioConverterConfig, ConverterConfig, ConversionProgress, ConversionStage } from './types';
import { ConversionError, ProcessError, ValidationError } from './utils/ErrorUtils';
import { Logger, LogLevel } from './utils/LogUtils';
import { RetryHandler, RetryConfig } from './utils/RetryUtils';

/**
 * Audio converter implementation using FFmpeg
 */
export class AudioConverter extends BaseConverter {
  private readonly defaultAudioCodecs: Record<string, string> = {
    mp3: 'libmp3lame',
    wav: 'pcm_s16le',
    ogg: 'libvorbis',
    aac: 'aac',
    m4a: 'aac',
    opus: 'libopus'
  };

  private tempDir: string;
  protected logger: Logger;
  private retryHandler: RetryHandler;

  constructor(
    tempDir: string = path.join(process.cwd(), 'temp'),
    retryConfig?: Partial<RetryConfig>
  ) {
    super();
    this.tempDir = tempDir;
    this.logger = new Logger({ minLevel: LogLevel.INFO });
    this.retryHandler = new RetryHandler(retryConfig);
    
    this.supportedInputFormats = [
      'mp3', 'wav', 'aac', 'ogg', 'm4a', 'flac',
      'wma', 'aiff', 'opus', 'ac3', 'webm'
    ];
    
    this.supportedOutputFormats = [
      'mp3', 'wav', 'aac', 'ogg', 'm4a', 'flac',
      'opus'
    ];
  }

  /**
   * Convert audio from one format to another using FFmpeg
   */
  public async convert(
    input: string | Readable,
    output: string | Writable,
    config: ConverterConfig
  ): Promise<void> {
    if (!this.validateConfig(config)) {
      throw new ValidationError('Invalid configuration');
    }

    const audioConfig = config as AudioConverterConfig;
    let inputPath: string | undefined;
    let outputPath: string | undefined;
    let isTemporaryInput = false;
    let isTemporaryOutput = false;
    
    try {
      this.emitProgress({
        percent: 0,
        bytesProcessed: 0,
        timeElapsed: 0,
        stage: ConversionStage.INITIALIZING,
        details: {
          inputFormat: audioConfig.inputFormat,
          outputFormat: audioConfig.outputFormat
        }
      });

      // Create temp directory if needed
      await fsPromises.mkdir(this.tempDir, { recursive: true });

      // Handle input
      if (typeof input === 'string') {
        await fsPromises.access(input).catch(() => {
          throw new ValidationError(`Input file not accessible: ${input}`);
        });
        inputPath = input;
      } else {
        inputPath = path.join(this.tempDir, `input-${uuidv4()}`);
        isTemporaryInput = true;
        await this.streamToFile(input, inputPath);
      }

      // Handle output
      if (typeof output === 'string') {
        outputPath = output;
      } else {
        outputPath = path.join(this.tempDir, `output-${uuidv4()}.${audioConfig.outputFormat}`);
        isTemporaryOutput = true;
      }

      this.emitProgress({
        percent: 0,
        bytesProcessed: 0,
        timeElapsed: 0,
        stage: ConversionStage.VALIDATING,
        details: {
          inputPath,
          outputPath
        }
      });

      // Get input metadata for progress tracking
      const metadata = await this.getMetadata(inputPath);
      const totalDuration = parseFloat(metadata.format?.duration || '0');

      // Convert the audio with retry logic
      await this.retryHandler.withRetry(
        async () => {
          await this.runFFmpeg(inputPath!, outputPath!, audioConfig, totalDuration);
        },
        {
          operationName: 'Audio conversion',
          cleanupFn: async () => {
            // Clean up output file if it exists (for retry)
            if (isTemporaryOutput && outputPath) {
              try {
                await fsPromises.unlink(outputPath);
              } catch (error) {
                // Ignore errors if file doesn't exist
                if ((error as NodeJS.ErrnoException).code !== 'ENOENT') {
                  this.logger.warn('Error cleaning up temporary output file', { error });
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
              details: {
                error: error.message,
                attempt,
                inputFormat: audioConfig.inputFormat,
                outputFormat: audioConfig.outputFormat
              }
            });
          }
        }
      );

      this.emitProgress({
        percent: 100,
        bytesProcessed: metadata.format?.size || 0,
        totalBytes: metadata.format?.size || 0,
        timeElapsed: totalDuration,
        stage: ConversionStage.FINALIZING,
        details: {
          inputFormat: audioConfig.inputFormat,
          outputFormat: audioConfig.outputFormat
        }
      });

      // If output is a stream, pipe the result
      if (isTemporaryOutput && outputPath) {
        const outputStream = output as Writable;
        await this.fileToStream(outputPath, outputStream);
      }

      this.emitComplete();
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
      );
      this.logger.error('Conversion failed', { error: conversionError });
      throw conversionError;
    } finally {
      this.emitProgress({
        percent: 100,
        bytesProcessed: 0,
        timeElapsed: 0,
        stage: ConversionStage.CLEANING_UP
      });

      // Cleanup temporary files
      try {
        if (isTemporaryInput && inputPath) {
          await fsPromises.unlink(inputPath);
        }
        if (isTemporaryOutput && outputPath) {
          await fsPromises.unlink(outputPath);
        }
      } catch (cleanupError) {
        this.logger.warn('Error cleaning up temporary files', {
          error: cleanupError
        });
      }
    }
  }

  /**
   * Run FFmpeg command with the specified configuration
   */
  private async runFFmpeg(
    inputPath: string,
    outputPath: string,
    config: AudioConverterConfig,
    totalDuration: number
  ): Promise<void> {
    return new Promise<void>((resolve, reject) => {
      const args = this.buildFFmpegArgs(config, inputPath, outputPath);
      const ffmpeg = spawn('ffmpeg', args);
      let lastProgress = 0;

      ffmpeg.stderr.on('data', (data: Buffer) => {
        const output = data.toString();
        const timeMatch = output.match(/time=(\d+:\d+:\d+.\d+)/);
        
        if (timeMatch) {
          const time = this.timeToSeconds(timeMatch[1]);
          const percent = Math.min(Math.round((time / totalDuration) * 100), 100);
          
          // Only emit progress if it has changed significantly
          if (percent > lastProgress + 1 || percent === 100) {
            lastProgress = percent;
            this.emitProgress({
              percent,
              bytesProcessed: Math.floor((percent / 100) * fs.statSync(inputPath).size),
              totalBytes: fs.statSync(inputPath).size,
              timeElapsed: time,
              timeRemaining: totalDuration - time,
              stage: ConversionStage.CONVERTING,
              details: {
                currentTime: timeMatch[1],
                totalDuration: this.secondsToTimestamp(totalDuration)
              }
            });
          }
        }
      });

      ffmpeg.on('error', (error: Error) => {
        reject(new ProcessError('FFmpeg process error', {
          command: 'ffmpeg',
          args,
          error: error.message
        }));
      });

      ffmpeg.on('exit', (code: number) => {
        if (code === 0) {
          resolve();
        } else {
          reject(new ProcessError('FFmpeg process failed', {
            command: 'ffmpeg',
            args,
            exitCode: code
          }));
        }
      });
    });
  }

  /**
   * Build FFmpeg command arguments based on configuration
   */
  private buildFFmpegArgs(config: AudioConverterConfig, inputPath: string, outputPath: string): string[] {
    const args: string[] = [
      '-i', inputPath,
      '-y'  // Overwrite output files without asking
    ];

    // Add audio codec
    const format = config.outputFormat.toLowerCase();
    const codec = config.codec || this.defaultAudioCodecs[format];
    if (codec) {
      args.push('-c:a', codec);
    }

    // Add channels if specified
    if (config.channels) {
      args.push('-ac', config.channels.toString());
    }

    // Add sample rate if specified
    if (config.sampleRate) {
      args.push('-ar', config.sampleRate.toString());
    }

    // Add bitrate if specified
    if (config.bitrate) {
      args.push('-b:a', config.bitrate);
    }

    // Add normalization if requested
    if (config.normalize) {
      args.push('-filter:a', 'loudnorm');
    }

    // Add quality settings
    if (config.quality !== undefined) {
      const formatQuality = this.getFormatSpecificQuality(format, config.quality);
      if (formatQuality.flag && formatQuality.value !== null) {
        args.push(formatQuality.flag, formatQuality.value.toString());
      }
    }

    // Add output path
    args.push(outputPath);

    return args;
  }

  /**
   * Get format-specific quality settings
   */
  private getFormatSpecificQuality(format: string, quality: number): {
    flag: string;
    value: number | null;
  } {
    // Convert quality (0-100) to format-specific values
    switch (format.toLowerCase()) {
      case 'mp3':
        // MP3 VBR quality: 0 (best) to 9 (worst)
        return {
          flag: '-q:a',
          value: Math.round(9 - (quality / 100) * 9)
        };
      case 'ogg':
        // Vorbis quality: -1 to 10
        return {
          flag: '-q:a',
          value: Math.round((quality / 100) * 10)
        };
      default:
        return {
          flag: '',
          value: null
        };
    }
  }

  /**
   * Convert time string (HH:MM:SS.ms) to seconds
   */
  private timeToSeconds(time: string): number {
    const parts = time.split(':').map(parseFloat);
    return parts[0] * 3600 + parts[1] * 60 + parts[2];
  }

  /**
   * Convert seconds to timestamp string
   */
  private secondsToTimestamp(seconds: number): string {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    const ms = Math.floor((seconds % 1) * 100);
    
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}.${ms.toString().padStart(2, '0')}`;
  }

  /**
   * Get audio metadata using FFprobe
   */
  private async getMetadata(filePath: string): Promise<any> {
    return new Promise((resolve, reject) => {
      const ffprobe = spawn('ffprobe', [
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        '-show_streams',
        filePath
      ]);

      let output = '';
      ffprobe.stdout.on('data', (data) => {
        output += data;
      });

      ffprobe.on('close', (code) => {
        if (code === 0) {
          try {
            resolve(JSON.parse(output));
          } catch (error) {
            reject(new ProcessError('Failed to parse FFprobe output', {
              command: 'ffprobe',
              output
            }));
          }
        } else {
          reject(new ProcessError('FFprobe process failed', {
            command: 'ffprobe',
            exitCode: code
          }));
        }
      });

      ffprobe.on('error', (err) => {
        reject(new ProcessError('FFprobe process error', {
          command: 'ffprobe',
          error: err
        }));
      });
    });
  }

  /**
   * Stream to file utility
   */
  private async streamToFile(stream: Readable, filePath: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const writeStream = fs.createWriteStream(filePath);
      stream.pipe(writeStream);
      
      writeStream.on('finish', resolve);
      writeStream.on('error', reject);
      stream.on('error', reject);
    });
  }

  /**
   * File to stream utility
   */
  private async fileToStream(filePath: string, outputStream: Writable): Promise<void> {
    return new Promise((resolve, reject) => {
      const readStream = fs.createReadStream(filePath);
      readStream.pipe(outputStream);
      
      outputStream.on('finish', resolve);
      outputStream.on('error', reject);
      readStream.on('error', reject);
    });
  }

  /**
   * Override validateConfig to add audio-specific validation
   */
  public validateConfig(config: ConverterConfig): boolean {
    if (!super.validateConfig(config)) {
      return false;
    }

    const audioConfig = config as AudioConverterConfig;
    
    // Validate channels if specified
    if (audioConfig.channels !== undefined &&
        (!Number.isInteger(audioConfig.channels) ||
         audioConfig.channels < 1 ||
         audioConfig.channels > 8)) {
      return false;
    }

    // Validate sample rate if specified
    if (audioConfig.sampleRate !== undefined &&
        (!Number.isInteger(audioConfig.sampleRate) ||
         audioConfig.sampleRate < 8000 ||
         audioConfig.sampleRate > 192000 ||
         ![8000, 11025, 22050, 44100, 48000, 96000, 192000].includes(audioConfig.sampleRate))) {
      return false;
    }

    // Validate bitrate format if specified
    if (audioConfig.bitrate && !this.isValidBitrate(audioConfig.bitrate)) {
      return false;
    }

    // Validate quality if specified
    if (audioConfig.quality !== undefined &&
        (typeof audioConfig.quality !== 'number' ||
         audioConfig.quality < 0 ||
         audioConfig.quality > 100)) {
      return false;
    }

    return true;
  }

  /**
   * Validate bitrate format (e.g., '320k', '128k')
   */
  private isValidBitrate(bitrate: string): boolean {
    return /^\d+[kM]$/i.test(bitrate);
  }
} 