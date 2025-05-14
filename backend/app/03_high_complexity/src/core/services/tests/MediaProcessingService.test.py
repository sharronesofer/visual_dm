from typing import Any, Dict, List



  ProcessingJobStatus,
  StreamProcessingOptions,
  ProcessingProgress,
  ProcessingJob
} from '../types/MediaProcessing'
const testFilesDir = path.join(__dirname, '../../../test/fixtures/media')
async function createTestImage(): Promise<void> {
  const testImagePath = path.join(testFilesDir, 'test.jpg')
  const imageBuffer = Buffer.from('fake image data')
  await fs.writeFile(testImagePath, imageBuffer)
}
async function createTestVideo(): Promise<void> {
  const testVideoPath = path.join(testFilesDir, 'test.mp4')
  const videoBuffer = Buffer.from('fake video data')
  await fs.writeFile(testVideoPath, videoBuffer)
}
async function createTestAudio(): Promise<void> {
  const testAudioPath = path.join(testFilesDir, 'test.mp3')
  const audioBuffer = Buffer.from('fake audio data')
  await fs.writeFile(testAudioPath, audioBuffer)
}
async function createTestDocument(): Promise<void> {
  const testDocPath = path.join(testFilesDir, 'test.docx')
  const docBuffer = Buffer.from('fake document data')
  await fs.writeFile(testDocPath, docBuffer)
}
describe('MediaProcessingService', () => {
  let service: MediaProcessingService
  beforeAll(async () => {
    await fs.mkdir(testFilesDir, { recursive: true })
    await Promise.all([
      createTestImage(),
      createTestVideo(),
      createTestAudio(),
      createTestDocument()
    ])
    service = MediaProcessingService.getInstance()
    await service.initialize()
  })
  afterAll(async () => {
    await service.cleanup()
    await fs.rm(testFilesDir, { recursive: true, force: true })
  })
  describe('Initialization', () => {
    it('should initialize successfully', async () => {
      const newService = MediaProcessingService.getInstance()
      await expect(newService.initialize()).resolves.not.toThrow()
    })
    it('should be a singleton', () => {
      const instance1 = MediaProcessingService.getInstance()
      const instance2 = MediaProcessingService.getInstance()
      expect(instance1).toBe(instance2)
    })
  })
  describe('Input Validation', () => {
    it('should reject null input', async () => {
      await expect(
        service.process(null as any, {
          mimeType: 'image/jpeg',
          thumbnail: Dict[str, Any]
        })
      ).resolves.toEqual({
        success: false,
        error: expect.any(ServiceError)
      })
    })
    it('should reject empty string input', async () => {
      await expect(
        service.process('', {
          mimeType: 'image/jpeg',
          thumbnail: Dict[str, Any]
        })
      ).resolves.toEqual({
        success: false,
        error: expect.any(ServiceError)
      })
    })
    it('should reject missing MIME type', async () => {
      const buffer = await fs.readFile(path.join(testFilesDir, 'test.jpg'))
      await expect(
        service.process(buffer, {
          mimeType: '',
          thumbnail: Dict[str, Any]
        })
      ).resolves.toEqual({
        success: false,
        error: expect.any(ServiceError)
      })
    })
    it('should reject when no operations are requested', async () => {
      const buffer = await fs.readFile(path.join(testFilesDir, 'test.jpg'))
      await expect(
        service.process(buffer, {
          mimeType: 'image/jpeg'
        })
      ).resolves.toEqual({
        success: false,
        error: expect.any(ServiceError)
      })
    })
  })
  describe('Image Processing', () => {
    let imageBuffer: Buffer
    beforeAll(async () => {
      imageBuffer = await fs.readFile(path.join(testFilesDir, 'test.jpg'))
    })
    it('should generate thumbnail', async () => {
      const result = await service.process(imageBuffer, {
        mimeType: 'image/jpeg',
        thumbnail: Dict[str, Any]
      })
      expect(result.success).toBe(true)
      expect(result.data).toBeDefined()
      expect(result.data!.thumbnail).toBeInstanceOf(Buffer)
      expect(result.data!.processingTime).toBeGreaterThan(0)
    })
    it('should convert format', async () => {
      const result = await service.process(imageBuffer, {
        mimeType: 'image/jpeg',
        conversion: Dict[str, Any]
      })
      expect(result.success).toBe(true)
      expect(result.data).toBeDefined()
      expect(result.data!.converted).toBeInstanceOf(Buffer)
      expect(result.data!.processingTime).toBeGreaterThan(0)
    })
    it('should extract metadata', async () => {
      const result = await service.process(imageBuffer, {
        mimeType: 'image/jpeg',
        metadata: Dict[str, Any]
      })
      expect(result.success).toBe(true)
      expect(result.data).toBeDefined()
      expect(result.data!.metadata).toEqual(
        expect.objectContaining({
          format: expect.any(String),
          width: expect.any(Number),
          height: expect.any(Number)
        })
      )
    })
    it('should process multiple operations concurrently', async () => {
      const result = await service.process(imageBuffer, {
        mimeType: 'image/jpeg',
        thumbnail: Dict[str, Any],
        conversion: Dict[str, Any],
        metadata: Dict[str, Any]
      })
      expect(result.success).toBe(true)
      expect(result.data).toBeDefined()
      expect(result.data!.thumbnail).toBeInstanceOf(Buffer)
      expect(result.data!.converted).toBeInstanceOf(Buffer)
      expect(result.data!.metadata).toBeDefined()
    })
  })
  describe('Video Processing', () => {
    let videoBuffer: Buffer
    beforeAll(async () => {
      videoBuffer = await fs.readFile(path.join(testFilesDir, 'test.mp4'))
    })
    it('should generate video thumbnail', async () => {
      const result = await service.process(videoBuffer, {
        mimeType: 'video/mp4',
        thumbnail: Dict[str, Any]
      })
      expect(result.success).toBe(true)
      expect(result.data).toBeDefined()
      expect(result.data!.thumbnail).toBeInstanceOf(Buffer)
    })
    it('should convert video format', async () => {
      const result = await service.process(videoBuffer, {
        mimeType: 'video/mp4',
        conversion: Dict[str, Any]
      })
      expect(result.success).toBe(true)
      expect(result.data).toBeDefined()
      expect(result.data!.converted).toBeInstanceOf(Buffer)
    })
    it('should extract video metadata', async () => {
      const result = await service.process(videoBuffer, {
        mimeType: 'video/mp4',
        metadata: Dict[str, Any]
      })
      expect(result.success).toBe(true)
      expect(result.data).toBeDefined()
      expect(result.data!.metadata).toEqual(
        expect.objectContaining({
          duration: expect.any(Number),
          width: expect.any(Number),
          height: expect.any(Number),
          codec: expect.any(String)
        })
      )
    })
  })
  describe('Audio Processing', () => {
    let audioBuffer: Buffer
    beforeAll(async () => {
      audioBuffer = await fs.readFile(path.join(testFilesDir, 'test.mp3'))
    })
    it('should convert audio format', async () => {
      const result = await service.process(audioBuffer, {
        mimeType: 'audio/mpeg',
        conversion: Dict[str, Any]
      })
      expect(result.success).toBe(true)
      expect(result.data).toBeDefined()
      expect(result.data!.converted).toBeInstanceOf(Buffer)
    })
    it('should extract audio metadata', async () => {
      const result = await service.process(audioBuffer, {
        mimeType: 'audio/mpeg',
        metadata: Dict[str, Any]
      })
      expect(result.success).toBe(true)
      expect(result.data).toBeDefined()
      expect(result.data!.metadata).toEqual(
        expect.objectContaining({
          duration: expect.any(Number),
          bitrate: expect.any(Number),
          sampleRate: expect.any(Number)
        })
      )
    })
  })
  describe('Document Processing', () => {
    let pdfBuffer: Buffer
    beforeAll(async () => {
      pdfBuffer = await fs.readFile(path.join(testFilesDir, 'test.pdf'))
    })
    it('should generate document thumbnail', async () => {
      const result = await service.process(pdfBuffer, {
        mimeType: 'application/pdf',
        thumbnail: Dict[str, Any]
      })
      expect(result.success).toBe(true)
      expect(result.data).toBeDefined()
      expect(result.data!.thumbnail).toBeInstanceOf(Buffer)
    })
    it('should convert document format', async () => {
      const result = await service.process(pdfBuffer, {
        mimeType: 'application/pdf',
        conversion: Dict[str, Any]
      })
      expect(result.success).toBe(true)
      expect(result.data).toBeDefined()
      expect(result.data!.converted).toBeInstanceOf(Buffer)
    })
    it('should extract document metadata', async () => {
      const result = await service.process(pdfBuffer, {
        mimeType: 'application/pdf',
        metadata: Dict[str, Any]
      })
      expect(result.success).toBe(true)
      expect(result.data).toBeDefined()
      expect(result.data!.metadata).toEqual(
        expect.objectContaining({
          pageCount: expect.any(Number),
          author: expect.any(String),
          title: expect.any(String)
        })
      )
    })
  })
  describe('Caching', () => {
    it('should cache and return cached results', async () => {
      const buffer = await fs.readFile(path.join(testFilesDir, 'test.jpg'))
      const options = {
        mimeType: 'image/jpeg',
        thumbnail: Dict[str, Any],
        cache: Dict[str, Any]
      }
      const result1 = await service.process(buffer, options)
      expect(result1.success).toBe(true)
      const result2 = await service.process(buffer, options)
      expect(result2.success).toBe(true)
      expect(result2.data!.processingTime).toBeLessThan(
        result1.data!.processingTime
      )
    })
  })
  describe('Error Handling', () => {
    it('should handle invalid file formats', async () => {
      const buffer = Buffer.from('invalid file content')
      const result = await service.process(buffer, {
        mimeType: 'image/jpeg',
        thumbnail: Dict[str, Any]
      })
      expect(result.success).toBe(false)
      expect(result.error).toBeInstanceOf(ServiceError)
    })
    it('should handle processing failures gracefully', async () => {
      const buffer = await fs.readFile(path.join(testFilesDir, 'test.jpg'))
      buffer[0] = 0
      buffer[1] = 0
      const result = await service.process(buffer, {
        mimeType: 'image/jpeg',
        thumbnail: Dict[str, Any]
      })
      expect(result.success).toBe(false)
      expect(result.error).toBeInstanceOf(ServiceError)
    })
  })
  describe('Stream Processing', () => {
    let inputStream: Readable
    let outputStream: Writable
    let testBuffer: Buffer
    beforeEach(async () => {
      testBuffer = await fs.readFile(path.join(testFilesDir, 'test.jpg'))
      inputStream = Readable.from(testBuffer)
      outputStream = new Writable({
        write(chunk: Buffer | string, encoding: BufferEncoding, callback: (error?: Error | null) => void): void {
          callback()
        }
      })
    })
    afterEach(() => {
      if (inputStream.destroy && !inputStream.destroyed) {
        inputStream.destroy()
      }
      if (outputStream.destroy && !outputStream.destroyed) {
        outputStream.destroy()
      }
    })
    it('should process image stream successfully', async () => {
      const options: StreamProcessingOptions = {
        mimeType: 'image/jpeg',
        conversion: Dict[str, Any],
        chunkSize: 1024 * 1024,
        progressInterval: 50
      }
      const result = await service.processStream(inputStream, outputStream, options)
      expect(result.success).toBe(true)
      expect(result.data).toBeDefined()
      expect(result.data!.originalFormat).toBe('jpeg')
      expect(result.data!.processingTime).toBeGreaterThan(0)
      expect(result.data!.bytesProcessed).toBeGreaterThan(0)
    })
    it('should process video stream successfully', async () => {
      const videoBuffer = await fs.readFile(path.join(testFilesDir, 'test.mp4'))
      const videoInputStream = Readable.from(videoBuffer)
      const videoOutputStream = new Writable({
        write(chunk: Buffer | string, encoding: BufferEncoding, callback: (error?: Error | null) => void): void {
          callback()
        }
      })
      const options: StreamProcessingOptions = {
        mimeType: 'video/mp4',
        conversion: Dict[str, Any],
        chunkSize: 1024 * 1024,
        progressInterval: 50
      }
      const result = await service.processStream(videoInputStream, videoOutputStream, options)
      expect(result.success).toBe(true)
      expect(result.data).toBeDefined()
      expect(result.data!.originalFormat).toBe('mp4')
      expect(result.data!.processingTime).toBeGreaterThan(0)
      expect(result.data!.bytesProcessed).toBeGreaterThan(0)
      expect(result.data!.totalBytes).toBeGreaterThan(0)
    })
    it('should process audio stream successfully', async () => {
      const audioBuffer = await fs.readFile(path.join(testFilesDir, 'test.mp3'))
      const audioInputStream = Readable.from(audioBuffer)
      const audioOutputStream = new Writable({
        write(chunk: Buffer | string, encoding: BufferEncoding, callback: (error?: Error | null) => void): void {
          callback()
        }
      })
      const options: StreamProcessingOptions = {
        mimeType: 'audio/mpeg',
        conversion: Dict[str, Any],
        chunkSize: 1024 * 1024,
        progressInterval: 50
      }
      const result = await service.processStream(audioInputStream, audioOutputStream, options)
      expect(result.success).toBe(true)
      expect(result.data).toBeDefined()
      expect(result.data!.originalFormat).toBe('mp3')
      expect(result.data!.processingTime).toBeGreaterThan(0)
      expect(result.data!.bytesProcessed).toBeGreaterThan(0)
      expect(result.data!.totalBytes).toBeGreaterThan(0)
    })
    it('should process document stream successfully', async () => {
      const docBuffer = await fs.readFile(path.join(testFilesDir, 'test.docx'))
      const docInputStream = Readable.from(docBuffer)
      const docOutputStream = new Writable({
        write(chunk: Buffer | string, encoding: BufferEncoding, callback: (error?: Error | null) => void): void {
          callback()
        }
      })
      const options: StreamProcessingOptions = {
        mimeType: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        conversion: Dict[str, Any],
        chunkSize: 1024 * 1024,
        progressInterval: 50
      }
      const result = await service.processStream(docInputStream, docOutputStream, options)
      expect(result.success).toBe(true)
      expect(result.data).toBeDefined()
      expect(result.data!.originalFormat).toBe('docx')
      expect(result.data!.processingTime).toBeGreaterThan(0)
      expect(result.data!.bytesProcessed).toBeGreaterThan(0)
      expect(result.data!.totalBytes).toBeGreaterThan(0)
    })
    it('should handle errors during stream processing', async () => {
      const options: StreamProcessingOptions = {
        mimeType: 'image/jpeg',
        conversion: Dict[str, Any]
      }
      const result = await service.processStream(inputStream, outputStream, options)
      expect(result.success).toBe(false)
      expect(result.error).toBeDefined()
      expect(result.error!.code).toBe('STREAM_PROCESSING_ERROR')
    })
    it('should track progress during stream processing', async () => {
      const progressUpdates: List[number] = []
      const options: StreamProcessingOptions = {
        mimeType: 'image/jpeg',
        conversion: Dict[str, Any],
        progressInterval: 50
      }
      service.on('progress', (progress: ProcessingProgress) => {
        progressUpdates.push(progress.overall)
      })
      await service.processStream(inputStream, outputStream, options)
      expect(progressUpdates.length).toBeGreaterThan(0)
      expect(progressUpdates[progressUpdates.length - 1]).toBe(100)
    })
    it('should process multiple streams in parallel', async () => {
      const streams = await Promise.all([
        fs.readFile(path.join(testFilesDir, 'test.jpg')),
        fs.readFile(path.join(testFilesDir, 'test.mp4')),
        fs.readFile(path.join(testFilesDir, 'test.mp3'))
      ])
      const options: List[StreamProcessingOptions] = [
        {
          mimeType: 'image/jpeg',
          conversion: Dict[str, Any]
        },
        {
          mimeType: 'video/mp4',
          conversion: Dict[str, Any]
        },
        {
          mimeType: 'audio/mpeg',
          conversion: Dict[str, Any]
        }
      ]
      const results = await Promise.all(
        streams.map((buffer, index) => {
          const inputStream = Readable.from(buffer)
          const outputStream = new Writable({
            write(chunk: Buffer | string, encoding: BufferEncoding, callback: (error?: Error | null) => void): void {
              callback()
            }
          })
          return service.processStream(inputStream, outputStream, options[index])
        })
      )
      results.forEach(result => {
        expect(result.success).toBe(true)
        expect(result.data).toBeDefined()
        expect(result.data!.processingTime).toBeGreaterThan(0)
      })
    })
  })
}) 