import { MetadataExtractor } from './MetadataExtractor';
import { ServiceError } from '../base/types';

export class MetadataExtractorFactory {
  private static instance: MetadataExtractorFactory;
  private extractors: Map<string, MetadataExtractor> = new Map();
  private supportedFormats: Set<string> = new Set(['jpeg', 'png', 'gif', 'webp', 'mp4', 'webm', 'mov', 'mp3', 'wav']);

  private constructor() {}

  public static getInstance(): MetadataExtractorFactory {
    if (!MetadataExtractorFactory.instance) {
      MetadataExtractorFactory.instance = new MetadataExtractorFactory();
    }
    return MetadataExtractorFactory.instance;
  }

  public registerExtractor(type: string, extractor: MetadataExtractor): void {
    this.extractors.set(type.toLowerCase(), extractor);
    this.supportedFormats.add(type.toLowerCase());
  }

  public getExtractor(type: string): MetadataExtractor {
    const extractor = this.extractors.get(type.toLowerCase());
    if (!extractor) {
      throw new ServiceError(
        'UnsupportedFormat',
        `Metadata extractor not found for type: ${type}`,
        { type }
      );
    }
    return extractor;
  }

  public getSupportedFormats(): string[] {
    return Array.from(this.supportedFormats);
  }
} 