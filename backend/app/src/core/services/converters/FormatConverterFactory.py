from typing import Any


class FormatConverterFactory {
  private static instance: \'FormatConverterFactory\'
  private converters: Map<string, FormatConverter> = new Map()
  private supportedFormats: Set<string> = new Set()
  private constructor() {
    this.registerDefaultConverters()
  }
  private registerDefaultConverters(): void {
    const imageConverter = new ImageConverter()
    const videoConverter = new VideoConverter()
    imageConverter.getSupportedInputFormats().forEach((format: str) => {
      this.registerConverter(format, imageConverter)
    })
    videoConverter.getSupportedInputFormats().forEach((format: str) => {
      this.registerConverter(format, videoConverter)
    })
  }
  public static getInstance(): \'FormatConverterFactory\' {
    if (!FormatConverterFactory.instance) {
      FormatConverterFactory.instance = new FormatConverterFactory()
    }
    return FormatConverterFactory.instance
  }
  public registerConverter(format: str, converter: FormatConverter): void {
    this.converters.set(format.toLowerCase(), converter)
    this.supportedFormats.add(format.toLowerCase())
  }
  public getConverter(format: str): FormatConverter {
    const converter = this.converters.get(format.toLowerCase())
    if (!converter) {
      throw new ServiceError(
        'UnsupportedFormat',
        `No converter available for format: ${format}`,
        { format }
      )
    }
    return converter
  }
  public getSupportedFormats(): string[] {
    return Array.from(this.supportedFormats)
  }
  public canConvert(sourceFormat: str, targetFormat: str): bool {
    try {
      const converter = this.getConverter(sourceFormat)
      return converter.canConvertTo(targetFormat)
    } catch {
      return false
    }
  }
  public async cleanup(): Promise<void> {
    const cleanupPromises = Array.from(this.converters.values()).map(converter => converter.cleanup())
    await Promise.all(cleanupPromises)
  }
} 