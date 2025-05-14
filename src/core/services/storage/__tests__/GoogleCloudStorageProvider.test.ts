import { GoogleCloudStorageProvider } from '../GoogleCloudStorageProvider';
import { StorageError } from '../../../interfaces/storage/StorageProvider';

describe('GoogleCloudStorageProvider', () => {
  const bucketName = 'test-bucket';
  let provider: GoogleCloudStorageProvider;

  beforeEach(() => {
    provider = new GoogleCloudStorageProvider(bucketName, { keyFilename: 'fake.json', projectId: 'test' });
  });

  it('should instantiate without error', () => {
    expect(provider).toBeInstanceOf(GoogleCloudStorageProvider);
  });

  it('should throw NOT_SUPPORTED for save', async () => {
    await expect(provider.save(Buffer.from('data'), 'file.txt')).rejects.toThrow(StorageError);
  });

  it('should throw NOT_SUPPORTED for get', async () => {
    await expect(provider.get('file.txt')).rejects.toThrow(StorageError);
  });

  it('should throw NOT_SUPPORTED for delete', async () => {
    await expect(provider.delete('file.txt')).rejects.toThrow(StorageError);
  });

  it('should throw NOT_SUPPORTED for exists', async () => {
    await expect(provider.exists('file.txt')).rejects.toThrow(StorageError);
  });

  it('should throw NOT_SUPPORTED for getUrl', async () => {
    await expect(provider.getUrl('file.txt')).rejects.toThrow(StorageError);
  });

  it('should throw NOT_SUPPORTED for list', async () => {
    await expect(provider.list('')).rejects.toThrow(StorageError);
  });

  it('should throw NOT_SUPPORTED for copy', async () => {
    await expect(provider.copy('a.txt', 'b.txt')).rejects.toThrow(StorageError);
  });

  it('should throw NOT_SUPPORTED for move', async () => {
    await expect(provider.move('a.txt', 'b.txt')).rejects.toThrow(StorageError);
  });

  it('should throw NOT_SUPPORTED for getMetadata', async () => {
    await expect(provider.getMetadata('file.txt')).rejects.toThrow(StorageError);
  });

  it('should throw NOT_SUPPORTED for updateMetadata', async () => {
    await expect(provider.updateMetadata('file.txt', {})).rejects.toThrow(StorageError);
  });
}); 