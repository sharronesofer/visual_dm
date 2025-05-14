import { CollectionService } from '../CollectionService';
import { Collection } from '../../interfaces/Collection';
import { Repository } from '../../interfaces/Repository';
import { ValidationError } from '../../utils/errors';

class TestRepository implements Repository<Collection> {
  private items: Collection[] = [];
  private nextId = 1;

  async findById(id: string | number): Promise<Collection | null> {
    return this.items.find(item => item.id === id) || null;
  }

  async findAll(): Promise<Collection[]> {
    return [...this.items];
  }

  async create(entity: Omit<Collection, 'id' | 'createdAt' | 'updatedAt'>): Promise<Collection> {
    const newEntity: Collection = {
      id: this.nextId++,
      createdAt: new Date(),
      updatedAt: new Date(),
      ...entity,
    };
    this.items.push(newEntity);
    return newEntity;
  }

  async update(id: string | number, entity: Partial<Collection>): Promise<Collection | null> {
    const index = this.items.findIndex(item => item.id === id);
    if (index === -1) return null;

    const updatedEntity: Collection = {
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

describe('CollectionService', () => {
  let repository: TestRepository;
  let service: CollectionService;

  beforeEach(() => {
    repository = new TestRepository();
    service = new CollectionService(repository);
  });

  describe('createCollection', () => {
    it('should create a new collection with minimal data', async () => {
      const result = await service.createCollection({ name: 'Test Collection' });
      expect(result).toMatchObject({
        id: expect.any(Number),
        name: 'Test Collection',
        assets: [],
        tags: [],
      });
    });

    it('should create a collection with all data', async () => {
      const result = await service.createCollection({
        name: 'Test Collection',
        description: 'Test Description',
        tags: ['tag1', 'tag2'],
      });
      expect(result).toMatchObject({
        id: expect.any(Number),
        name: 'Test Collection',
        description: 'Test Description',
        tags: ['tag1', 'tag2'],
        assets: [],
      });
    });

    it('should throw ValidationError when name is missing', async () => {
      await expect(service.createCollection({} as any)).rejects.toThrow(ValidationError);
    });

    it('should throw ValidationError when name is too long', async () => {
      const longName = 'a'.repeat(101);
      await expect(service.createCollection({ name: longName })).rejects.toThrow(ValidationError);
    });

    it('should throw ValidationError when description is too long', async () => {
      const longDesc = 'a'.repeat(501);
      await expect(service.createCollection({
        name: 'Test',
        description: longDesc,
      })).rejects.toThrow(ValidationError);
    });

    it('should throw ValidationError when too many tags', async () => {
      const manyTags = Array.from({ length: 21 }, (_, i) => `tag${i}`);
      await expect(service.createCollection({
        name: 'Test',
        tags: manyTags,
      })).rejects.toThrow(ValidationError);
    });
  });

  describe('addAssetToCollection', () => {
    it('should return null for non-existent collection', async () => {
      const result = await service.addAssetToCollection(1, 1);
      expect(result).toBeNull();
    });

    it('should add asset to collection', async () => {
      const collection = await service.createCollection({ name: 'Test' });
      const result = await service.addAssetToCollection(collection.id, 1);
      expect(result?.assets).toHaveLength(1);
      expect(result?.assets[0].id).toBe(1);
    });

    it('should not add duplicate asset', async () => {
      const collection = await service.createCollection({ name: 'Test' });
      await service.addAssetToCollection(collection.id, 1);
      const result = await service.addAssetToCollection(collection.id, 1);
      expect(result?.assets).toHaveLength(1);
    });
  });

  describe('removeAssetFromCollection', () => {
    it('should return null for non-existent collection', async () => {
      const result = await service.removeAssetFromCollection(1, 1);
      expect(result).toBeNull();
    });

    it('should remove asset from collection', async () => {
      const collection = await service.createCollection({ name: 'Test' });
      await service.addAssetToCollection(collection.id, 1);
      const result = await service.removeAssetFromCollection(collection.id, 1);
      expect(result?.assets).toHaveLength(0);
    });

    it('should handle non-existent asset gracefully', async () => {
      const collection = await service.createCollection({ name: 'Test' });
      const result = await service.removeAssetFromCollection(collection.id, 1);
      expect(result?.assets).toHaveLength(0);
    });
  });

  describe('updateCollectionTags', () => {
    it('should return null for non-existent collection', async () => {
      const result = await service.updateCollectionTags(1, ['tag1']);
      expect(result).toBeNull();
    });

    it('should update collection tags', async () => {
      const collection = await service.createCollection({ name: 'Test' });
      const result = await service.updateCollectionTags(collection.id, ['tag1', 'tag2']);
      expect(result?.tags).toEqual(['tag1', 'tag2']);
    });

    it('should throw ValidationError when too many tags', async () => {
      const collection = await service.createCollection({ name: 'Test' });
      const manyTags = Array.from({ length: 21 }, (_, i) => `tag${i}`);
      await expect(service.updateCollectionTags(collection.id, manyTags)).rejects.toThrow(ValidationError);
    });
  });
}); 