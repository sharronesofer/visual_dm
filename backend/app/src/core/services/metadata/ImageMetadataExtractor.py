from typing import Any


const ExifReader = require('exifreader')
  MediaMetadata,
  MetadataExtractionOptions,
  MetadataExtractionResult
} from './MetadataExtractor'
declare module 'exifreader' {
  class ExifTag:
    value: Any
    description?: str
  class ExifTags:
    [key: str]: \'ExifTag\'
  function load(buffer: Buffer): Promise<ExifTags>
}
class ImageMetadataExtractor extends BaseMetadataExtractor {
  private readonly supportedTypes = [
    'image/jpeg',
    'image/png',
    'image/webp',
    'image/tiff',
    'image/gif',
    'image/avif'
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
      const sharpMetadata = await sharp(buffer).metadata()
      let exifData: Record<string, any> = {}
      let iptcData: Record<string, any> = {}
      let xmpData: Record<string, any> = {}
      if (options.extractExif || options.extractIptc || options.extractXmp) {
        const tags = await ExifReader.load(buffer)
        if (options.extractExif) {
          exifData = this.processExifTags(tags)
        }
        if (options.extractIptc) {
          iptcData = this.processIptcTags(tags)
        }
        if (options.extractXmp) {
          xmpData = this.processXmpTags(tags)
        }
      }
      const metadata: MediaMetadata = {
        format: sharpMetadata.format || '',
        mimeType: this.getMimeType(input),
        size: buffer.length,
        width: sharpMetadata.width,
        height: sharpMetadata.height,
        colorSpace: sharpMetadata.space,
        hasAlpha: sharpMetadata.hasAlpha,
        orientation: sharpMetadata.orientation,
        dpi: sharpMetadata.density,
        createdAt: new Date(),
        modifiedAt: new Date(),
        exif: exifData,
        iptc: iptcData,
        xmp: xmpData
      }
      if (options.computeColorProfile) {
        metadata.colorProfile = await this.computeColorProfile(buffer)
      }
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
  private processExifTags(tags: Record<string, any>): Record<string, any> {
    const exif: Record<string, any> = {}
    const commonTags = [
      'Make', 'Model', 'Software', 'DateTime', 'Artist',
      'Copyright', 'ExposureTime', 'FNumber', 'ISO', 'FocalLength',
      'GPSLatitude', 'GPSLongitude'
    ]
    for (const tag of commonTags) {
      if (tags[tag] && tags[tag].value !== undefined) {
        exif[tag] = tags[tag].value
      }
    }
    return exif
  }
  private processIptcTags(tags: Record<string, any>): Record<string, any> {
    const iptc: Record<string, any> = {}
    const iptcTags = [
      'ObjectName', 'Keywords', 'Caption', 'CaptionWriter',
      'Headline', 'SpecialInstructions', 'Category', 'ByLine',
      'ByLineTitle', 'Credit', 'Source', 'CopyrightNotice',
      'City', 'Country'
    ]
    for (const tag of iptcTags) {
      if (tags[tag] && tags[tag].value !== undefined) {
        iptc[tag] = tags[tag].value
      }
    }
    return iptc
  }
  private processXmpTags(tags: Record<string, any>): Record<string, any> {
    const xmp: Record<string, any> = {}
    const xmpTags = [
      'Creator', 'Description', 'Rights', 'Title',
      'Rating', 'Label', 'Subject'
    ]
    for (const tag of xmpTags) {
      if (tags[tag] && tags[tag].value !== undefined) {
        xmp[tag] = tags[tag].value
      }
    }
    return xmp
  }
  private async computeColorProfile(buffer: Buffer): Promise<string> {
    try {
      const image = sharp(buffer)
      const stats = await image.stats()
      const channels = stats.channels
      const profile = {
        isRGB: channels.length === 3,
        isRGBA: channels.length === 4,
        isGreyscale: channels.length === 1,
        meanIntensity: channels.map(c => c.mean).reduce((a, b) => a + b) / channels.length
      }
      return JSON.stringify(profile)
    } catch (error) {
      this.logger.warn('Failed to compute color profile:', error)
      return 'unknown'
    }
  }
} 