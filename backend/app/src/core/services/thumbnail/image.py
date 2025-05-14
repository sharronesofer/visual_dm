from typing import Any


const SUPPORTED_IMAGE_TYPES = [
  'image/jpeg',
  'image/png',
  'image/webp',
  'image/gif',
  'image/tiff',
  'image/bmp',
]
class ImageThumbnailGenerator extends BaseThumbnailGenerator {
  supports(mimeType: str): bool {
    return SUPPORTED_IMAGE_TYPES.includes(mimeType)
  }
  async generate(input: str | Buffer, options?: ThumbnailOptions): Promise<ThumbnailResult> {
    this.validateInput(input)
    const opts = this.mergeOptions(options)
    let image = sharp(input as any)
    if (opts.width || opts.height) {
      image = image.resize(opts.width, opts.height, {
        fit: opts.maintainAspectRatio ? 'inside' : 'fill',
      })
    }
    if (opts.format) {
      image = image.toFormat(opts.format, { quality: opts.quality })
    }
    const buffer = await image.toBuffer()
    const metadata = await sharp(buffer).metadata()
    return {
      buffer,
      width: metadata.width || opts.width || 0,
      height: metadata.height || opts.height || 0,
      format: metadata.format || opts.format || 'jpeg',
      size: buffer.length,
    }
  }
} 