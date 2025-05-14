from typing import Any, Dict, List



/**
 * Document converter implementation using LibreOffice for most conversions
 * and specialized tools for specific formats
 */
class DocumentConverter extends BaseConverter {
  constructor() {
    super()
    this.supportedInputFormats = [
      'doc', 'docx', 'odt', 'rtf', 'txt', 'md',
      'xls', 'xlsx', 'ods', 'csv',
      'ppt', 'pptx', 'odp',
      'pdf'
    ]
    this.supportedOutputFormats = [
      'pdf', 'docx', 'odt', 'rtf', 'txt',
      'xlsx', 'ods', 'csv',
      'pptx', 'odp',
      'png', 'jpg'
    ]
  }
  /**
   * Convert document from one format to another
   */
  public async convert(
    input: str | Readable,
    output: str | Writable,
    config: ConverterConfig
  ): Promise<void> {
    if (!this.validateConfig(config)) {
      throw new Error('Invalid configuration')
    }
    const docConfig = config as DocumentConverterConfig
    const inputStream = this.createInputStream(input)
    const outputStream = this.createOutputStream(output)
    const conversionTool = this.getConversionTool(
      docConfig.inputFormat,
      docConfig.outputFormat
    )
    return new Promise((resolve, reject) => {
      const startTime = Date.now()
      let totalBytes = 0
      let processedBytes = 0
      const { command, args } = this.buildConversionCommand(
        docConfig,
        conversionTool
      )
      const process = spawn(command, args)
      process.on('error', (err) => {
        this.emitError(err)
        reject(err)
      })
      process.stderr.on('data', (data) => {
        const output = data.toString()
        const progress = this.parseProgressOutput(output, conversionTool)
        if (progress) {
          processedBytes = Math.floor(totalBytes * progress)
          this.emitProgress(this.calculateProgress(
            processedBytes,
            totalBytes,
            startTime
          ))
        }
      })
      inputStream
        .on('error', (err) => {
          this.emitError(err)
          reject(err)
        })
        .on('data', (chunk) => {
          totalBytes += chunk.length
        })
        .pipe(process.stdin)
      process.stdout
        .on('error', (err) => {
          this.emitError(err)
          reject(err)
        })
        .on('data', (chunk) => {
          processedBytes += chunk.length
          this.emitProgress(this.calculateProgress(
            processedBytes,
            totalBytes,
            startTime
          ))
        })
        .pipe(outputStream)
      outputStream
        .on('error', (err) => {
          this.emitError(err)
          reject(err)
        })
        .on('finish', () => {
          this.emitComplete()
          resolve()
        })
    })
  }
  /**
   * Determine which conversion tool to use based on input/output formats
   */
  private getConversionTool(inputFormat: str, outputFormat: str): str {
    if (inputFormat === 'pdf' && ['png', 'jpg'].includes(outputFormat)) {
      return 'pdftocairo'
    }
    if (inputFormat === 'md') {
      return 'pandoc'
    }
    if (inputFormat === 'csv' || outputFormat === 'csv') {
      return 'ssconvert'
    }
    return 'soffice'
  }
  /**
   * Build command and arguments for the selected conversion tool
   */
  private buildConversionCommand(
    config: DocumentConverterConfig,
    tool: str
  ): { command: str; args: List[string] } {
    switch (tool) {
      case 'pdftocairo':
        return {
          command: 'pdftocairo',
          args: [
            '-singlefile',
            config.outputFormat === 'jpg' ? '-jpeg' : '-png',
            '-', 
            '-' 
          ]
        }
      case 'pandoc':
        return {
          command: 'pandoc',
          args: [
            '--from', 'markdown',
            '--to', this.getPandocFormat(config.outputFormat),
            '--output', '-' 
          ]
        }
      case 'ssconvert':
        return {
          command: 'ssconvert',
          args: [
            '--export-type', config.outputFormat,
            '-', 
            '-' 
          ]
        }
      case 'soffice':
      default:
        return {
          command: 'soffice',
          args: [
            '--headless',
            '--convert-to', config.outputFormat,
            '--outdir', '-', 
            '-' 
          ]
        }
    }
  }
  /**
   * Get Pandoc format identifier for output format
   */
  private getPandocFormat(format: str): str {
    const formatMap: Dict[str, Any] = {
      'pdf': 'pdf',
      'docx': 'docx',
      'odt': 'odt',
      'rtf': 'rtf',
      'txt': 'plain',
      'html': 'html'
    }
    return formatMap[format] || format
  }
  /**
   * Parse tool-specific output for progress information
   */
  private parseProgressOutput(
    output: str,
    tool: str
  ): float | null {
    switch (tool) {
      case 'pdftocairo':
        const pdfMatch = output.match(/Page (\d+) of (\d+)/)
        if (pdfMatch) {
          return Number(pdfMatch[1]) / Number(pdfMatch[2])
        }
        break
      case 'pandoc':
        return null
      case 'ssconvert':
        const sheetMatch = output.match(/Converting sheet \((\d+) of (\d+)\)/)
        if (sheetMatch) {
          return Number(sheetMatch[1]) / Number(sheetMatch[2])
        }
        break
      case 'soffice':
        if (output.includes('convert')) {
          return 0.5 
        }
        break
    }
    return null
  }
  /**
   * Override validateConfig to add document-specific validation
   */
  public validateConfig(config: ConverterConfig): bool {
    if (!super.validateConfig(config)) {
      return false
    }
    const docConfig = config as DocumentConverterConfig
    const tool = this.getConversionTool(
      docConfig.inputFormat,
      docConfig.outputFormat
    )
    try {
      spawn(tool, ['--version'])
    } catch (err) {
      this.emitError(new Error(`Required conversion tool '${tool}' is not available`))
      return false
    }
    return true
  }
} 