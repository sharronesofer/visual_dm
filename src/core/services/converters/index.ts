import { FormatConverterFactory } from './FormatConverterFactory';
import { ImageFormatConverter } from './ImageFormatConverter';
import { VideoFormatConverter } from './VideoFormatConverter';
import { AudioFormatConverter } from './AudioFormatConverter';
import { DocumentFormatConverter } from './DocumentFormatConverter';
import { ConversionOptions, ConversionResult, StreamConversionResult } from './FormatConverter';
import { ServiceResponse as BaseServiceResponse } from '../base/types';
import { ServiceError as BaseServiceError } from '../base/types';
import { Readable, Writable } from 'stream';

/**
 * Unified convert function for all media types.
 * @param input Buffer or file path
 * @param options Conversion options (must include targetFormat)
 * @returns ServiceResponse<ConversionResult>
 */
export async function convert(
  input: Buffer | string,
  options: ConversionOptions
): Promise<BaseServiceResponse<ConversionResult>> {
  const factory = FormatConverterFactory.getInstance();
  const converter = factory.getConverter(input);
  const result = await converter.convert(input, options);
  return {
    success: result.success,
    data: result.data ?? null,
    error: result.error as BaseServiceError | undefined
  };
}

/**
 * Unified convertStream function for all media types.
 * @param inputStream Readable stream
 * @param outputStream Writable stream
 * @param inputFormatOrPath Buffer or file path (for type detection)
 * @param options Conversion options (must include targetFormat)
 * @returns ServiceResponse<StreamConversionResult>
 */
export async function convertStream(
  inputStream: Readable,
  outputStream: Writable,
  inputFormatOrPath: Buffer | string,
  options: ConversionOptions
): Promise<BaseServiceResponse<StreamConversionResult>> {
  const factory = FormatConverterFactory.getInstance();
  const converter = factory.getConverter(inputFormatOrPath);
  const result = await converter.convertStream(inputStream, outputStream, options);
  let normalizedData: StreamConversionResult | null = null;
  if (result.data) {
    // If metadata is missing createdAt, add it; ensure format is always a string and createdAt is a Date
    let createdAt: Date;
    const rawCreatedAt = result.data.metadata.createdAt;
    if (rawCreatedAt instanceof Date) {
      createdAt = rawCreatedAt;
    } else if (typeof rawCreatedAt === 'string' || typeof rawCreatedAt === 'number') {
      createdAt = new Date(rawCreatedAt);
    } else {
      createdAt = new Date();
    }
    const metadata = {
      ...result.data.metadata,
      format: typeof result.data.metadata.format === 'string' ? result.data.metadata.format : '',
      createdAt
    };
    normalizedData = {
      ...result.data,
      metadata
    };
  }
  return {
    success: result.success,
    data: normalizedData,
    error: result.error as BaseServiceError | undefined
  };
}

export {
  FormatConverterFactory,
  ImageFormatConverter,
  VideoFormatConverter,
  AudioFormatConverter,
  DocumentFormatConverter
}; 