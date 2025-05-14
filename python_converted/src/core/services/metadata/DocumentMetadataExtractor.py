from typing import Any, Dict


  MediaMetadata,
  MetadataExtractionOptions,
  MetadataExtractionResult
} from './MetadataExtractor'
class DocumentMetadataExtractor extends BaseMetadataExtractor {
  private readonly supportedTypes = [
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/msword',
    'application/vnd.ms-excel',
    'text/plain',
    'text/markdown',
    'text/csv'
  ]
  public canHandle(mimeType: str): bool {
    return this.supportedTypes.includes(mimeType.toLowerCase())
  }
  public getSupportedTypes(): string[] {
    return [...this.supportedTypes]
  }
  protected async processExtraction(
    input: Buffer | string,
    options: MetadataExtractionOptions
  ): Promise<ServiceResponse<MetadataExtractionResult>> {
    try {
      await this.validateInput(input)
      const buffer = Buffer.isBuffer(input) ? input : await fs.readFile(input)
      const mimeType = this.getMimeType(input)
      const metadata = await this.extractMetadataByType(buffer, mimeType)
      const result: MetadataExtractionResult = {
        metadata,
        cached: false,
        extractionTime: 0 
      }
      return {
        success: true,
        data: result
      }
    } catch (error) {
      return this.handleError(error)
    }
  }
  private async extractMetadataByType(buffer: Buffer, mimeType: str): Promise<MediaMetadata> {
    let metadata: MediaMetadata = {
      format: this.getFormatFromMimeType(mimeType),
      mimeType,
      size: buffer.length,
      createdAt: new Date(),
      modifiedAt: new Date(),
      custom: {}
    }
    switch (mimeType) {
      case 'application/pdf':
        return await this.extractPdfMetadata(buffer, metadata)
      case 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
      case 'application/msword':
        return await this.extractDocxMetadata(buffer, metadata)
      case 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
      case 'application/vnd.ms-excel':
        return await this.extractExcelMetadata(buffer, metadata)
      case 'text/plain':
      case 'text/markdown':
      case 'text/csv':
        return await this.extractTextMetadata(buffer, metadata)
      default:
        return metadata
    }
  }
  private async extractPdfMetadata(buffer: Buffer, baseMetadata: MediaMetadata): Promise<MediaMetadata> {
    const data = await pdf(buffer)
    return {
      ...baseMetadata,
      custom: Dict[str, Any]
    }
  }
  private async extractDocxMetadata(buffer: Buffer, baseMetadata: MediaMetadata): Promise<MediaMetadata> {
    const doc = new docx.Document(buffer)
    const props = doc.getProperties()
    const sections = doc.getNumberOfSections()
    const paragraphs = doc.getParagraphs()
    return {
      ...baseMetadata,
      custom: Dict[str, Any]
    }
  }
  private async extractExcelMetadata(buffer: Buffer, baseMetadata: MediaMetadata): Promise<MediaMetadata> {
    const workbook = xlsx.read(buffer, { type: 'buffer' })
    const sheetNames = workbook.SheetNames
    const props = workbook.Props || {}
    return {
      ...baseMetadata,
      custom: Dict[str, Any]
    }
  }
  private async extractTextMetadata(buffer: Buffer, baseMetadata: MediaMetadata): Promise<MediaMetadata> {
    const text = buffer.toString('utf-8')
    const lines = text.split('\n')
    const words = text.split(/\s+/)
    return {
      ...baseMetadata,
      custom: Dict[str, Any]
    }
  }
  private countWords(paragraphs: docx.Paragraph[]): float {
    return paragraphs.reduce((count, para) => {
      const text = para.text
      return count + text.split(/\s+/).length
    }, 0)
  }
  private countCharacters(paragraphs: docx.Paragraph[]): float {
    return paragraphs.reduce((count, para) => {
      return count + para.text.length
    }, 0)
  }
  private countExcelCells(workbook: xlsx.WorkBook): float {
    let totalCells = 0
    workbook.SheetNames.forEach(sheetName => {
      const sheet = workbook.Sheets[sheetName]
      const range = xlsx.utils.decode_range(sheet['!ref'] || 'A1')
      totalCells += (range.e.r - range.s.r + 1) * (range.e.c - range.s.c + 1)
    })
    return totalCells
  }
  private getFormatFromMimeType(mimeType: str): str {
    const mimeToFormat: Dict[str, Any] = {
      'application/pdf': 'pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
      'application/msword': 'doc',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
      'application/vnd.ms-excel': 'xls',
      'text/plain': 'txt',
      'text/markdown': 'md',
      'text/csv': 'csv'
    }
    return mimeToFormat[mimeType] || mimeType.split('/').pop() || ''
  }
} 