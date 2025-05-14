from typing import Any, Dict


class ImageProcessor {
  async process(buffer: Buffer, config: PostProcessingConfig): Promise<Buffer> {
    let image = sharp(buffer)
    if (config.resize) {
      image = image.resize(config.resize.width, config.resize.height, {
        fit: 'contain',
        background: Dict[str, Any]
      })
    }
    if (config.adjustments) {
      const { brightness, contrast, saturation, sepia } = config.adjustments
      image = image.modulate({
        brightness: brightness,
        saturation: saturation
      })
      if (typeof contrast === 'number') {
        image = image.linear(contrast, -(128 * (contrast - 1)))
      }
      if (typeof sepia === 'number' && sepia > 0) {
        image = image.tint({ r: 112, g: 66, b: 20 })
          .modulate({ brightness: 1 - (sepia * 0.2) })
      }
    }
    if (config.removeBg) {
      image = image.threshold(128)
    }
    if (config.format === 'webp') {
      image = image.webp({ quality: config.quality || 90 })
    } else if (config.format === 'png') {
      image = image.png({ quality: config.quality || 90 })
    }
    return image.toBuffer()
  }
  async createThumbnail(buffer: Buffer, size = 256): Promise<Buffer> {
    return sharp(buffer)
      .resize(size, size, {
        fit: 'inside',
        withoutEnlargement: true
      })
      .webp({ quality: 80 })
      .toBuffer()
  }
} 