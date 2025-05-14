import { Readable, Writable } from 'stream';
import { BufferManager, BufferEventType, MediaBuffer } from '../../../services/media-conversion/BufferManager';

describe('BufferManager', () => {
  let bufferManager: BufferManager;

  beforeEach(() => {
    bufferManager = BufferManager.getInstance();
  });

  describe('Singleton Pattern', () => {
    it('should return the same instance', () => {
      const instance1 = BufferManager.getInstance();
      const instance2 = BufferManager.getInstance();
      expect(instance1).toBe(instance2);
    });
  });

  describe('Buffer Type Conversions', () => {
    const testData = 'Hello, World!';
    const buffer = Buffer.from(testData);
    const uint8Array = new Uint8Array(buffer);
    const arrayBuffer = buffer.buffer;

    it('should convert various types to Buffer', () => {
      expect(bufferManager.toBuffer(buffer)).toBeInstanceOf(Buffer);
      expect(bufferManager.toBuffer(uint8Array)).toBeInstanceOf(Buffer);
      expect(bufferManager.toBuffer(arrayBuffer)).toBeInstanceOf(Buffer);

      expect(bufferManager.toBuffer(buffer).toString()).toBe(testData);
      expect(bufferManager.toBuffer(uint8Array).toString()).toBe(testData);
      expect(bufferManager.toBuffer(arrayBuffer).toString()).toBe(testData);
    });

    it('should convert Buffer to ArrayBuffer', () => {
      const result = bufferManager.toArrayBuffer(buffer);
      expect(result).toBeInstanceOf(ArrayBuffer);
      expect(new Uint8Array(result)).toEqual(uint8Array);
    });

    it('should convert Buffer to Uint8Array', () => {
      const result = bufferManager.toUint8Array(buffer);
      expect(result).toBeInstanceOf(Uint8Array);
      expect(result).toEqual(uint8Array);
    });

    it('should throw error for unsupported buffer types', () => {
      expect(() => {
        // @ts-expect-error Testing invalid input
        bufferManager.toBuffer('invalid');
      }).toThrow('Unsupported buffer type');
    });
  });

  describe('Stream Operations', () => {
    const testData = Buffer.from('Test data for streaming');

    it('should create readable stream from buffer', async () => {
      const progressEvents: any[] = [];
      bufferManager.on(BufferEventType.TRANSFORM_PROGRESS, (progress) => {
        progressEvents.push(progress);
      });

      const stream = bufferManager.createReadableStream(testData, { chunkSize: 5 });
      const chunks: Buffer[] = [];

      for await (const chunk of stream) {
        chunks.push(chunk);
      }

      const result = Buffer.concat(chunks);
      expect(result.toString()).toBe(testData.toString());
      expect(progressEvents.length).toBeGreaterThan(0);
      expect(progressEvents[0].totalBytes).toBe(testData.length);
    });

    it('should create writable stream and collect data', async () => {
      const writableStream = bufferManager.createWritableStream();
      const progressEvents: any[] = [];
      
      bufferManager.on(BufferEventType.TRANSFORM_PROGRESS, (progress) => {
        progressEvents.push(progress);
      });

      writableStream.write(testData.slice(0, 10));
      writableStream.write(testData.slice(10));
      writableStream.end();

      const result = await writableStream;
      expect(result.toString()).toBe(testData.toString());
      expect(progressEvents.length).toBeGreaterThan(0);
    });

    it('should convert readable stream to buffer', async () => {
      const readable = Readable.from([testData]);
      const result = await bufferManager.streamToBuffer(readable);
      expect(result.toString()).toBe(testData.toString());
    });

    it('should handle stream errors', async () => {
      const errorStream = new Readable({
        read() {
          this.emit('error', new Error('Stream error'));
        }
      });

      const errorHandler = jest.fn();
      bufferManager.on(BufferEventType.TRANSFORM_ERROR, errorHandler);

      await expect(bufferManager.streamToBuffer(errorStream)).rejects.toThrow('Stream error');
      expect(errorHandler).toHaveBeenCalled();
    });
  });

  describe('Event Handling', () => {
    const testData = Buffer.from('Event test data');

    it('should emit transform events in correct order', async () => {
      const events: string[] = [];
      const eventHandler = (type: BufferEventType) => () => events.push(type);

      bufferManager.on(BufferEventType.TRANSFORM_START, eventHandler(BufferEventType.TRANSFORM_START));
      bufferManager.on(BufferEventType.TRANSFORM_PROGRESS, eventHandler(BufferEventType.TRANSFORM_PROGRESS));
      bufferManager.on(BufferEventType.TRANSFORM_COMPLETE, eventHandler(BufferEventType.TRANSFORM_COMPLETE));

      const stream = bufferManager.createReadableStream(testData);
      await bufferManager.streamToBuffer(stream);

      expect(events).toContain(BufferEventType.TRANSFORM_START);
      expect(events).toContain(BufferEventType.TRANSFORM_PROGRESS);
      expect(events).toContain(BufferEventType.TRANSFORM_COMPLETE);
      expect(events.indexOf(BufferEventType.TRANSFORM_START))
        .toBeLessThan(events.indexOf(BufferEventType.TRANSFORM_COMPLETE));
    });

    it('should emit error events when appropriate', () => {
      const errorHandler = jest.fn();
      bufferManager.on(BufferEventType.TRANSFORM_ERROR, errorHandler);

      const writableStream = bufferManager.createWritableStream();
      const error = new Error('Write error');
      
      writableStream.emit('error', error);
      expect(errorHandler).toHaveBeenCalledWith(error);
    });
  });

  describe('Performance', () => {
    it('should handle large buffers efficiently', async () => {
      const largeData = Buffer.alloc(1024 * 1024); // 1MB
      largeData.fill('x');

      const start = Date.now();
      const stream = bufferManager.createReadableStream(largeData, { chunkSize: 64 * 1024 });
      const result = await bufferManager.streamToBuffer(stream);

      const end = Date.now();
      const duration = end - start;

      expect(result.length).toBe(largeData.length);
      expect(duration).toBeLessThan(1000); // Should process 1MB in less than 1 second
    });

    it('should respect highWaterMark settings', async () => {
      const data = Buffer.alloc(1024 * 1024); // 1MB
      const highWaterMark = 16 * 1024; // 16KB

      const stream = bufferManager.createReadableStream(data, { highWaterMark });
      expect((stream as any)._readableState.highWaterMark).toBe(highWaterMark);
    });
  });
}); 