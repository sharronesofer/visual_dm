import { promises as fs } from 'fs';
import { createReadStream, createWriteStream } from 'fs';
import { lookup } from 'mime-types';
import { v4 as uuidv4 } from 'uuid';
import path from 'path';
import { spawn } from 'child_process';
import { BaseFormatConverter } from './BaseFormatConverter';
import { 
  ConversionOptions, 
  ConversionResult, 
  ConversionProgress,
  StreamConversionResult
} from './FormatConverter';
import { ServiceResponse, ServiceError } from '../base/types';
import { Readable, Writable } from 'stream';

interface PandocOptions extends ConversionOptions {
  pageRange?: string;
  resolution?: number;
  tableOfContents?: boolean;
  numberSections?: boolean;
  highlightStyle?: string;
  standalone?: boolean;
  template?: string;
  css?: string;
  pdfEngine?: 'pdflatex' | 'xelatex' | 'lualatex' | 'wkhtmltopdf';
}

export class DocumentFormatConverter extends BaseFormatConverter {
  private readonly supportedInputFormats = [
    'text/markdown',
    'text/plain',
    'text/html',
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.oasis.opendocument.text',
    'application/rtf',
    'application/x-latex',
    'application/x-tex'
  ];

  private readonly supportedOutputFormats = [
    'md',
    'txt',
    'html',
    'pdf',
    'docx',
    'odt',
    'rtf',
    'latex',
    'epub'
  ];

  private readonly pandocFormatMap: Record<string, string> = {
    md: 'markdown',
    txt: 'plain',
    html: 'html5',
    pdf: 'pdf',
    docx: 'docx',
    odt: 'odt',
    rtf: 'rtf',
    latex: 'latex',
    epub: 'epub'
  };

  private tempDir: string;

  constructor(tempDir: string = path.join(process.cwd(), 'temp')) {
    super();
    this.tempDir = tempDir;
    Object.assign(this.defaultOptions, {
      targetFormat: 'pdf',
      resolution: 300,
      tableOfContents: false,
      numberSections: false,
      highlightStyle: 'tango',
      standalone: true
    });
  }

  private handleError(error: unknown): ServiceResponse<ConversionResult> {
    const errorMessage = error instanceof Error ? error.message : String(error);
    this.logger.error('Document conversion error:', { error: errorMessage });
    const serviceError: ServiceError = {
      code: 'DOCUMENT_CONVERSION_ERROR',
      message: errorMessage,
      status: 500
    };
    return {
      success: false,
      error: serviceError,
      data: null
    };
  }

  private mergeWithDefaultOptions(options?: ConversionOptions): PandocOptions {
    return {
      ...this.defaultOptions,
      ...options
    } as PandocOptions;
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

  protected async validateOptions(options?: ConversionOptions): Promise<PandocOptions> {
    const mergedOptions = this.mergeWithDefaultOptions(options);

    // Validate target format
    if (!mergedOptions.targetFormat || !this.canConvertTo(mergedOptions.targetFormat)) {
      throw new Error(`Unsupported target format: ${mergedOptions.targetFormat}`);
    }

    // Validate document-specific options
    if (mergedOptions.pageRange && !/^\d+(-\d+)?$/.test(mergedOptions.pageRange)) {
      throw new Error('Invalid page range format. Use format like "1-5" or "3"');
    }

    if (mergedOptions.resolution && (mergedOptions.resolution < 72 || mergedOptions.resolution > 2400)) {
      throw new Error('Resolution must be between 72 and 2400 DPI');
    }

    if (mergedOptions.pdfEngine && 
        !['pdflatex', 'xelatex', 'lualatex', 'wkhtmltopdf'].includes(mergedOptions.pdfEngine)) {
      throw new Error('Invalid PDF engine. Supported engines: pdflatex, xelatex, lualatex, wkhtmltopdf');
    }

    return mergedOptions;
  }

  private buildPandocArgs(inputPath: string, outputPath: string, options: PandocOptions): string[] {
    const args: string[] = [
      '-f', this.pandocFormatMap[path.extname(inputPath).slice(1)] || 'markdown',
      '-t', this.pandocFormatMap[options.targetFormat] || options.targetFormat,
      '-o', outputPath,
      inputPath
    ];

    if (options.standalone) {
      args.push('--standalone');
    }

    if (options.tableOfContents) {
      args.push('--toc');
    }

    if (options.numberSections) {
      args.push('--number-sections');
    }

    if (options.highlightStyle) {
      args.push('--highlight-style', options.highlightStyle);
    }

    if (options.template) {
      args.push('--template', options.template);
    }

    if (options.css) {
      args.push('--css', options.css);
    }

    if (options.targetFormat === 'pdf' && options.pdfEngine) {
      args.push('--pdf-engine', options.pdfEngine);
    }

    return args;
  }

  protected async processStream(
    inputStream: Readable,
    outputStream: Writable,
    options: PandocOptions,
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

      // Build pandoc arguments
      const args = this.buildPandocArgs(tempInputPath, tempOutputPath, options);

      // Run pandoc
      await new Promise<void>((resolve, reject) => {
        const pandoc = spawn('pandoc', args);
        let stderr = '';

        pandoc.stderr.on('data', (data: Buffer) => {
          stderr += data.toString();
        });

        pandoc.on('close', (code: number) => {
          if (code === 0) {
            resolve();
          } else {
            reject(new Error(`Pandoc failed with code ${code}: ${stderr}`));
          }
        });

        pandoc.on('error', reject);
      });

      // Read the output file in chunks and write to output stream
      const readStream = createReadStream(tempOutputPath, {
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

      // Get output file stats
      const stats = await fs.stat(tempOutputPath);
      const endTime = Date.now();
      const conversionTime = endTime - startTime;

      // Update stats
      this.updateStats(true, inputStream, outputStream, conversionTime);

      return {
        success: true,
        data: {
          metadata: {
            format: options.targetFormat,
            size: stats.size,
            createdAt: new Date()
          },
          originalFormat: path.extname(tempInputPath).slice(1),
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

      // Build pandoc arguments
      const args = this.buildPandocArgs(inputPath, outputPath, validatedOptions);

      // Run pandoc
      await new Promise<void>((resolve, reject) => {
        const pandoc = spawn('pandoc', args);
        let stderr = '';

        pandoc.stderr.on('data', (data: Buffer) => {
          stderr += data.toString();
        });

        pandoc.on('close', (code: number) => {
          if (code === 0) {
            resolve();
          } else {
            reject(new Error(`Pandoc failed with code ${code}: ${stderr}`));
          }
        });

        pandoc.on('error', reject);
      });

      // Read the output file
      const outputBuffer = await fs.readFile(outputPath);
      const endTime = Date.now();
      const conversionTime = endTime - startTime;

      // Get output file stats
      const stats = await fs.stat(outputPath);

      // Update conversion stats
      this.updateStats(true, input, outputBuffer, conversionTime);

      // Return the result
      return {
        success: true,
        data: {
          data: outputBuffer,
          metadata: {
            format: validatedOptions.targetFormat,
            size: stats.size,
            createdAt: new Date()
          },
          originalFormat: path.extname(inputPath).slice(1),
          conversionTime
        }
      };
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