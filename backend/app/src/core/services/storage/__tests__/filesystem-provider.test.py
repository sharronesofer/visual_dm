from typing import Any


describe('FileSystemStorageProvider', () => {
  const testDir = join(process.cwd(), 'test-storage')
  let provider: FileSystemStorageProvider
  beforeEach(async () => {
    await fs.rm(testDir, { recursive: true, force: true })
    provider = new FileSystemStorageProvider({ basePath: testDir })
  })
  afterEach(async () => {
    await fs.rm(testDir, { recursive: true, force: true })
  })
  describe('constructor', () => {
    it('should create base directory if it does not exist', async () => {
      const exists = await fs.access(testDir).then(() => true).catch(() => false)
      expect(exists).toBe(true)
    })
    it('should use default permissions if not specified', () => {
      const provider = new FileSystemStorageProvider({ basePath: testDir })
      expect(provider['options'].permissions).toBe(0o644)
    })
    it('should use custom permissions if specified', () => {
      const provider = new FileSystemStorageProvider({
        basePath: testDir,
        permissions: 0o600
      })
      expect(provider['options'].permissions).toBe(0o600)
    })
  })
  describe('save', () => {
    it('should save string data to a file', async () => {
      const data = 'test content'
      const result = await provider.save('test.txt', data)
      expect(result.path).toBe('test.txt')
      expect(result.metadata.size).toBe(Buffer.from(data).length)
      expect(result.metadata.mimeType).toBe('text/plain')
      const content = await fs.readFile(join(testDir, 'test.txt'), 'utf8')
      expect(content).toBe(data)
    })
    it('should save buffer data to a file', async () => {
      const data = Buffer.from([1, 2, 3, 4])
      const result = await provider.save('test.bin', data)
      expect(result.path).toBe('test.bin')
      expect(result.metadata.size).toBe(data.length)
      const content = await fs.readFile(join(testDir, 'test.bin'))
      expect(Buffer.compare(content, data)).toBe(0)
    })
    it('should create nested directories as needed', async () => {
      await provider.save('nested/path/test.txt', 'test')
      const exists = await fs.access(join(testDir, 'nested/path/test.txt'))
        .then(() => true)
        .catch(() => false)
      expect(exists).toBe(true)
    })
    it('should throw if file exists and overwrite is false', async () => {
      await provider.save('test.txt', 'original')
      await expect(provider.save('test.txt', 'new')).rejects.toThrow(FileExistsError)
    })
    it('should overwrite existing file when overwrite is true', async () => {
      await provider.save('test.txt', 'original')
      await provider.save('test.txt', 'new', { overwrite: true })
      const content = await fs.readFile(join(testDir, 'test.txt'), 'utf8')
      expect(content).toBe('new')
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
    it('should return file URL', () => {
      const url = provider.getUrl('test.txt')
      expect(url).toBe(`file:
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
    it('should handle cross-device moves', async () => {
      const originalRename = fs.rename
      fs.rename = jest.fn().mockRejectedValue(Object.assign(new Error(), { code: 'EXDEV' }))
      try {
        await provider.move('source.txt', 'target.txt')
        expect(await provider.exists('source.txt')).toBe(false)
        expect(await provider.exists('target.txt')).toBe(true)
        const content = await provider.read('target.txt')
        expect(content.toString()).toBe('test content')
      } finally {
        fs.rename = originalRename
      }
    })
  })
}) 