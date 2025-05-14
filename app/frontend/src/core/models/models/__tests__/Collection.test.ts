import { Collection, CollectionModel } from '../Collection';

describe('CollectionModel', () => {
  const baseData: Collection = {
    id: 'col-1',
    createdAt: new Date(),
    updatedAt: new Date(),
    isActive: true,
    name: 'My Collection',
    mediaAssets: [],
    visibility: 'public',
  };

  it('should instantiate with valid data', () => {
    const collection = new CollectionModel(baseData);
    expect(collection.name).toBe('My Collection');
    expect(collection.visibility).toBe('public');
    expect(collection.mediaAssets).toEqual([]);
  });

  it('should add and remove media asset IDs', () => {
    const collection = new CollectionModel(baseData);
    collection.addMediaAsset('asset-1');
    expect(collection.mediaAssets).toContain('asset-1');
    collection.addMediaAsset('asset-1'); // should not duplicate
    expect(collection.mediaAssets.filter(id => id === 'asset-1').length).toBe(1);
    expect(collection.removeMediaAsset('asset-1')).toBe(true);
    expect(collection.mediaAssets).not.toContain('asset-1');
    expect(collection.removeMediaAsset('asset-1')).toBe(false);
  });

  it('should manage metadata fields', () => {
    const collection = new CollectionModel(baseData);
    collection.setMetadata('foo', 123);
    expect(collection.getMetadata('foo')).toBe(123);
    expect(collection.getMetadata('bar')).toBeUndefined();
  });

  it('should validate required fields and throw on invalid data', () => {
    expect(() => new CollectionModel({ ...baseData, name: '' })).toThrow();
    expect(() => new CollectionModel({ ...baseData, visibility: 'invalid' as any })).toThrow();
    expect(() => new CollectionModel({ ...baseData, mediaAssets: [123 as any] })).toThrow();
    expect(() => new CollectionModel({ ...baseData, mediaAssets: [''] })).toThrow();
  });
}); 