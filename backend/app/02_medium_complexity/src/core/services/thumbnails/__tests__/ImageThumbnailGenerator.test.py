from typing import Any



jest.mock('sharp', () => {
  const mockSharp = jest.fn().mockReturnValue({
    metadata: jest.fn().mockResolvedValue({ width: 800, height: 600, format: 'jpeg' }),
    resize: jest.fn().mockReturnThis(),
    toFormat: jest.fn().mockReturnThis(),
    toBuffer: jest.fn().mockResolvedValue(Buffer.from('test-image')),
  })
  mockSharp.prototype.metadata = jest.fn()
  return mockSharp
})
jest.mock('mime-types', () => ({
  lookup: jest.fn(),
}))
describe('ImageThumbnailGenerator', () => {
  let generator: ImageThumbnailGenerator
  const testImage = Buffer.from('test-image')
  const defaultOptions: ThumbnailOptions = {
    width: 200,
    height: 200,
    quality: 80,
    format: 'jpeg',
    preserveAspectRatio: true,
  }
  beforeEach(() => {
    jest.clearAllMocks()
    generator = new ImageThumbnailGenerator()
  })
  describe('canHandle', () => {
    it('should return true for supported image types', () => {
      const supportedTypes = [
        'image/jpeg',
        'image/png',
        'image/webp',
        'image/tiff',
        'image/gif',
      ]
      supportedTypes.forEach((mimeType) => {
        expect(generator.canHandle(mimeType)).toBe(true)
      })
    })
    it('should return false for unsupported types', () => {
      const unsupportedTypes = [
        'image/bmp',
        'application/pdf',
        'video/mp4',
        'text/plain',
      ]
      unsupportedTypes.forEach((mimeType) => {
        expect(generator.canHandle(mimeType)).toBe(false)
      })
    })
  })
  describe('validateFile', () => {
    it('should validate buffer input', async () => {
      const result = await generator['validateFile'](testImage)
      expect(result).toBe(true)
    })
    it('should validate file path input with supported format', async () => {
      (lookup as jest.Mock).mockReturnValue('image/jpeg')
      const result = await generator['validateFile']('test.jpg')
      expect(result).toBe(true)
    })
    it('should reject empty input', async () => {
      const result = await generator['validateFile']('')
      expect(result).toBe(false)
    })
    it('should reject unsupported format', async () => {
      (lookup as jest.Mock).mockReturnValue('image/bmp')
      const result = await generator['validateFile']('test.bmp')
      expect(result).toBe(false)
    })
    it('should reject invalid file type', async () => {
      const result = await generator['validateFile'](123 as any)
      expect(result).toBe(false)
    })
  })
  describe('generateThumbnail', () => {
    it('should generate thumbnail from buffer', async () => {
      const result = await generator.generateThumbnail(testImage, defaultOptions)
      expect(result.success).toBe(true)
      expect(result.data).toBeDefined()
      expect(sharp).toHaveBeenCalledWith(testImage)
    })
    it('should generate thumbnail from file path', async () => {
      (lookup as jest.Mock).mockReturnValue('image/jpeg')
      const result = await generator.generateThumbnail('test.jpg', defaultOptions)
      expect(result.success).toBe(true)
      expect(result.data).toBeDefined()
      expect(sharp).toHaveBeenCalledWith('test.jpg')
    })
    it('should handle invalid file input', async () => {
      const result = await generator.generateThumbnail('', defaultOptions)
      expect(result.success).toBe(false)
      expect(result.error).toBeInstanceOf(ValidationError)
      expect(result.data).toBeNull()
    })
    it('should handle invalid options', async () => {
      const invalidOptions: ThumbnailOptions = {
        ...defaultOptions,
        width: -100, 
      }
      const result = await generator.generateThumbnail(testImage, invalidOptions)
      expect(result.success).toBe(false)
      expect(result.error).toBeInstanceOf(ValidationError)
      expect(result.data).toBeNull()
    })
    it('should preserve aspect ratio when specified', async () => {
      const options: ThumbnailOptions = {
        ...defaultOptions,
        preserveAspectRatio: true,
      }
      await generator.generateThumbnail(testImage, options)
      const mockSharp = sharp as unknown as jest.Mock
      expect(mockSharp(testImage).resize).toHaveBeenCalledWith(
        expect.any(Number),
        expect.any(Number),
        expect.objectContaining({ fit: 'inside' })
      )
    })
    it('should not preserve aspect ratio when specified', async () => {
      const options: ThumbnailOptions = {
        ...defaultOptions,
        preserveAspectRatio: false,
      }
      await generator.generateThumbnail(testImage, options)
      const mockSharp = sharp as unknown as jest.Mock
      expect(mockSharp(testImage).resize).toHaveBeenCalledWith(
        expect.any(Number),
        expect.any(Number),
        expect.objectContaining({ fit: 'fill' })
      )
    })
    it('should handle sharp errors', async () => {
      const error = new Error('Sharp processing failed')
      const mockSharp = sharp as unknown as jest.Mock
      mockSharp.mockImplementationOnce(() => {
        throw error
      })
      const result = await generator.generateThumbnail(testImage, defaultOptions)
      expect(result.success).toBe(false)
      expect(result.error).toBeInstanceOf(ValidationError)
      expect(result.data).toBeNull()
    })
    it('should use default options when none provided', async () => {
      await generator.generateThumbnail(testImage)
      const mockSharp = sharp as unknown as jest.Mock
      expect(mockSharp(testImage).resize).toHaveBeenCalledWith(
        200,
        200,
        expect.objectContaining({ fit: 'inside' })
      )
    })
    it('should handle metadata extraction errors', async () => {
      const mockSharp = sharp as unknown as jest.Mock
      mockSharp.mockReturnValueOnce({
        metadata: jest.fn().mockRejectedValueOnce(new Error('Metadata extraction failed')),
        resize: jest.fn().mockReturnThis(),
        toFormat: jest.fn().mockReturnThis(),
        toBuffer: jest.fn().mockResolvedValue(Buffer.from('test-image')),
      })
      const result = await generator.generateThumbnail(testImage, defaultOptions)
      expect(result.success).toBe(false)
      expect(result.error).toBeInstanceOf(ValidationError)
      expect(result.data).toBeNull()
    })
  })
  describe('cleanup', () => {
    it('should not throw error on cleanup', async () => {
      await expect(generator.cleanup()).resolves.not.toThrow()
    })
  })
}) 