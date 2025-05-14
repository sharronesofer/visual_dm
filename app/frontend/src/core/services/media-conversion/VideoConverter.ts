import { spawn } from 'child_process';
import { EventEmitter } from 'events';
import * as fs from 'fs';
import * as path from 'path';
import { v4 as uuidv4 } from 'uuid';
import { Readable, Writable } from 'stream';
import { BaseConverter } from './BaseConverter';
import { ConversionEventType, ConversionProgress, ConversionStage, BaseConfig, VideoConfig } from './types';
import { Logger, LogLevel } from './utils/LogUtils';
import { ProcessError, ValidationError, createStreamError } from './utils/ErrorUtils';
import { RetryHandler } from './utils/RetryUtils';
import { ThrottleStream } from './utils/StreamUtils';

/**
 * Video converter implementation using FFmpeg
 */
export class VideoConverter extends BaseConverter {
  private readonly supportedFormats = ['mp4', 'avi', 'mov', 'mkv', 'webm', 'flv'];
  private readonly logger: Logger;
  private readonly retryHandler: RetryHandler;
  private tempDir: string;

  constructor(logger: Logger) {
    super();
    this.logger = logger;
    this.retryHandler = new RetryHandler({}, logger);
    this.tempDir = path.join(process.cwd(), 'temp');
    this.createTempDirectory();
  }

  /**
   * Convert video from one format to another using FFmpeg
   */
  public async convert(
    input: string | Readable,
    output: string | Writable,
    config: BaseConfig
  ): Promise<void> {
    const videoConfig = config as VideoConfig;
    const inputPath = typeof input === 'string' ? input : await this.saveStreamToTemp(input);
    const outputPath = typeof output === 'string' ? output : await this.createTempFile();
    
    this.logger.info('Starting video conversion', { inputPath, outputPath, config: videoConfig });
    
    let tempFilePath: string | null = null;
    const isOutputTemp = typeof output !== 'string';
    
    try {
      await this.emitProgress(ConversionStage.INITIALIZING, 0);
      
      // Validation phase
      await this.emitProgress(ConversionStage.VALIDATING, 0);
      await this.validateInput(inputPath);
      await this.validateFormat(inputPath);
      await this.emitProgress(ConversionStage.VALIDATING, 100);

      // Create temp file for conversion
      tempFilePath = path.join(this.tempDir, `${uuidv4()}.tmp`);
      
      // Conversion phase with retry
      await this.retryHandler.execute(
        async () => {
          await this.executeConversion(inputPath, tempFilePath!, videoConfig);
        },
        ConversionStage.CONVERTING
      );

      // Finalization phase
      await this.emitProgress(ConversionStage.FINALIZING, 0);
      
      if (isOutputTemp) {
        // If output is a stream, pipe the converted file to it
        const readStream = fs.createReadStream(tempFilePath);
        await this.pipeToOutput(readStream, output as Writable);
      } else {
        // If output is a path, just rename the temp file
        await fs.promises.rename(tempFilePath, outputPath);
      }
      
      await this.emitProgress(ConversionStage.FINALIZING, 100);
      
      this.logger.info('Video conversion completed successfully', { outputPath });
    } catch (error) {
      const typedError = error instanceof Error ? error : new Error(String(error));
      this.logger.error('Video conversion failed', { error: typedError });
      
      if (tempFilePath) {
        await this.cleanup(tempFilePath);
      }
      
      // Clean up temp files if we created them
      if (typeof input !== 'string') {
        await this.cleanup(inputPath);
      }
      if (isOutputTemp) {
        await this.cleanup(outputPath);
      }
      
      throw typedError;
    }
  }

  private async validateInput(inputPath: string): Promise<void> {
    if (!fs.existsSync(inputPath)) {
      throw new ValidationError('Input file does not exist', { path: inputPath });
    }
  }

  private async validateFormat(inputPath: string): Promise<void> {
    const extension = path.extname(inputPath).toLowerCase().slice(1);
    if (!this.supportedFormats.includes(extension)) {
      throw new ValidationError('Unsupported video format', {
        format: extension,
        supportedFormats: this.supportedFormats
      });
    }
  }

