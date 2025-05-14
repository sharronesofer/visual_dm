import { MediaAsset, MediaAssetModel } from '../MediaAsset';

describe('MediaAssetModel', () => {
  const baseData = {
    id: 'uuid-789',
    createdAt: new Date(),
    updatedAt: new Date(),
    isActive: true,
    title: 'Sample Image',
    fileUrl: 'https://example.com/image.png',
    fileType: 'image/png',
    fileSize: 1024,
  };

  it('should instantiate with valid data', () => {
    const asset = new MediaAssetModel(baseData);
    expect(asset.title).toBe('Sample Image');
    expect(asset.fileType).toBe('image/png');
    expect(asset.isActive).toBe(true);
  });

  it('should throw for missing required fields', () => {
    expect(() => new MediaAssetModel({ ...baseData, title: '' })).toThrow();
    expect(() => new MediaAssetModel({ ...baseData, fileUrl: '' })).toThrow();
    expect(() => new MediaAssetModel({ ...baseData, fileType: '' })).toThrow();
    expect(() => new MediaAssetModel({ ...baseData, fileSize: -1 })).toThrow();
  });

  it('should throw for unsupported fileType', () => {
    expect(() => new MediaAssetModel({ ...baseData, fileType: 'application/zip' })).toThrow();
  });

  it('should validate dimensions if provided', () => {
    expect(() => new MediaAssetModel({ ...baseData, dimensions: { width: 100, height: 200 } })).not.toThrow();
    // @ts-expect-error
    expect(() => new MediaAssetModel({ ...baseData, dimensions: { width: '100', height: 200 } })).toThrow();
  });
}); 