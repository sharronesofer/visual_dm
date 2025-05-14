from typing import Any



jest.mock('sharp', () => {
  const actual = jest.requireActual('sharp')
  return jest.fn(() => ({
    resize: jest.fn().mockReturnThis(),
    toFormat: jest.fn().mockReturnThis(),
    toBuffer: jest.fn().mockResolvedValue(Buffer.from([1, 2, 3])),
    metadata: jest.fn().mockResolvedValue({ width: 100, height: 100, format: 'jpeg' }),
  }))
})
describe('ImageThumbnailGenerator', () => {
  let generator: ImageThumbnailGenerator
  beforeEach(() => {
    generator = new ImageThumbnailGenerator()
  })
  it('should support jpeg mime type', () => {
    expect(generator.supports('image/jpeg')).toBe(true)
    expect(generator.supports('application/pdf')).toBe(false)
  })
  it('should throw ValidationError for missing input', async () => {
    await expect(generator.generate(undefined as any)).rejects.toThrow(ValidationError)
  })
  it('should generate a thumbnail for valid input', async () => {
    const result = await generator.generate(Buffer.from([1, 2, 3]), { width: 100, height: 100 })
    expect(result.width).toBe(100)
    expect(result.height).toBe(100)
    expect(result.format).toBe('jpeg')
    expect(result.buffer).toBeInstanceOf(Buffer)
  })
}) 