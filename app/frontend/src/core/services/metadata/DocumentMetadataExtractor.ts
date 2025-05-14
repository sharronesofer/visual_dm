import { promises as fs } from 'fs';
import * as pdf from 'pdf-parse';
import * as docx from 'docx';
import * as xlsx from 'xlsx';
import { BaseMetadataExtractor } from './BaseMetadataExtractor';
import {
  MediaMetadata,
  MetadataExtractionOptions,
  MetadataExtractionResult
} from './MetadataExtractor';
import { ServiceResponse } from '../base/types';

export class DocumentMetadataExtractor extends BaseMetadataExtractor {
  private readonly supportedTypes = [
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/msword',
    'application/vnd.ms-excel',
    'text/plain',
    'text/markdown',
    'text/csv'
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

      // If input is a string (file path), read it into a buffer
      const buffer = Buffer.isBuffer(input) ? input : await fs.readFile(input);
      const mimeType = this.getMimeType(input);

      // Extract metadata based on document type
      const metadata = await this.extractMetadataByType(buffer, mimeType);

      const result: MetadataExtractionResult = {
        metadata,
        cached: false,
        extractionTime: 0 // Will be set by base class
      };

      return {
        success: true,
        data: result
      };
    } catch (error) {
      return this.handleError(error);
    }
  }

  private async extractMetadataByType(buffer: Buffer, mimeType: string): Promise<MediaMetadata> {
    let metadata: MediaMetadata = {
      format: this.getFormatFromMimeType(mimeType),
      mimeType,
      size: buffer.length,
      createdAt: new Date(),
      modifiedAt: new Date(),
      custom: {}
    };

    switch (mimeType) {
      case 'application/pdf':
        return await this.extractPdfMetadata(buffer, metadata);
      case 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
      case 'application/msword':
        return await this.extractDocxMetadata(buffer, metadata);
      case 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
      case 'application/vnd.ms-excel':
        return await this.extractExcelMetadata(buffer, metadata);
      case 'text/plain':
      case 'text/markdown':
      case 'text/csv':
        return await this.extractTextMetadata(buffer, metadata);
      default:
        return metadata;
    }
  }

  private async extractPdfMetadata(buffer: Buffer, baseMetadata: MediaMetadata): Promise<MediaMetadata> {
    const data = await pdf(buffer);
    return {
      ...baseMetadata,
      custom: {
        pageCount: data.numpages,
        title: data.info?.Title,
        author: data.info?.Author,
        subject: data.info?.Subject,
        keywords: data.info?.Keywords,
        creator: data.info?.Creator,
        producer: data.info?.Producer,
        creationDate: data.info?.CreationDate,
        modificationDate: data.info?.ModDate,
        isEncrypted: data.info?.IsEncrypted,
        wordCount: data.text.split(/\s+/).length,
        characterCount: data.text.length
      }
    };
  }

  private async extractDocxMetadata(buffer: Buffer, baseMetadata: MediaMetadata): Promise<MediaMetadata> {
    const doc = new docx.Document(buffer);
    const props = doc.getProperties();
    const sections = doc.getNumberOfSections();
    const paragraphs = doc.getParagraphs();

    return {
      ...baseMetadata,
      custom: {
        title: props.title,
        author: props.creator,
        subject: props.subject,
        keywords: props.keywords,
        description: props.description,
        lastModifiedBy: props.lastModifiedBy,
        revision: props.revision,
        createdAt: props.created,
        modifiedAt: props.modified,
        sectionCount: sections,
        paragraphCount: paragraphs.length,
        wordCount: this.countWords(paragraphs),
        characterCount: this.countCharacters(paragraphs)
      }
    };
  }

  private async extractExcelMetadata(buffer: Buffer, baseMetadata: MediaMetadata): Promise<MediaMetadata> {
    const workbook = xlsx.read(buffer, { type: 'buffer' });
    const sheetNames = workbook.SheetNames;
    const props = workbook.Props || {};

    return {
      ...baseMetadata,
      custom: {
        title: props.Title,
        author: props.Author,
        subject: props.Subject,
        keywords: props.Keywords,
        category: props.Category,
        company: props.Company,
        manager: props.Manager,
        createdAt: props.CreatedDate,
        modifiedAt: props.ModifiedDate,
        sheetCount: sheetNames.length,
        sheetNames,
        totalCells: this.countExcelCells(workbook)
      }
    };
  }

  private async extractTextMetadata(buffer: Buffer, baseMetadata: MediaMetadata): Promise<MediaMetadata> {
    const text = buffer.toString('utf-8');
    const lines = text.split('\n');
    const words = text.split(/\s+/);

    return {
      ...baseMetadata,
      custom: {
        lineCount: lines.length,
        wordCount: words.length,
        characterCount: text.length,
        averageLineLength: text.length / lines.length,
        averageWordLength: text.length / words.length
      }
    };
  }

  private countWords(paragraphs: docx.Paragraph[]): number {
    return paragraphs.reduce((count, para) => {
      const text = para.text;
      return count + text.split(/\s+/).length;
    }, 0);
  }

  private countCharacters(paragraphs: docx.Paragraph[]): number {
    return paragraphs.reduce((count, para) => {
      return count + para.text.length;
    }, 0);
  }

  private countExcelCells(workbook: xlsx.WorkBook): number {
    let totalCells = 0;
    workbook.SheetNames.forEach(sheetName => {
      const sheet = workbook.Sheets[sheetName];
      const range = xlsx.utils.decode_range(sheet['!ref'] || 'A1');
      totalCells += (range.e.r - range.s.r + 1) * (range.e.c - range.s.c + 1);
    });
    return totalCells;
  }

  private getFormatFromMimeType(mimeType: string): string {
    const mimeToFormat: { [key: string]: string } = {
      'application/pdf': 'pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
      'application/msword': 'doc',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
      'application/vnd.ms-excel': 'xls',
      'text/plain': 'txt',
      'text/markdown': 'md',
      'text/csv': 'csv'
    };
    return mimeToFormat[mimeType] || mimeType.split('/').pop() || '';
  }
} 