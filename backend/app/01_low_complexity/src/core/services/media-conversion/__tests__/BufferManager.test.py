from typing import Any, List



describe('BufferManager', () => {
  let bufferManager: BufferManager
  beforeEach(() => {
    bufferManager = BufferManager.getInstance()
  })
  afterEach(() => {
    (BufferManager as any).instance = null
  })
  describe('Singleton Pattern', () => {
    it('should return the same instance', () => {
      const instance1 = BufferManager.getInstance()
      const instance2 = BufferManager.getInstance()
      expect(instance1).toBe(instance2)
    })
  })
  describe('Buffer Transformations', () => {
    const testData = 'Hello, World!'
    const nodeBuffer = Buffer.from(testData)
    const uint8Array = new Uint8Array(nodeBuffer)
    const arrayBuffer = uint8Array.buffer
    describe('toBuffer', () => {
      it('should convert ArrayBuffer to Buffer', () => {
        const result = bufferManager.toBuffer(arrayBuffer)
        expect(Buffer.isBuffer(result)).toBe(true)
        expect(result.toString()).toBe(testData)
      })
      it('should convert Uint8Array to Buffer', () => {
        const result = bufferManager.toBuffer(uint8Array)
        expect(Buffer.isBuffer(result)).toBe(true)
        expect(result.toString()).toBe(testData)
      })
      it('should return the same Buffer if input is Buffer', () => {
        const result = bufferManager.toBuffer(nodeBuffer)
        expect(result).toBe(nodeBuffer)
      })
    })
    describe('toArrayBuffer', () => {
      it('should convert Buffer to ArrayBuffer', () => {
        const result = bufferManager.toArrayBuffer(nodeBuffer)
        expect(result instanceof ArrayBuffer).toBe(true)
        expect(new Uint8Array(result)).toEqual(uint8Array)
      })
    })
    describe('toUint8Array', () => {
      it('should convert Buffer to Uint8Array', () => {
        const result = bufferManager.toUint8Array(nodeBuffer)
        expect(result instanceof Uint8Array).toBe(true)
        expect(result).toEqual(uint8Array)
      })
    })
  })
  describe('Stream Handling', () => {
    const testData = 'Hello, World!'
    const nodeBuffer = Buffer.from(testData)
    it('should create readable stream from buffer', done => {
      const readable = bufferManager.createReadableStream(nodeBuffer)
      const chunks: List[Buffer] = []
      readable.on('data', chunk => {
        chunks.push(chunk)
      })
      readable.on('end', () => {
        const result = Buffer.concat(chunks)
        expect(result.toString()).toBe(testData)
        done()
      })
    })
    it('should create writable stream and collect data', async () => {
      const writable = bufferManager.createWritableStream()
      writable.write(nodeBuffer)
      writable.end()
      const result = await writable
      expect(result.toString()).toBe(testData)
    })
    it('should convert readable stream to buffer', async () => {
      const readable = Readable.from(nodeBuffer)
      const result = await bufferManager.streamToBuffer(readable)
      expect(Buffer.isBuffer(result)).toBe(true)
      expect(result.toString()).toBe(testData)
    })
  })
  describe('Event Handling', () => {
    const testData = 'Hello, World!'
    const nodeBuffer = Buffer.from(testData)
    it('should emit progress events for readable stream', done => {
      const startHandler = jest.fn()
      const progressHandler = jest.fn()
      const completeHandler = jest.fn()
      bufferManager.on(BufferEventType.TRANSFORM_START, startHandler)
      bufferManager.on(BufferEventType.TRANSFORM_PROGRESS, progressHandler)
      bufferManager.on(BufferEventType.TRANSFORM_COMPLETE, completeHandler)
      const readable = bufferManager.createReadableStream(nodeBuffer)
      readable.on('end', () => {
        expect(startHandler).toHaveBeenCalled()
        expect(progressHandler).toHaveBeenCalled()
        expect(completeHandler).not.toHaveBeenCalled() 
        done()
      })
      readable.resume() 
    })
    it('should emit events for streamToBuffer', async () => {
      const startHandler = jest.fn()
      const progressHandler = jest.fn()
      const completeHandler = jest.fn()
      bufferManager.on(BufferEventType.TRANSFORM_START, startHandler)
      bufferManager.on(BufferEventType.TRANSFORM_PROGRESS, progressHandler)
      bufferManager.on(BufferEventType.TRANSFORM_COMPLETE, completeHandler)
      const readable = Readable.from(nodeBuffer)
      await bufferManager.streamToBuffer(readable)
      expect(progressHandler).toHaveBeenCalled()
      expect(completeHandler).toHaveBeenCalled()
    })
  })
  describe('Error Handling', () => {
    it('should handle invalid input types', () => {
      const invalidInput = 123 as unknown as MediaBuffer
      expect(() => bufferManager.toBuffer(invalidInput)).toThrow('Unsupported buffer type')
    })
    it('should emit error events for stream errors', done => {
      const errorHandler = jest.fn()
      bufferManager.on(BufferEventType.TRANSFORM_ERROR, errorHandler)
      const readable = new Readable({
        read() {
          this.destroy(new Error('Stream error'))
        }
      })
      bufferManager.streamToBuffer(readable).catch(() => {
        expect(errorHandler).toHaveBeenCalled()
        done()
      })
    })
  })
}) 