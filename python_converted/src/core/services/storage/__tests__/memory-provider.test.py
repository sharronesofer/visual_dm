from typing import Any


describe('MemoryStorageProvider', () => {
  let provider: MemoryStorageProvider
  beforeEach(() => {
    provider = new MemoryStorageProvider()
  })
  afterEach(() => {
    provider.clear()
  })
  describe('constructor', () => {
    it('should use default options if none provided', () => {
      const provider = new MemoryStorageProvider()
      expect(provider['options'].basePath).toBe(process.cwd())
      expect(provider['options'].operationTimeout).toBeUndefined()
    })
    it('should use provided options', () => {
      const provider = new MemoryStorageProvider({
        basePath: '/custom/path',
        operationTimeout: 5000
      })
      expect(provider['options'].basePath).toBe('/custom/path')
      expect(provider['options'].operationTimeout).toBe(5000)
    })
  })
  describe('save', () => {
    it('should save string data', async () => {
      const data = 'test content'
      const result = await provider.save('test.txt', data)
      expect(result.path).toBe('test.txt')
      expect(result.metadata.size).toBe(Buffer.from(data).length)
      expect(result.metadata.mimeType).toBe('text/plain')
      const content = await provider.read('test.txt')
      expect(content.toString()).toBe(data)
    })
    it('should save buffer data', async () => {
      const data = Buffer.from([1, 2, 3, 4])
      const result = await provider.save('test.bin', data)
      expect(result.path).toBe('test.bin')
      expect(result.metadata.size).toBe(data.length)
      const content = await provider.read('test.bin')
      expect(Buffer.compare(content, data)).toBe(0)
    })
    it('should handle nested paths', async () => {
      await provider.save('nested/path/test.txt', 'test')
      expect(await provider.exists('nested/path/test.txt')).toBe(true)
    })
    it('should throw if file exists and overwrite is false', async () => {
      await provider.save('test.txt', 'original')
      await expect(provider.save('test.txt', 'new')).rejects.toThrow(FileExistsError)
    })
    it('should overwrite existing file when overwrite is true', async () => {
      await provider.save('test.txt', 'original')
      await provider.save('test.txt', 'new', { overwrite: true })
      const content = await provider.read('test.txt')
      expect(content.toString()).toBe('new')
    })
  })
  describe('read', () => {
    it('should read file contents', async () => {
      const data = 'test content'
      await provider.save('test.txt', data)
      const content = await provider.read('test.txt')
      expect(content.toString()).toBe(data)
    })
    it('should throw FileNotFoundError for non-existent files', async () => {
      await expect(provider.read('missing.txt')).rejects.toThrow(FileNotFoundError)
    })
  })
  describe('delete', () => {
    it('should delete existing file', async () => {
      await provider.save('test.txt', 'test')
      const result = await provider.delete('test.txt')
      expect(result).toBe(true)
      expect(await provider.exists('test.txt')).toBe(false)
    })
    it('should return false for non-existent files', async () => {
      const result = await provider.delete('missing.txt')
      expect(result).toBe(false)
    })
  })
  describe('exists', () => {
    it('should return true for existing files', async () => {
      await provider.save('test.txt', 'test')
      expect(await provider.exists('test.txt')).toBe(true)
    })
    it('should return false for non-existent files', async () => {
      expect(await provider.exists('missing.txt')).toBe(false)
    })
  })
  describe('list', () => {
    beforeEach(async () => {
      await provider.save('file1.txt', 'test')
      await provider.save('nested/file2.txt', 'test')
      await provider.save('nested/deep/file3.txt', 'test')
    })
    it('should list files in root directory (non-recursive)', async () => {
      const files = await provider.list('')
      expect(files).toEqual(['file1.txt'])
    })
    it('should list files in nested directory (non-recursive)', async () => {
      const files = await provider.list('nested')
      expect(files).toEqual(['nested/file2.txt'])
    })
    it('should list all files recursively', async () => {
      const files = await provider.list('', true)
      expect(files.sort()).toEqual([
        'file1.txt',
        'nested/file2.txt',
        'nested/deep/file3.txt'
      ].sort())
    })
    it('should return empty array for non-existent directory', async () => {
      const files = await provider.list('missing')
      expect(files).toEqual([])
    })
  })
  describe('getMetadata', () => {
    it('should return file metadata', async () => {
      const data = 'test content'
      await provider.save('test.txt', data)
      const metadata = await provider.getMetadata('test.txt')
      expect(metadata.name).toBe('test.txt')
      expect(metadata.size).toBe(Buffer.from(data).length)
      expect(metadata.mimeType).toBe('text/plain')
      expect(metadata.createdAt).toBeInstanceOf(Date)
      expect(metadata.modifiedAt).toBeInstanceOf(Date)
    })
    it('should throw FileNotFoundError for non-existent files', async () => {
      await expect(provider.getMetadata('missing.txt')).rejects.toThrow(FileNotFoundError)
    })
  })
  describe('getUrl', () => {
    it('should return memory URL', () => {
      const url = provider.getUrl('test.txt')
      expect(url).toBe('memory:
    })
  })
  describe('copy', () => {
    beforeEach(async () => {
      await provider.save('source.txt', 'test content')
    })
    it('should copy file to new location', async () => {
      const result = await provider.copy('source.txt', 'target.txt')
      expect(result.path).toBe('target.txt')
      expect(await provider.exists('source.txt')).toBe(true)
      expect(await provider.exists('target.txt')).toBe(true)
      const sourceContent = await provider.read('source.txt')
      const targetContent = await provider.read('target.txt')
      expect(sourceContent.toString()).toBe(targetContent.toString())
    })
    it('should throw FileNotFoundError if source does not exist', async () => {
      await expect(provider.copy('missing.txt', 'target.txt')).rejects.toThrow(FileNotFoundError)
    })
    it('should throw FileExistsError if target exists and overwrite is false', async () => {
      await provider.save('target.txt', 'original')
      await expect(provider.copy('source.txt', 'target.txt')).rejects.toThrow(FileExistsError)
    })
    it('should overwrite target when overwrite is true', async () => {
      await provider.save('target.txt', 'original')
      await provider.copy('source.txt', 'target.txt', { overwrite: true })
      const content = await provider.read('target.txt')
      expect(content.toString()).toBe('test content')
    })
  })
  describe('move', () => {
    beforeEach(async () => {
      await provider.save('source.txt', 'test content')
    })
    it('should move file to new location', async () => {
      const result = await provider.move('source.txt', 'target.txt')
      expect(result.path).toBe('target.txt')
      expect(await provider.exists('source.txt')).toBe(false)
      expect(await provider.exists('target.txt')).toBe(true)
      const content = await provider.read('target.txt')
      expect(content.toString()).toBe('test content')
    })
    it('should throw FileNotFoundError if source does not exist', async () => {
      await expect(provider.move('missing.txt', 'target.txt')).rejects.toThrow(FileNotFoundError)
    })
    it('should throw FileExistsError if target exists and overwrite is false', async () => {
      await provider.save('target.txt', 'original')
      await expect(provider.move('source.txt', 'target.txt')).rejects.toThrow(FileExistsError)
    })
    it('should overwrite target when overwrite is true', async () => {
      await provider.save('target.txt', 'original')
      await provider.move('source.txt', 'target.txt', { overwrite: true })
      expect(await provider.exists('source.txt')).toBe(false)
      const content = await provider.read('target.txt')
      expect(content.toString()).toBe('test content')
    })
  })
  describe('clear', () => {
    it('should remove all files', async () => {
      await provider.save('file1.txt', 'test')
      await provider.save('file2.txt', 'test')
      provider.clear()
      expect(await provider.exists('file1.txt')).toBe(false)
      expect(await provider.exists('file2.txt')).toBe(false)
      expect(await provider.list('', true)).toEqual([])
    })
  })
  describe('timeout handling', () => {
    it('should timeout long operations', async () => {
      const provider = new MemoryStorageProvider({
        operationTimeout: 50
      })
      jest.spyOn(provider as any, 'withTimeout').mockImplementationOnce(async () => {
        await new Promise(resolve => setTimeout(resolve, 100))
      })
      await expect(provider.read('test.txt')).rejects.toThrow(StorageTimeoutError)
    })
  })
  describe('createDirectory', () => {
    it('should create a directory', async () => {
      const result = await provider.createDirectory('test-dir')
      expect(result.success).toBe(true)
      expect(result.path).toBe('test-dir')
      const exists = await provider.exists('test-dir')
      expect(exists).toBe(true)
    })
    it('should fail if directory already exists', async () => {
      await provider.createDirectory('test-dir')
      const result = await provider.createDirectory('test-dir')
      expect(result.success).toBe(false)
      expect(result.error?.name).toBe('StorageError')
      expect(result.error?.code).toBe('DIR_EXISTS')
    })
  })
  describe('removeDirectory', () => {
    beforeEach(async () => {
      await provider.createDirectory('test-dir')
      await provider.save('test-dir/file1.txt', 'test')
      await provider.save('test-dir/file2.txt', 'test')
    })
    it('should remove empty directory', async () => {
      const emptyDir = 'empty-dir'
      await provider.createDirectory(emptyDir)
      const result = await provider.removeDirectory(emptyDir)
      expect(result.success).toBe(true)
      const exists = await provider.exists(emptyDir)
      expect(exists).toBe(false)
    })
    it('should remove directory and contents when failIfNotEmpty is false', async () => {
      const result = await provider.removeDirectory('test-dir')
      expect(result.success).toBe(true)
      const exists = await provider.exists('test-dir')
      expect(exists).toBe(false)
      const file1Exists = await provider.exists('test-dir/file1.txt')
      const file2Exists = await provider.exists('test-dir/file2.txt')
      expect(file1Exists).toBe(false)
      expect(file2Exists).toBe(false)
    })
    it('should fail to remove non-empty directory when failIfNotEmpty is true', async () => {
      const result = await provider.removeDirectory('test-dir', { failIfNotEmpty: true })
      expect(result.success).toBe(false)
      expect(result.error?.name).toBe('StorageError')
      expect(result.error?.code).toBe('DIR_NOT_EMPTY')
      const exists = await provider.exists('test-dir')
      expect(exists).toBe(true)
    })
    it('should fail if directory does not exist', async () => {
      const result = await provider.removeDirectory('missing-dir')
      expect(result.success).toBe(false)
      expect(result.error?.name).toBe('FileNotFoundError')
    })
  })
  describe('listDirectory', () => {
    beforeEach(async () => {
      await provider.createDirectory('test-dir')
      await provider.save('test-dir/file1.txt', 'test')
      await provider.save('test-dir/file2.txt', 'test')
      await provider.createDirectory('test-dir/subdir')
      await provider.save('test-dir/subdir/file3.txt', 'test')
    })
    it('should list directory contents non-recursively', async () => {
      const files = await provider.listDirectory('test-dir')
      expect(files.sort()).toEqual([
        'test-dir/file1.txt',
        'test-dir/file2.txt',
        'test-dir/subdir'
      ].sort())
    })
    it('should list directory contents recursively', async () => {
      const files = await provider.listDirectory('test-dir', { recursive: true })
      expect(files.sort()).toEqual([
        'test-dir/file1.txt',
        'test-dir/file2.txt',
        'test-dir/subdir',
        'test-dir/subdir/file3.txt'
      ].sort())
    })
    it('should list only files when includeDirectories is false', async () => {
      const files = await provider.listDirectory('test-dir', { includeDirectories: false })
      expect(files.sort()).toEqual([
        'test-dir/file1.txt',
        'test-dir/file2.txt'
      ].sort())
    })
    it('should apply filter when provided', async () => {
      const files = await provider.listDirectory('test-dir', {
        filter: path => path.endsWith('.txt'),
        recursive: true
      })
      expect(files.sort()).toEqual([
        'test-dir/file1.txt',
        'test-dir/file2.txt',
        'test-dir/subdir/file3.txt'
      ].sort())
    })
    it('should throw FileNotFoundError if directory does not exist', async () => {
      await expect(provider.listDirectory('missing-dir')).rejects.toThrow(FileNotFoundError)
    })
  })
}) 