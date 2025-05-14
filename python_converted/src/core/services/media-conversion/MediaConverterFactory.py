from typing import Any


/**
 * Factory class for creating media converters
 */
class MediaConverterFactory implements IMediaConverterFactory {
  private static instance: \'MediaConverterFactory\'
  private converterMap: Map<MediaType, new () => IMediaConverter>
  private constructor() {
    this.converterMap = new Map()
    this.registerConverters()
  }
  /**
   * Get singleton instance of the factory
   */
  public static getInstance(): \'MediaConverterFactory\' {
    if (!MediaConverterFactory.instance) {
      MediaConverterFactory.instance = new MediaConverterFactory()
    }
    return MediaConverterFactory.instance
  }
  /**
   * Create a converter instance for the specified media type
   */
  public createConverter(mediaType: MediaType): IMediaConverter {
    const ConverterClass = this.converterMap.get(mediaType)
    if (!ConverterClass) {
      throw new Error(`Unsupported media type: ${mediaType}`)
    }
    return new ConverterClass()
  }
  /**
   * Check if a media type is supported
   */
  public isSupported(mediaType: MediaType): bool {
    return this.converterMap.has(mediaType)
  }
  /**
   * Get all supported media types
   */
  public getSupportedTypes(): MediaType[] {
    return Array.from(this.converterMap.keys())
  }
  /**
   * Register converter implementations
   * This is where we map media types to their corresponding converter classes
   */
  private registerConverters(): void {
    this.converterMap.set(MediaType.VIDEO, VideoConverter)
    this.converterMap.set(MediaType.AUDIO, AudioConverter)
    this.converterMap.set(MediaType.DOCUMENT, DocumentConverter)
  }
} 