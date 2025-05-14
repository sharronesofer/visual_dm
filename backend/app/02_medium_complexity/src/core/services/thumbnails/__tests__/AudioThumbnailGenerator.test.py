from typing import Any, Dict



jest.mock('fluent-ffmpeg', () => {
  const mockFfmpeg = jest.fn().mockReturnValue({
    outputOptions: jest.fn().mockReturnThis(),
    output: jest.fn().mockReturnThis(),
    on: jest.fn().mockReturnThis(),
    run: jest.fn(),
  })
  const mockFfprobe = jest.fn()
  return Object.assign(mockFfmpeg, { ffprobe: mockFfprobe })
})
jest.mock('mime-types', () => ({
  lookup: jest.fn(),
}))
jest.mock('sharp', () => {
  const mockSharp = jest.fn().mockReturnValue({
    metadata: jest.fn().mockResolvedValue({ width: 800, height: 600, format: 'jpeg' }),
    resize: jest.fn().mockReturnThis(),
    toFormat: jest.fn().mockReturnThis(),
    toBuffer: jest.fn().mockResolvedValue({ 
      data: Buffer.from('test-image'),
      info: Dict[str, Any]
    }),
  })
  return mockSharp
})
const ffmpeg = require('fluent-ffmpeg')
describe('AudioThumbnailGenerator', () => {
  let generator: AudioThumbnailGenerator
  const testAudio = Buffer.from('test-audio')
  const defaultOptions: ThumbnailOptions = {
    width: 200,
    height: 200,
    quality: 80,
    format: 'jpeg',
    preserveAspectRatio: true,
  }
  beforeEach(() => {
    jest.clearAllMocks()
    generator = new AudioThumbnailGenerator()
  })
  describe('canHandle', () => {
    it('should return true for supported audio types', () => {
      const supportedTypes = [
        'audio/mpeg',
        'audio/wav',
        'audio/ogg',
        'audio/flac',
        'audio/aac',
        'audio/webm',
      ]
      supportedTypes.forEach((mimeType) => {
        expect(generator.canHandle(mimeType)).toBe(true)
      })
    })
    it('should return false for unsupported types', () => {
      const unsupportedTypes = [
        'audio/midi',
        'video/mp4',
        'image/jpeg',
        'text/plain',
      ]
      unsupportedTypes.forEach((mimeType) => {
        expect(generator.canHandle(mimeType)).toBe(false)
      })
    })
  })
  describe('generateThumbnail', () => {
    beforeEach(() => {
      ffmpeg.ffprobe.mockImplementation((_, callback) => {
        callback(null, {
          format: Dict[str, Any],
        })
      })
      (ffmpeg as jest.Mock).mockReturnValue({
        outputOptions: jest.fn().mockReturnThis(),
        output: jest.fn().mockReturnThis(),
        on: jest.fn().mockImplementation(function(this: Any, event: str, callback: () => void) {
          if (event === 'end') {
            callback()
          }
          return this
        }),
        run: jest.fn(),
      })
    })
    it('should generate thumbnail from buffer', async () => {
      const result = await generator.generateThumbnail(testAudio, defaultOptions)
      expect(result.success).toBe(true)
      expect(result.data).toBeDefined()
      expect(ffmpeg).toHaveBeenCalled()
    })
    it('should generate thumbnail from file path', async () => {
      (lookup as jest.Mock).mockReturnValue('audio/mpeg')
      const result = await generator.generateThumbnail('test.mp3', defaultOptions)
      expect(result.success).toBe(true)
      expect(result.data).toBeDefined()
      expect(ffmpeg).toHaveBeenCalledWith('test.mp3')
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
      const result = await generator.generateThumbnail(testAudio, invalidOptions)
      expect(result.success).toBe(false)
      expect(result.error).toBeInstanceOf(ValidationError)
      expect(result.data).toBeNull()
    })
    it('should handle ffprobe errors', async () => {
      ffmpeg.ffprobe.mockImplementation((_, callback) => {
        callback(new Error('FFprobe failed'), null)
      })
      const result = await generator.generateThumbnail(testAudio, defaultOptions)
      expect(result.success).toBe(false)
      expect(result.error).toBeInstanceOf(ValidationError)
      expect(result.data).toBeNull()
    })
    it('should handle waveform generation errors', async () => {
      (ffmpeg as jest.Mock).mockReturnValue({
        outputOptions: jest.fn().mockReturnThis(),
        output: jest.fn().mockReturnThis(),
        on: jest.fn().mockImplementation(function(this: Any, event: str, callback: (err?: Error) => void) {
          if (event === 'error') {
            callback(new Error('Waveform generation failed'))
          }
          return this
        }),
        run: jest.fn(),
      })
      const result = await generator.generateThumbnail(testAudio, defaultOptions)
      expect(result.success).toBe(false)
      expect(result.error).toBeInstanceOf(ValidationError)
      expect(result.data).toBeNull()
    })
    it('should use default options when none provided', async () => {
      await generator.generateThumbnail(testAudio)
      expect(ffmpeg).toHaveBeenCalled()
      const mockFfmpeg = ffmpeg as unknown as jest.Mock
      expect(mockFfmpeg().outputOptions).toHaveBeenCalledWith(
        expect.arrayContaining([
          '-filter_complex',
          expect.stringContaining('200x200'), 
        ])
      )
    })
    it('should preserve aspect ratio when specified', async () => {
      const options: ThumbnailOptions = {
        ...defaultOptions,
        preserveAspectRatio: true,
      }
      await generator.generateThumbnail(testAudio, options)
      const mockSharp = (await import('sharp')).default as unknown as jest.Mock
      expect(mockSharp().resize).toHaveBeenCalledWith(
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
      await generator.generateThumbnail(testAudio, options)
      const mockSharp = (await import('sharp')).default as unknown as jest.Mock
      expect(mockSharp().resize).toHaveBeenCalledWith(
        expect.any(Number),
        expect.any(Number),
        expect.objectContaining({ fit: 'fill' })
      )
    })
    it('should handle custom dimensions', async () => {
      const options: ThumbnailOptions = {
        ...defaultOptions,
        width: 300,
        height: 150,
      }
      await generator.generateThumbnail(testAudio, options)
      const mockFfmpeg = ffmpeg as unknown as jest.Mock
      expect(mockFfmpeg().outputOptions).toHaveBeenCalledWith(
        expect.arrayContaining([
          '-filter_complex',
          expect.stringContaining('300x150'),
        ])
      )
    })
  })
  describe('cleanup', () => {
    it('should not throw error on cleanup', async () => {
      await expect(generator.cleanup()).resolves.not.toThrow()
    })
  })
}) 