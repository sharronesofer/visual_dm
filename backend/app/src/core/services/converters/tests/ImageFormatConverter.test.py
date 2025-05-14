from typing import Any, List


describe('ImageFormatConverter', () => {
  let converter: ImageFormatConverter
  let inputBuffer: Buffer
  let outputChunks: List[Buffer]
  let mockOutputStream: Writable
  let tempDir: str
  beforeEach(async () => {
    converter = new ImageFormatConverter()
    tempDir = path.join(__dirname, 'temp')
    inputBuffer = Buffer.from([
      0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01,
      0x01, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43,
      0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
      0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
      0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
      0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
      0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
      0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xC0, 0x00, 0x0B, 0x08, 0x00, 0x01, 0x00,
      0x01, 0x01, 0x01, 0x11, 0x00, 0xFF, 0xC4, 0x00, 0x14, 0x00, 0x01, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x03, 0xFF, 0xC4, 0x00, 0x14, 0x10, 0x01, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0xFF, 0xDA, 0x00, 0x08, 0x01, 0x01, 0x00, 0x00, 0x3F, 0x00, 0x37,
      0xFF, 0xD9
    ])
    outputChunks = []
    mockOutputStream = new Writable({
      write(chunk: Buffer, encoding: BufferEncoding, callback: (error?: Error | null) => void) {
        outputChunks.push(chunk)
        callback()
      }
    })
    await fs.mkdir(tempDir, { recursive: true })
  })
  afterEach(async () => {
    if (mockOutputStream.destroy && !mockOutputStream.destroyed) {
      mockOutputStream.destroy()
    }
    try {
      const files = await fs.readdir(tempDir)
      await Promise.all(
        files.map(file => fs.unlink(path.join(tempDir, file)))
      )
      await fs.rmdir(tempDir)
    } catch (error) {
    }
  })
  describe('convertStream', () => {
    it('should convert JPEG to PNG', async () => {
      const options: ConversionOptions = {
        targetFormat: 'png',
        quality: 90,
        tempDir,
      }
      const inputStream = Readable.from(inputBuffer)
      const result = await converter.convertStream(inputStream, mockOutputStream, options)
      expect(result.success).toBe(true)
      expect(result.data).toBeDefined()
      expect(result.data!.originalFormat).toBe('jpeg')
      expect(result.data!.metadata.format).toBe('png')
      expect(result.data!.bytesProcessed).toBeGreaterThan(0)
      expect(result.data!.totalBytes).toBeGreaterThan(0)
      expect(result.data!.processingTime).toBeGreaterThan(0)
      expect(result.data!.conversionTime).toBeGreaterThan(0)
      expect(outputChunks.length).toBeGreaterThan(0)
    })
    it('should convert JPEG to WebP', async () => {
      const options: ConversionOptions = {
        targetFormat: 'webp',
        quality: 80,
        compression: true,
        tempDir,
      }
      const inputStream = Readable.from(inputBuffer)
      const result = await converter.convertStream(inputStream, mockOutputStream, options)
      expect(result.success).toBe(true)
      expect(result.data).toBeDefined()
      expect(result.data!.originalFormat).toBe('jpeg')
      expect(result.data!.metadata.format).toBe('webp')
      expect(result.data!.bytesProcessed).toBeGreaterThan(0)
      expect(result.data!.totalBytes).toBeGreaterThan(0)
      expect(result.data!.processingTime).toBeGreaterThan(0)
      expect(result.data!.conversionTime).toBeGreaterThan(0)
      expect(outputChunks.length).toBeGreaterThan(0)
    })
    it('should handle resizing during conversion', async () => {
      const options: ConversionOptions = {
        targetFormat: 'png',
        width: 100,
        height: 100,
        quality: 90,
        tempDir,
      }
      const inputStream = Readable.from(inputBuffer)
      const result = await converter.convertStream(inputStream, mockOutputStream, options)
      expect(result.success).toBe(true)
      expect(result.data).toBeDefined()
      expect(result.data!.metadata.width).toBeLessThanOrEqual(100)
      expect(result.data!.metadata.height).toBeLessThanOrEqual(100)
    })
    it('should emit progress events during conversion', async () => {
      const options: ConversionOptions = {
        targetFormat: 'png',
        quality: 90,
        chunkSize: 1024,
        tempDir,
      }
      const progressEvents: Array<{ bytesProcessed: float; totalBytes: float }> = []
      converter.on('progress', (progress) => {
        progressEvents.push(progress)
      })
      const inputStream = Readable.from(inputBuffer)
      await converter.convertStream(inputStream, mockOutputStream, options)
      expect(progressEvents.length).toBeGreaterThan(0)
      expect(progressEvents[progressEvents.length - 1].bytesProcessed).toBe(progressEvents[progressEvents.length - 1].totalBytes)
    })
    it('should handle errors gracefully', async () => {
      const options: ConversionOptions = {
        targetFormat: 'invalid',
        tempDir,
      }
      const inputStream = Readable.from(inputBuffer)
      const result = await converter.convertStream(inputStream, mockOutputStream, options)
      expect(result.success).toBe(false)
      expect(result.error).toBeDefined()
      expect(result.error!.code).toBe('UnsupportedFormat')
    })
    it('should handle stream errors', async () => {
      const options: ConversionOptions = {
        targetFormat: 'png',
        tempDir,
      }
      const errorStream = new Readable({
        read() {
          this.destroy(new Error('Stream error'))
        }
      })
      const result = await converter.convertStream(errorStream, mockOutputStream, options)
      expect(result.success).toBe(false)
      expect(result.error).toBeDefined()
    })
    it('should clean up temporary files after conversion', async () => {
      const options: ConversionOptions = {
        targetFormat: 'png',
        tempDir,
      }
      const inputStream = Readable.from(inputBuffer)
      await converter.convertStream(inputStream, mockOutputStream, options)
      const files = await fs.readdir(tempDir)
      expect(files.length).toBe(0)
    })
  })
  describe('getSupportedFormats', () => {
    it('should return supported input formats', () => {
      const formats = converter.getSupportedInputFormats()
      expect(formats).toContain('jpeg')
      expect(formats).toContain('png')
      expect(formats).toContain('webp')
    })
    it('should return supported output formats', () => {
      const formats = converter.getSupportedOutputFormats()
      expect(formats).toContain('jpeg')
      expect(formats).toContain('png')
      expect(formats).toContain('webp')
    })
  })
}) 