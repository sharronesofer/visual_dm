from typing import Any



describe('FileSystemStorageProvider', () => {
  let provider: FileSystemStorageProvider
  let rootDir: str
  let testFile: str
  let testData: Buffer
  beforeEach(async () => {
    rootDir = await fs.mkdtemp(path.join(os.tmpdir(), 'storage-test-'))
    const config: FileSystemStorageConfig = {
      rootDir,
      baseUrl: 'http:
      createDirs: true
    }
    provider = new FileSystemStorageProvider(config)
    testFile = 'test/file.txt'
    testData = Buffer.from('Hello, World!')
  })
  afterEach(async () => {
    await fs.rm(rootDir, { recursive: true, force: true })
  })
  describe('save', () => {
    it('should save buffer data correctly', async () => {
      const result = await provider.save(testData, testFile)
      expect(result.path).toBe(testFile)
      expect(result.size).toBe(testData.length)
      const savedData = await fs.readFile(path.join(rootDir, testFile))
      expect(savedData).toEqual(testData)
    })
    it('should save stream data correctly', async () => {
      const stream = Readable.from(testData)
      const result = await provider.save(stream, testFile)
      expect(result.path).toBe(testFile)
      expect(result.size).toBeGreaterThan(0)
      const savedData = await fs.readFile(path.join(rootDir, testFile))
      expect(savedData).toEqual(testData)
    })
    it('should save metadata if provided', async () => {
      const metadata = { contentType: 'text/plain', author: 'test' }
      await provider.save(testData, testFile, { metadata })
      const savedMetadata = await provider.getMetadata(testFile)
      expect(savedMetadata).toEqual(metadata)
    })
    it('should create parent directories if needed', async () => {
      const deepFile = 'deep/nested/path/file.txt'
      await provider.save(testData, deepFile)
      const exists = await fs.access(path.join(rootDir, 'deep/nested/path'))
        .then(() => true)
        .catch(() => false)
      expect(exists).toBe(true)
    })
  })
  describe('get', () => {
    beforeEach(async () => {
      await provider.save(testData, testFile)
    })
    it('should retrieve file as buffer for small files', async () => {
      const data = await provider.get(testFile)
      expect(Buffer.isBuffer(data)).toBe(true)
      expect(data).toEqual(testData)
    })
    it('should retrieve file as stream for large files', async () => {
      const largeData = Buffer.alloc(2 * 1024 * 1024) 
      await provider.save(largeData, 'large.bin')
      const data = await provider.get('large.bin')
      expect(data).toBeInstanceOf(Readable)
    })
    it('should throw NOT_FOUND for non-existent files', async () => {
      await expect(provider.get('nonexistent.txt'))
        .rejects
        .toThrow(StorageError)
    })
  })
  describe('delete', () => {
    beforeEach(async () => {
      await provider.save(testData, testFile)
    })
    it('should delete existing file', async () => {
      const result = await provider.delete(testFile)
      expect(result).toBe(true)
      const exists = await provider.exists(testFile)
      expect(exists).toBe(false)
    })
    it('should return false for non-existent file', async () => {
      const result = await provider.delete('nonexistent.txt')
      expect(result).toBe(false)
    })
    it('should delete metadata file if it exists', async () => {
      const metadata = { test: 'value' }
      await provider.save(testData, testFile, { metadata })
      await provider.delete(testFile)
      const metadataExists = await fs.access(path.join(rootDir, `${testFile}.metadata.json`))
        .then(() => true)
        .catch(() => false)
      expect(metadataExists).toBe(false)
    })
  })
  describe('exists', () => {
    it('should return true for existing file', async () => {
      await provider.save(testData, testFile)
      const exists = await provider.exists(testFile)
      expect(exists).toBe(true)
    })
    it('should return false for non-existent file', async () => {
      const exists = await provider.exists('nonexistent.txt')
      expect(exists).toBe(false)
    })
  })
  describe('getUrl', () => {
    it('should generate correct URL', async () => {
      const url = await provider.getUrl(testFile)
      expect(url).toBe('http:
    })
    it('should throw NOT_SUPPORTED if baseUrl not configured', async () => {
      const localProvider = new FileSystemStorageProvider({ rootDir })
      await expect(localProvider.getUrl(testFile))
        .rejects
        .toThrow(new StorageError(StorageErrorCode.NOT_SUPPORTED, expect.any(String)))
    })
  })
  describe('list', () => {
    beforeEach(async () => {
      await provider.save(testData, 'file1.txt')
      await provider.save(testData, 'dir/file2.txt')
      await provider.save(testData, 'dir/subdir/file3.txt')
    })
    it('should list files in root directory', async () => {
      const items = await provider.list()
      expect(items).toHaveLength(2) 
      expect(items.find(i => i.path === 'file1.txt')).toBeDefined()
      expect(items.find(i => i.path === 'dir' && i.isDirectory)).toBeDefined()
    })
    it('should list files in subdirectory', async () => {
      const items = await provider.list('dir')
      expect(items).toHaveLength(2) 
      expect(items.find(i => i.path === 'dir/file2.txt')).toBeDefined()
      expect(items.find(i => i.path === 'dir/subdir' && i.isDirectory)).toBeDefined()
    })
    it('should return empty array for non-existent directory', async () => {
      const items = await provider.list('nonexistent')
      expect(items).toHaveLength(0)
    })
  })
  describe('copy and move', () => {
    beforeEach(async () => {
      await provider.save(testData, testFile)
    })
    it('should copy file correctly', async () => {
      const destPath = 'copy/dest.txt'
      const result = await provider.copy(testFile, destPath)
      expect(result).toBe(true)
      const sourceExists = await provider.exists(testFile)
      const destExists = await provider.exists(destPath)
      expect(sourceExists).toBe(true)
      expect(destExists).toBe(true)
      const copiedData = await provider.get(destPath)
      expect(copiedData).toEqual(testData)
    })
    it('should move file correctly', async () => {
      const destPath = 'move/dest.txt'
      const result = await provider.move(testFile, destPath)
      expect(result).toBe(true)
      const sourceExists = await provider.exists(testFile)
      const destExists = await provider.exists(destPath)
      expect(sourceExists).toBe(false)
      expect(destExists).toBe(true)
      const movedData = await provider.get(destPath)
      expect(movedData).toEqual(testData)
    })
  })
  describe('metadata', () => {
    const metadata = { contentType: 'text/plain', author: 'test' }
    beforeEach(async () => {
      await provider.save(testData, testFile, { metadata })
    })
    it('should get metadata correctly', async () => {
      const result = await provider.getMetadata(testFile)
      expect(result).toEqual(metadata)
    })
    it('should return empty object for file without metadata', async () => {
      await provider.save(testData, 'no-metadata.txt')
      const result = await provider.getMetadata('no-metadata.txt')
      expect(result).toEqual({})
    })
    it('should update metadata correctly', async () => {
      const newMetadata = { ...metadata, modified: true }
      const result = await provider.updateMetadata(testFile, newMetadata)
      expect(result).toEqual(newMetadata)
      const savedMetadata = await provider.getMetadata(testFile)
      expect(savedMetadata).toEqual(newMetadata)
    })
  })
  describe('error handling', () => {
    it('should handle permission errors', async () => {
      const readOnlyDir = path.join(rootDir, 'readonly')
      await fs.mkdir(readOnlyDir)
      await fs.chmod(readOnlyDir, 0o444)
      await expect(provider.save(testData, 'readonly/file.txt'))
        .rejects
        .toThrow(new StorageError(StorageErrorCode.PERMISSION_DENIED, expect.any(String)))
    })
    it('should handle not found errors', async () => {
      await expect(provider.get('nonexistent.txt'))
        .rejects
        .toThrow(new StorageError(StorageErrorCode.NOT_FOUND, expect.any(String)))
    })
    it('should handle already exists errors', async () => {
      const filePath = 'exists.txt'
      await provider.save(testData, filePath)
      await expect(fs.mkdir(path.join(rootDir, filePath)))
        .rejects
        .toThrow()
    })
  })
}) 