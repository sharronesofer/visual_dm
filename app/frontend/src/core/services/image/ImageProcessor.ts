import sharp from 'sharp';
import { PostProcessingConfig } from '../../generators/medieval-assets/types';

export class ImageProcessor {
  async process(buffer: Buffer, config: PostProcessingConfig): Promise<Buffer> {
    let image = sharp(buffer);

    // Apply resizing if specified
    if (config.resize) {
      image = image.resize(config.resize.width, config.resize.height, {
        fit: 'contain',
        background: { r: 0, g: 0, b: 0, alpha: 0 }
      });
    }

    // Apply adjustments if specified
    if (config.adjustments) {
      const { brightness, contrast, saturation, sepia } = config.adjustments;
      
      // Apply brightness and saturation together
      image = image.modulate({
        brightness: brightness,
        saturation: saturation
      });
      
      // Apply contrast using linear adjustment
      if (typeof contrast === 'number') {
        image = image.linear(contrast, -(128 * (contrast - 1)));
      }

      // Apply sepia effect
      if (typeof sepia === 'number' && sepia > 0) {
        image = image.tint({ r: 112, g: 66, b: 20 })
          .modulate({ brightness: 1 - (sepia * 0.2) });
      }
    }

    // Remove background using threshold
    if (config.removeBg) {
      image = image.threshold(128);
    }

    // Convert to specified format
    if (config.format === 'webp') {
      image = image.webp({ quality: config.quality || 90 });
    } else if (config.format === 'png') {
      image = image.png({ quality: config.quality || 90 });
    }

    return image.toBuffer();
  }

  async createThumbnail(buffer: Buffer, size = 256): Promise<Buffer> {
    return sharp(buffer)
      .resize(size, size, {
        fit: 'inside',
        withoutEnlargement: true
      })
      .webp({ quality: 80 })
      .toBuffer();
  }
} 