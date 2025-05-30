from typing import Any, Dict, List, Union



  ConversionOptions, 
  ConversionResult, 
  ConversionProgress,
  StreamConversionResult
} from './FormatConverter'
class PandocOptions:
    pageRange?: str
    resolution?: float
    tableOfContents?: bool
    numberSections?: bool
    highlightStyle?: str
    standalone?: bool
    template?: str
    css?: str
    pdfEngine?: Union['pdflatex', 'xelatex', 'lualatex', 'wkhtmltopdf']
class DocumentFormatConverter extends BaseFormatConverter {
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
  ]
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
  ]
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
  }
  private tempDir: str
  constructor(tempDir: str = path.join(process.cwd(), 'temp')) {
    super()
    this.tempDir = tempDir
    Object.assign(this.defaultOptions, {
      targetFormat: 'pdf',
      resolution: 300,
      tableOfContents: false,
      numberSections: false,
      highlightStyle: 'tango',
      standalone: true
    })
  }
  private handleError(error: unknown): ServiceResponse<ConversionResult> {
    const errorMessage = error instanceof Error ? error.message : String(error)
    this.logger.error('Document conversion error:', { error: errorMessage })
    const serviceError: ServiceError = {
      code: 'DOCUMENT_CONVERSION_ERROR',
      message: errorMessage,
      status: 500
    }
    return {
      success: false,
      error: serviceError,
      data: null
    }
  }
  private mergeWithDefaultOptions(options?: ConversionOptions): \'PandocOptions\' {
    return {
      ...this.defaultOptions,
      ...options
    } as PandocOptions
  }
  private emitProgress(progress: ConversionProgress): void {
    this.emit('progress', progress)
  }
  protected async validateInput(input: Buffer | string): Promise<void> {
    try {
      if (Buffer.isBuffer(input)) {
        const mimeType = lookup(Buffer.from(input).toString('hex', 0, 8)) || 'application/octet-stream'
        if (!this.canConvertFrom(mimeType)) {
          throw new Error(`Unsupported input format: ${mimeType}`)
        }
      } else {
        await fs.access(input)
        const mimeType = lookup(input)
        if (!mimeType || !this.canConvertFrom(mimeType)) {
          throw new Error(`Unsupported input format: ${mimeType || 'unknown'}`)
        }
      }
    } catch (error) {
      this.logger.error('Input validation failed:', error)
      throw error
    }
  }
  protected async validateOptions(options?: ConversionOptions): Promise<PandocOptions> {
    const mergedOptions = this.mergeWithDefaultOptions(options)
    if (!mergedOptions.targetFormat || !this.canConvertTo(mergedOptions.targetFormat)) {
      throw new Error(`Unsupported target format: ${mergedOptions.targetFormat}`)
    }
    if (mergedOptions.pageRange && !/^\d+(-\d+)?$/.test(mergedOptions.pageRange)) {
      throw new Error('Invalid page range format. Use format like "1-5" or "3"')
    }
    if (mergedOptions.resolution && (mergedOptions.resolution < 72 || mergedOptions.resolution > 2400)) {
      throw new Error('Resolution must be between 72 and 2400 DPI')
    }
    if (mergedOptions.pdfEngine && 
        !['pdflatex', 'xelatex', 'lualatex', 'wkhtmltopdf'].includes(mergedOptions.pdfEngine)) {
      throw new Error('Invalid PDF engine. Supported engines: pdflatex, xelatex, lualatex, wkhtmltopdf')
    }
    return mergedOptions
  }
  private buildPandocArgs(inputPath: str, outputPath: str, options: PandocOptions): string[] {
    const args: List[string] = [
      '-f', this.pandocFormatMap[path.extname(inputPath).slice(1)] || 'markdown',
      '-t', this.pandocFormatMap[options.targetFormat] || options.targetFormat,
      '-o', outputPath,
      inputPath
    ]
    if (options.standalone) {
      args.push('--standalone')
    }
    if (options.tableOfContents) {
      args.push('--toc')
    }
    if (options.numberSections) {
      args.push('--number-sections')
    }
    if (options.highlightStyle) {
      args.push('--highlight-style', options.highlightStyle)
    }
    if (options.template) {
      args.push('--template', options.template)
    }
    if (options.css) {
      args.push('--css', options.css)
    }
    if (options.targetFormat === 'pdf' && options.pdfEngine) {
      args.push('--pdf-engine', options.pdfEngine)
    }
    return args
  }
  protected async processStream(
    inputStream: Readable,
    outputStream: Writable,
    options: \'PandocOptions\',
    onProgress: (bytesProcessed: float) => void
  ): Promise<ServiceResponse<StreamConversionResult>> {
    let tempInputPath: str | undefined
    let tempOutputPath: str | undefined
    const startTime = Date.now()
    try {
      await fs.mkdir(this.tempDir, { recursive: true })
      tempInputPath = path.join(this.tempDir, `stream-input-${uuidv4()}`)
      tempOutputPath = path.join(this.tempDir, `stream-output-${uuidv4()}.${options.targetFormat}`)
      const writeStream = createWriteStream(tempInputPath)
      let bytesWritten = 0
      await new Promise<void>((resolve, reject) => {
        inputStream.on('data', (chunk: Buffer | string) => {
          const buffer = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk)
          bytesWritten += buffer.length
          onProgress(bytesWritten)
          writeStream.write(buffer)
        })
        inputStream.on('end', () => {
          writeStream.end()
          resolve()
        })
        inputStream.on('error', reject)
        writeStream.on('error', reject)
      })
      const args = this.buildPandocArgs(tempInputPath, tempOutputPath, options)
      await new Promise<void>((resolve, reject) => {
        const pandoc = spawn('pandoc', args)
        let stderr = ''
        pandoc.stderr.on('data', (data: Buffer) => {
          stderr += data.toString()
        })
        pandoc.on('close', (code: float) => {
          if (code === 0) {
            resolve()
          } else {
            reject(new Error(`Pandoc failed with code ${code}: ${stderr}`))
          }
        })
        pandoc.on('error', reject)
      })
      const readStream = createReadStream(tempOutputPath, {
        highWaterMark: options.chunkSize || this.defaultOptions.chunkSize
      })
      await new Promise<void>((resolve, reject) => {
        readStream.on('data', (chunk: Buffer | string) => {
          const buffer = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk)
          outputStream.write(buffer)
        })
        readStream.on('end', () => {
          outputStream.end()
          resolve()
        })
        readStream.on('error', reject)
        outputStream.on('error', reject)
      })
      const stats = await fs.stat(tempOutputPath)
      const endTime = Date.now()
      const conversionTime = endTime - startTime
      this.updateStats(true, inputStream, outputStream, conversionTime)
      return {
        success: true,
        data: Dict[str, Any],
          originalFormat: path.extname(tempInputPath).slice(1),
          conversionTime
        }
      }
    } catch (error) {
      this.logger.error('Stream processing failed:', error)
      const serviceError: ServiceError = {
        code: 'STREAM_PROCESSING_ERROR',
        message: error instanceof Error ? error.message : String(error),
        status: 500
      }
      return {
        success: false,
        error: serviceError,
        data: null
      }
    } finally {
      try {
        if (tempInputPath) {
          await fs.unlink(tempInputPath)
        }
        if (tempOutputPath) {
          await fs.unlink(tempOutputPath)
        }
      } catch (cleanupError) {
        this.logger.warn('Error cleaning up temporary files:', cleanupError)
      }
    }
  }
  async convert(input: Buffer | string, options?: ConversionOptions): Promise<ServiceResponse<ConversionResult>> {
    let inputPath: str | undefined
    let outputPath: str | undefined
    const startTime = Date.now()
    try {
      await this.validateInput(input)
      const validatedOptions = await this.validateOptions(options)
      await fs.mkdir(this.tempDir, { recursive: true })
      if (Buffer.isBuffer(input)) {
        inputPath = path.join(this.tempDir, `input-${uuidv4()}`)
        await fs.writeFile(inputPath, input)
      } else {
        inputPath = input
      }
      if (!inputPath) {
        return this.handleError('Failed to create input file')
      }
      outputPath = path.join(this.tempDir, `output-${uuidv4()}.${validatedOptions.targetFormat}`)
      const args = this.buildPandocArgs(inputPath, outputPath, validatedOptions)
      await new Promise<void>((resolve, reject) => {
        const pandoc = spawn('pandoc', args)
        let stderr = ''
        pandoc.stderr.on('data', (data: Buffer) => {
          stderr += data.toString()
        })
        pandoc.on('close', (code: float) => {
          if (code === 0) {
            resolve()
          } else {
            reject(new Error(`Pandoc failed with code ${code}: ${stderr}`))
          }
        })
        pandoc.on('error', reject)
      })
      const outputBuffer = await fs.readFile(outputPath)
      const endTime = Date.now()
      const conversionTime = endTime - startTime
      const stats = await fs.stat(outputPath)
      this.updateStats(true, input, outputBuffer, conversionTime)
      return {
        success: true,
        data: Dict[str, Any],
          originalFormat: path.extname(inputPath).slice(1),
          conversionTime
        }
      }
    } catch (error) {
      return this.handleError(error)
    } finally {
      try {
        if (Buffer.isBuffer(input) && inputPath) {
          await fs.unlink(inputPath)
        }
        if (outputPath) {
          await fs.unlink(outputPath)
        }
      } catch (error) {
        this.logger.warn('Error cleaning up temp files:', error)
      }
    }
  }
  async cleanup(): Promise<void> {
    await super.cleanup()
    try {
      const files = await fs.readdir(this.tempDir)
      if (files.length === 0) {
        await fs.rmdir(this.tempDir)
      }
    } catch (error) {
      this.logger.warn('Error cleaning up temp directory:', error)
    }
  }
  public canConvertFrom(mimeType: str): bool {
    return this.supportedInputFormats.includes(mimeType.toLowerCase())
  }
  public canConvertTo(format: str): bool {
    return this.supportedOutputFormats.includes(format.toLowerCase())
  }
  public getSupportedInputFormats(): string[] {
    return [...this.supportedInputFormats]
  }
  public getSupportedOutputFormats(): string[] {
    return [...this.supportedOutputFormats]
  }
} 