  private async executeConversion(
    inputPath: string,
    outputPath: string,
    config: VideoConfig
  ): Promise<void> {
    const {
      codec = 'libx264',
      resolution = '1920x1080',
      bitrate = '2M',
      fps = 30
    } = config;

    const ffmpegArgs = [
      '-i', inputPath,
      '-c:v', codec,
      '-b:v', bitrate,
      '-r', fps.toString(),
      '-s', resolution,
      '-c:a', 'aac',
      '-b:a', '192k',
      '-movflags', '+faststart',
      '-y',
      outputPath
    ];

    return new Promise<void>((resolve, reject) => {
      const process = spawn('ffmpeg', ffmpegArgs);
      let duration: number | null = null;
      let timeElapsed = 0;

      process.stderr.on('data', (data: Buffer) => {
        const output = data.toString();
        
        // Extract duration if not already found
        if (!duration) {
          const durationMatch = output.match(/Duration: (\d{2}):(\d{2}):(\d{2})/);
          if (durationMatch) {
            const [, hours, minutes, seconds] = durationMatch;
            duration = (parseInt(hours) * 3600 + parseInt(minutes) * 60 + parseInt(seconds));
          }
        }

        // Extract current timestamp
        const timeMatch = output.match(/time=(\d{2}):(\d{2}):(\d{2})/);
        if (timeMatch && duration) {
          const [, hours, minutes, seconds] = timeMatch;
          timeElapsed = parseInt(hours) * 3600 + parseInt(minutes) * 60 + parseInt(seconds);
          
          const progress = Math.min((timeElapsed / duration) * 100, 99);
          this.emitProgress(ConversionStage.CONVERTING, progress);
        }
      });

      process.on('error', (error: Error) => {
        reject(new ProcessError('FFmpeg process error', {
          command: 'ffmpeg',
          args: ffmpegArgs,
          error: error.message
        }));
      });

      process.on('exit', (code: number) => {
        if (code === 0) {
          resolve();
        } else {
          reject(new ProcessError('FFmpeg process failed', {
            command: 'ffmpeg',
            args: ffmpegArgs,
            exitCode: code
          }));
        }
      });
    });
  }

  private async saveStreamToTemp(input: Readable): Promise<string> {
    const tempPath = path.join(this.tempDir, `${uuidv4()}.tmp`);
    const writeStream = fs.createWriteStream(tempPath);
    
    try {
      await this.pipeToOutput(input, writeStream);
      return tempPath;
    } catch (error) {
      await this.cleanup(tempPath);
      throw error;
    }
  }

  private async createTempFile(): Promise<string> {
    return path.join(this.tempDir, `${uuidv4()}.tmp`);
  }

  private async pipeToOutput(input: Readable, output: Writable): Promise<void> {
    return new Promise((resolve, reject) => {
      input.pipe(output)
        .on('finish', resolve)
        .on('error', (error) => {
          reject(createStreamError('Stream operation failed', 'output', error));
        });
    });
  }

  private async cleanup(filePath: string): Promise<void> {
    try {
      await this.emitProgress(ConversionStage.CLEANING_UP, 0);
      if (fs.existsSync(filePath)) {
        await fs.promises.unlink(filePath);
      }
      await this.emitProgress(ConversionStage.CLEANING_UP, 100);
    } catch (error) {
      const typedError = error instanceof Error ? error : new Error(String(error));
      this.logger.error('Error during cleanup', { error: typedError });
      throw createStreamError('Failed to clean up temporary file', 'output', typedError);
    }
  }

  private async createTempDirectory(): Promise<void> {
    try {
      await fs.promises.mkdir(this.tempDir, { recursive: true });
    } catch (error) {
      const typedError = error instanceof Error ? error : new Error(String(error));
      this.logger.error('Error creating temp directory', { error: typedError });
      throw createStreamError('Failed to create temporary directory', 'output', typedError);
    }
  }
} 