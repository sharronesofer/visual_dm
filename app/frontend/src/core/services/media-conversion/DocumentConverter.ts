import { spawn } from 'child_process';
import { Readable, Writable } from 'stream';
import { BaseConverter } from './BaseConverter';
import { DocumentConverterConfig, ConverterConfig } from './types';

/**
 * Document converter implementation using LibreOffice for most conversions
 * and specialized tools for specific formats
 */
export class DocumentConverter extends BaseConverter {
  constructor() {
    super();
    this.supportedInputFormats = [
      // Text documents
      'doc', 'docx', 'odt', 'rtf', 'txt', 'md',
      // Spreadsheets
      'xls', 'xlsx', 'ods', 'csv',
      // Presentations
      'ppt', 'pptx', 'odp',
      // PDF
      'pdf'
    ];
    
    this.supportedOutputFormats = [
      // Text documents
      'pdf', 'docx', 'odt', 'rtf', 'txt',
      // Spreadsheets
      'xlsx', 'ods', 'csv',
      // Presentations
      'pptx', 'odp',
      // Images (PDF pages)
      'png', 'jpg'
    ];
  }

  /**
   * Convert document from one format to another
   */
  public async convert(
    input: string | Readable,
    output: string | Writable,
    config: ConverterConfig
  ): Promise<void> {
    if (!this.validateConfig(config)) {
      throw new Error('Invalid configuration');
    }

    const docConfig = config as DocumentConverterConfig;
    const inputStream = this.createInputStream(input);
    const outputStream = this.createOutputStream(output);

    // Determine the conversion tool based on input/output formats
    const conversionTool = this.getConversionTool(
      docConfig.inputFormat,
      docConfig.outputFormat
    );

    return new Promise((resolve, reject) => {
      const startTime = Date.now();
      let totalBytes = 0;
      let processedBytes = 0;

      // Build command arguments based on the selected tool
      const { command, args } = this.buildConversionCommand(
        docConfig,
        conversionTool
      );

      // Spawn conversion process
      const process = spawn(command, args);

      // Handle process errors
      process.on('error', (err) => {
        this.emitError(err);
        reject(err);
      });

      // Handle process output for progress updates
      process.stderr.on('data', (data) => {
        const output = data.toString();
        // Parse tool-specific output for progress information
        const progress = this.parseProgressOutput(output, conversionTool);
        if (progress) {
          processedBytes = Math.floor(totalBytes * progress);
          this.emitProgress(this.calculateProgress(
            processedBytes,
            totalBytes,
            startTime
          ));
        }
      });

      // Pipe input through conversion process to output
      inputStream
        .on('error', (err) => {
          this.emitError(err);
          reject(err);
        })
        .on('data', (chunk) => {
          totalBytes += chunk.length;
        })
        .pipe(process.stdin);

      process.stdout
        .on('error', (err) => {
          this.emitError(err);
          reject(err);
        })
        .on('data', (chunk) => {
          processedBytes += chunk.length;
          this.emitProgress(this.calculateProgress(
            processedBytes,
            totalBytes,
            startTime
          ));
        })
        .pipe(outputStream);

      outputStream
        .on('error', (err) => {
          this.emitError(err);
          reject(err);
        })
        .on('finish', () => {
          this.emitComplete();
          resolve();
        });
    });
  }

  /**
   * Determine which conversion tool to use based on input/output formats
   */
  private getConversionTool(inputFormat: string, outputFormat: string): string {
    // PDF to image conversion
    if (inputFormat === 'pdf' && ['png', 'jpg'].includes(outputFormat)) {
      return 'pdftocairo';
    }
    
    // Markdown to other formats
    if (inputFormat === 'md') {
      return 'pandoc';
    }

    // CSV handling
    if (inputFormat === 'csv' || outputFormat === 'csv') {
      return 'ssconvert';
    }

    // Default to LibreOffice for most conversions
    return 'soffice';
  }

  /**
   * Build command and arguments for the selected conversion tool
   */
  private buildConversionCommand(
    config: DocumentConverterConfig,
    tool: string
  ): { command: string; args: string[] } {
    switch (tool) {
      case 'pdftocairo':
        return {
          command: 'pdftocairo',
          args: [
            '-singlefile',
            config.outputFormat === 'jpg' ? '-jpeg' : '-png',
            '-', // Read from stdin
            '-' // Write to stdout
          ]
        };

      case 'pandoc':
        return {
          command: 'pandoc',
          args: [
            '--from', 'markdown',
            '--to', this.getPandocFormat(config.outputFormat),
            '--output', '-' // Write to stdout
          ]
        };

      case 'ssconvert':
        return {
          command: 'ssconvert',
          args: [
            '--export-type', config.outputFormat,
            '-', // Read from stdin
            '-' // Write to stdout
          ]
        };

      case 'soffice':
      default:
        return {
          command: 'soffice',
          args: [
            '--headless',
            '--convert-to', config.outputFormat,
            '--outdir', '-', // Write to stdout
            '-' // Read from stdin
          ]
        };
    }
  }

  /**
   * Get Pandoc format identifier for output format
   */
  private getPandocFormat(format: string): string {
    const formatMap: { [key: string]: string } = {
      'pdf': 'pdf',
      'docx': 'docx',
      'odt': 'odt',
      'rtf': 'rtf',
      'txt': 'plain',
      'html': 'html'
    };
    return formatMap[format] || format;
  }

  /**
   * Parse tool-specific output for progress information
   */
  private parseProgressOutput(
    output: string,
    tool: string
  ): number | null {
    switch (tool) {
      case 'pdftocairo':
        // Example: "Page 5 of 10"
        const pdfMatch = output.match(/Page (\d+) of (\d+)/);
        if (pdfMatch) {
          return Number(pdfMatch[1]) / Number(pdfMatch[2]);
        }
        break;

      case 'pandoc':
        // Pandoc doesn't provide progress information
        return null;

      case 'ssconvert':
        // Example: "Converting sheet (2 of 5)"
        const sheetMatch = output.match(/Converting sheet \((\d+) of (\d+)\)/);
        if (sheetMatch) {
          return Number(sheetMatch[1]) / Number(sheetMatch[2]);
        }
        break;

      case 'soffice':
        // LibreOffice doesn't provide detailed progress
        if (output.includes('convert')) {
          return 0.5; // Rough estimate
        }
        break;
    }
    return null;
  }

  /**
   * Override validateConfig to add document-specific validation
   */
  public validateConfig(config: ConverterConfig): boolean {
    if (!super.validateConfig(config)) {
      return false;
    }

    const docConfig = config as DocumentConverterConfig;
    
    // Validate format compatibility
    const tool = this.getConversionTool(
      docConfig.inputFormat,
      docConfig.outputFormat
    );
    
    // Ensure the required conversion tool is available
    try {
      spawn(tool, ['--version']);
    } catch (err) {
      this.emitError(new Error(`Required conversion tool '${tool}' is not available`));
      return false;
    }

    return true;
  }
} 