from typing import Any, Dict



const SUPPORTED_AUDIO_TYPES = [
  'audio/mpeg',
  'audio/wav',
  'audio/x-wav',
  'audio/mp3',
  'audio/ogg',
  'audio/flac',
  'audio/aac',
]
class AudioThumbnailGenerator extends BaseThumbnailGenerator {
  supports(mimeType: str): bool {
    return SUPPORTED_AUDIO_TYPES.includes(mimeType)
  }
  async generate(input: str | Buffer, options?: ThumbnailOptions): Promise<ThumbnailResult> {
    this.validateInput(input)
    const opts = this.mergeOptions(options)
    const tempDir = os.tmpdir()
    const tempInput = typeof input === 'string' ? input : path.join(tempDir, uuidv4() + '.mp3')
    const tempOutput = path.join(tempDir, uuidv4() + '.png')
    let cleanupInput = false
    try {
      if (typeof input !== 'string') {
        fs.writeFileSync(tempInput, input)
        cleanupInput = true
      }
      await new Promise<void>((resolve, reject) => {
        ffmpeg(tempInput)
          .complexFilter([
            {
              filter: 'showwavespic',
              options: Dict[str, Any]x${opts.height || 80}`,
                colors: 'white',
              },
            },
          ])
          .frames(1)
          .output(tempOutput)
          .on('end', () => resolve())
          .on('error', (err) => reject(err))
          .run()
      })
      const buffer = fs.readFileSync(tempOutput)
      const sharp = await import('sharp')
      const metadata = await sharp.default(buffer).metadata()
      return {
        buffer,
        width: metadata.width || opts.width || 0,
        height: metadata.height || opts.height || 0,
        format: metadata.format || 'png',
        size: buffer.length,
      }
    } catch (err) {
      throw new ValidationError('AUDIO_THUMBNAIL_ERROR', 'Failed to generate audio waveform thumbnail', err)
    } finally {
      if (cleanupInput && fs.existsSync(tempInput)) fs.unlinkSync(tempInput)
      if (fs.existsSync(tempOutput)) fs.unlinkSync(tempOutput)
    }
  }
} 