import { MediaService } from '../MediaService';
import { MediaAsset } from '../../interfaces/MediaAsset';
import { Repository } from '../../interfaces/Repository';
import { ValidationError } from '../../utils/errors';

class TestRepository implements Repository<MediaAsset> {
  private items: MediaAsset[] = [];
  private nextId = 1;

  async findById(id: string | number): Promise<MediaAsset | null> {
    return this.items.find(item => item.id === id) || null;
  }

  async findAll(): Promise<MediaAsset[]> {
    return [...this.items];
  }

  async create(entity: Omit<MediaAsset, 'id' | 'createdAt' | 'updatedAt'>): Promise<MediaAsset> {
    const newEntity: MediaAsset = {
      id: this.nextId++,
      createdAt: new Date(),
      updatedAt: new Date(),
      ...entity,
    };
    this.items.push(newEntity);
    return newEntity;
  }

  async update(id: string | number, entity: Partial<MediaAsset>): Promise<MediaAsset | null> {
    const index = this.items.findIndex(item => item.id === id);
    if (index === -1) return null;

    const updatedEntity: MediaAsset = {
      ...this.items[index],
      ...entity,
      updatedAt: new Date(),
    };
    this.items[index] = updatedEntity;
    return updatedEntity;
  }

  async delete(id: string | number): Promise<boolean> {
    const index = this.items.findIndex(item => item.id === id);
    if (index === -1) return false;

    this.items.splice(index, 1);
    return true;
  }
}

describe('MediaService', () => {
  let repository: TestRepository;
  let service: MediaService;

  beforeEach(() => {
    repository = new TestRepository();
    service = new MediaService(repository);
  });

  describe('uploadAsset', () => {
    const validFile = {
      filename: 'test.jpg',
      path: '/path/to/test.jpg',
      mimeType: 'image/jpeg',
      size: 1024,
    };

    it('should create a new media asset', async () => {
      const result = await service.uploadAsset(validFile);
      expect(result).toMatchObject({
        id: expect.any(Number),
        filename: 'test.jpg',
        path: '/path/to/test.jpg',
        mimeType: 'image/jpeg',
        size: 1024,
        metadata: {},
      });
    });

    it('should throw ValidationError when filename is missing', async () => {
      const invalidFile = { ...validFile, filename: undefined };
      await expect(service.uploadAsset(invalidFile as any)).rejects.toThrow(ValidationError);
    });

    it('should throw ValidationError when path is missing', async () => {
      const invalidFile = { ...validFile, path: undefined };
      await expect(service.uploadAsset(invalidFile as any)).rejects.toThrow(ValidationError);
    });

    it('should throw ValidationError when mimeType is missing', async () => {
      const invalidFile = { ...validFile, mimeType: undefined };
      await expect(service.uploadAsset(invalidFile as any)).rejects.toThrow(ValidationError);
    });

    it('should throw ValidationError when size is missing', async () => {
      const invalidFile = { ...validFile, size: undefined };
      await expect(service.uploadAsset(invalidFile as any)).rejects.toThrow(ValidationError);
    });
  });

  describe('generateThumbnail', () => {
    it('should return null for non-existent asset', async () => {
      const result = await service.generateThumbnail(1);
      expect(result).toBeNull();
    });

    it('should update asset with thumbnail URL', async () => {
      const asset = await service.uploadAsset({
        filename: 'test.jpg',
        path: '/path/to/test.jpg',
        mimeType: 'image/jpeg',
        size: 1024,
      });

      const result = await service.generateThumbnail(asset.id);
      expect(result).toMatchObject({
        id: asset.id,
        thumbnailUrl: expect.stringContaining(String(asset.id)),
      });
    });
  });

  describe('deleteAsset', () => {
    it('should return false for non-existent asset', async () => {
      const result = await service.deleteAsset(1);
      expect(result).toBe(false);
    });

    it('should delete asset and return true', async () => {
      const asset = await service.uploadAsset({
        filename: 'test.jpg',
        path: '/path/to/test.jpg',
        mimeType: 'image/jpeg',
        size: 1024,
      });

      const result = await service.deleteAsset(asset.id);
      expect(result).toBe(true);

      const found = await service.findById(asset.id);
      expect(found).toBeNull();
    });
  });
}); 