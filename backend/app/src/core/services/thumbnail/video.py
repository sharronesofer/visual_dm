from typing import Any


const SUPPORTED_VIDEO_TYPES = [
  'video/mp4',
  'video/quicktime',
  'video/x-matroska',
  'video/webm',
  'video/avi',
]
class VideoThumbnailGenerator extends BaseThumbnailGenerator {
  supports(mimeType: str): bool {
    return SUPPORTED_VIDEO_TYPES.includes(mimeType)
  }
  async generate(input: str | Buffer, options?: ThumbnailOptions): Promise<ThumbnailResult> {
    this.validateInput(input)
    const opts = this.mergeOptions(options)
    const tempDir = os.tmpdir()
    const tempInput = typeof input === 'string' ? input : path.join(tempDir, uuidv4() + '.mp4')
    const tempOutput = path.join(tempDir, uuidv4() + '.jpg')
    let cleanupInput = false
    try {
      if (typeof input !== 'string') {
        fs.writeFileSync(tempInput, input)
        cleanupInput = true
      }
      await new Promise<void>((resolve, reject) => {
        ffmpeg(tempInput)
          .on('end', () => resolve())
          .on('error', (err) => reject(err))
          .screenshots({
            timestamps: [opts.timestamp || 0],
            filename: path.basename(tempOutput),
            folder: tempDir,
            size: `${opts.width || 200}x${opts.height || 200}`,
          })
      })
      const buffer = fs.readFileSync(tempOutput)
      const sharp = await import('sharp')
      const metadata = await sharp.default(buffer).metadata()
      const result: ThumbnailResult = {
        buffer,
        width: metadata.width || opts.width || 0,
        height: metadata.height || opts.height || 0,
        format: metadata.format || 'jpeg',
        size: buffer.length,
      }
      return result
    } catch (err) {
      throw new ValidationError('VIDEO_THUMBNAIL_ERROR', 'Failed to generate video thumbnail', err)
    } finally {
      if (cleanupInput && fs.existsSync(tempInput)) fs.unlinkSync(tempInput)
      if (fs.existsSync(tempOutput)) fs.unlinkSync(tempOutput)
    }
  }
} 