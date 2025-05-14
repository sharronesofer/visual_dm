import { ThumbnailService } from '../index';
import { ThumbnailOptions, ThumbnailResult } from '../types';

describe('ThumbnailService', () => {
  let service: ThumbnailService;

  beforeEach(() => {
    service = new ThumbnailService();
  });

  it('should return error for unsupported mime type', async () => {
    const result = await service.generateThumbnail('file.txt', 'text/plain');
    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.error.code).toBe('UNSUPPORTED_TYPE');
    }
  });

  it('should call the correct generator for image', async () => {
    const spy = jest.spyOn(service as any, 'getGenerator').mockReturnValue({
      generate: jest.fn().mockResolvedValue({ buffer: Buffer.from([]), width: 1, height: 1, format: 'jpeg', size: 0 }),
      supports: jest.fn().mockReturnValue(true),
    });
    const result = await service.generateThumbnail('file.jpg', 'image/jpeg');
    expect(result.success).toBe(true);
    spy.mockRestore();
  });

  it('should handle generator errors gracefully', async () => {
    const spy = jest.spyOn(service as any, 'getGenerator').mockReturnValue({
      generate: jest.fn().mockRejectedValue(new Error('fail')),
      supports: jest.fn().mockReturnValue(true),
    });
    const result = await service.generateThumbnail('file.jpg', 'image/jpeg');
    expect(result.success).toBe(false);
    expect(result.error.code).toBe('INTERNAL_ERROR');
    spy.mockRestore();
  });

  // Add more tests for video, audio, document as needed, mocking their generators
}); 