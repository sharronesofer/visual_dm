from typing import Any, Dict, List



  S3Client,
  PutObjectCommand,
  GetObjectCommand,
  DeleteObjectCommand,
  HeadObjectCommand,
  ListObjectsV2Command,
  CopyObjectCommand,
  GetObjectAttributesCommand,
  CreateMultipartUploadCommand,
  UploadPartCommand,
  CompleteMultipartUploadCommand,
  AbortMultipartUploadCommand,
  S3ServiceException,
  StorageClass
} from '@aws-sdk/client-s3'
describe('S3StorageProvider', () => {
  let provider: S3StorageProvider
  let s3Mock: ReturnType<typeof mockClient>
  let testData: Buffer
  let testConfig: S3StorageConfig
  beforeEach(() => {
    s3Mock = mockClient(S3Client)
    testData = Buffer.from('Hello, World!')
    testConfig = {
      s3Client: new S3Client({}),
      bucketName: 'test-bucket',
      basePath: 'test/base',
      urlExpirationSeconds: 3600,
      usePathStyleEndpoint: false,
      defaultStorageClass: 'STANDARD',
      enableProgress: true
    }
    provider = new S3StorageProvider(testConfig)
  })
  afterEach(() => {
    s3Mock.reset()
  })
  describe('constructor', () => {
    it('should initialize with default config', () => {
      const defaultProvider = new S3StorageProvider({
        s3Client: new S3Client({}),
        bucketName: 'test-bucket'
      })
      expect(defaultProvider).toBeInstanceOf(S3StorageProvider)
    })
    it('should initialize with custom config', () => {
      expect(provider).toBeInstanceOf(S3StorageProvider)
    })
    it('should configure retry settings correctly', () => {
      const customRetryConfig = {
        ...testConfig,
        maxRetries: 5
      }
      const retryProvider = new S3StorageProvider(customRetryConfig)
      expect(retryProvider['config'].maxRetries).toBe(5)
      expect(retryProvider['config'].s3Client.config.maxAttempts).toBeDefined()
      expect(retryProvider['config'].s3Client.config.retryMode).toBe('standard')
    })
  })
  describe('save', () => {
    describe('regular upload', () => {
      it('should upload small files using PutObject', async () => {
        s3Mock.on(PutObjectCommand).resolves({})
        s3Mock.on(GetObjectAttributesCommand).resolves({ ObjectSize: testData.length })
        const result = await provider.save(testData, 'test.txt', {
          contentType: 'text/plain',
          metadata: Dict[str, Any]
        })
        expect(result.path).toBe('test/base/test.txt')
        expect(result.size).toBe(testData.length)
        expect(result.metadata).toEqual({ test: 'value' })
        expect(s3Mock.calls()).toHaveLength(2) 
        const putCall = s3Mock.commandCalls(PutObjectCommand)[0]
        expect(putCall.args[0].input).toMatchObject({
          Bucket: 'test-bucket',
          Key: 'test/base/test.txt',
          Body: testData,
          ContentType: 'text/plain',
          Metadata: Dict[str, Any],
          StorageClass: 'STANDARD'
        })
      })
      it('should handle errors during upload', async () => {
        const error = new S3ServiceException({
          name: 'NoSuchBucket',
          $metadata: {},
          $fault: 'client'
        })
        s3Mock.on(PutObjectCommand).rejects(error)
        await expect(provider.save(testData, 'test.txt'))
          .rejects
          .toThrow(StorageError)
      })
    })
    describe('multipart upload', () => {
      const largeData = Buffer.alloc(6 * 1024 * 1024) 
      const uploadId = 'test-upload-id'
      const etag = 'test-etag'
      beforeEach(() => {
        s3Mock.on(CreateMultipartUploadCommand).resolves({ UploadId: uploadId })
        s3Mock.on(UploadPartCommand).resolves({ ETag: etag })
        s3Mock.on(CompleteMultipartUploadCommand).resolves({})
      })
      it('should use multipart upload for large files', async () => {
        const result = await provider.save(largeData, 'large.bin', {
          contentType: 'application/octet-stream'
        })
        expect(result.path).toBe('test/base/large.bin')
        expect(result.size).toBe(largeData.length)
        const createCall = s3Mock.commandCalls(CreateMultipartUploadCommand)[0]
        expect(createCall.args[0].input).toMatchObject({
          Bucket: 'test-bucket',
          Key: 'test/base/large.bin',
          ContentType: 'application/octet-stream'
        })
        const uploadCalls = s3Mock.commandCalls(UploadPartCommand)
        expect(uploadCalls.length).toBeGreaterThan(1) 
        const completeCalls = s3Mock.commandCalls(CompleteMultipartUploadCommand)
        expect(completeCalls).toHaveLength(1)
      })
      it('should handle stream input for multipart upload', async () => {
        const stream = Readable.from(largeData)
        const result = await provider.save(stream, 'stream.bin')
        expect(result.path).toBe('test/base/stream.bin')
        expect(result.size).toBe(largeData.length)
        expect(s3Mock.commandCalls(CreateMultipartUploadCommand)).toHaveLength(1)
        expect(s3Mock.commandCalls(UploadPartCommand).length).toBeGreaterThan(0)
        expect(s3Mock.commandCalls(CompleteMultipartUploadCommand)).toHaveLength(1)
      })
      it('should abort multipart upload on failure', async () => {
        const error = new S3ServiceException({
          name: 'InternalError',
          $metadata: {},
          $fault: 'server'
        })
        s3Mock.on(UploadPartCommand).rejects(error)
        s3Mock.on(AbortMultipartUploadCommand).resolves({})
        await expect(provider.save(largeData, 'fail.bin'))
          .rejects
          .toThrow(StorageError)
        expect(s3Mock.commandCalls(AbortMultipartUploadCommand)).toHaveLength(1)
      })
      it('should emit progress events during multipart upload', async () => {
        const progressEvents: List[any] = []
        provider.on('progress', (data) => progressEvents.push(data))
        await provider.save(largeData, 'progress.bin')
        expect(progressEvents.length).toBeGreaterThan(0)
        progressEvents.forEach(event => {
          expect(event).toHaveProperty('loaded')
          expect(event.loaded).toBeGreaterThan(0)
        })
      })
    })
  })
  describe('get', () => {
    it('should retrieve file data', async () => {
      const mockStream = new Readable()
      mockStream.push(testData)
      mockStream.push(null)
      s3Mock.on(GetObjectCommand).resolves({
        Body: mockStream as any 
      })
      const data = await provider.get('test.txt')
      expect(data).toBeInstanceOf(Readable)
    })
    it('should handle non-existent files', async () => {
      const error = new S3ServiceException({
        name: 'NoSuchKey',
        $metadata: {},
        $fault: 'client'
      })
      s3Mock.on(GetObjectCommand).rejects(error)
      await expect(provider.get('nonexistent.txt'))
        .rejects
        .toThrow(new StorageError(StorageErrorCode.NOT_FOUND, 'File not found'))
    })
  })
  describe('delete', () => {
    it('should delete existing file', async () => {
      s3Mock.on(DeleteObjectCommand).resolves({})
      const result = await provider.delete('test.txt')
      expect(result).toBe(true)
      const deleteCall = s3Mock.commandCalls(DeleteObjectCommand)[0]
      expect(deleteCall.args[0].input).toMatchObject({
        Bucket: 'test-bucket',
        Key: 'test/base/test.txt'
      })
    })
    it('should handle non-existent files', async () => {
      const error = new S3ServiceException({
        name: 'NoSuchKey',
        $metadata: {},
        $fault: 'client'
      })
      s3Mock.on(DeleteObjectCommand).rejects(error)
      const result = await provider.delete('nonexistent.txt')
      expect(result).toBe(false)
    })
  })
  describe('exists', () => {
    it('should return true for existing file', async () => {
      s3Mock.on(HeadObjectCommand).resolves({})
      const exists = await provider.exists('test.txt')
      expect(exists).toBe(true)
    })
    it('should return false for non-existent file', async () => {
      const error = new S3ServiceException({
        name: 'NotFound',
        $metadata: {},
        $fault: 'client'
      })
      s3Mock.on(HeadObjectCommand).rejects(error)
      const exists = await provider.exists('nonexistent.txt')
      expect(exists).toBe(false)
    })
  })
  describe('list', () => {
    it('should list files in directory', async () => {
      s3Mock.on(ListObjectsV2Command).resolves({
        Contents: [
          { Key: 'test/base/file1.txt', Size: 100, LastModified: new Date() },
          { Key: 'test/base/file2.txt', Size: 200, LastModified: new Date() }
        ]
      })
      const items = await provider.list('')
      expect(items).toHaveLength(2)
      items.forEach(item => {
        expect(item).toHaveProperty('path')
        expect(item).toHaveProperty('size')
        expect(item).toHaveProperty('modifiedAt')
      })
    })
    it('should handle empty directories', async () => {
      s3Mock.on(ListObjectsV2Command).resolves({
        Contents: []
      })
      const items = await provider.list('empty/')
      expect(items).toHaveLength(0)
    })
  })
  describe('copy', () => {
    it('should copy files within bucket', async () => {
      s3Mock.on(CopyObjectCommand).resolves({})
      const result = await provider.copy('source.txt', 'dest.txt')
      expect(result).toBe(true)
      const copyCall = s3Mock.commandCalls(CopyObjectCommand)[0]
      expect(copyCall.args[0].input).toMatchObject({
        Bucket: 'test-bucket',
        Key: 'test/base/dest.txt',
        CopySource: `test-bucket/test/base/source.txt`
      })
    })
    it('should handle non-existent source files', async () => {
      const error = new S3ServiceException({
        name: 'NoSuchKey',
        $metadata: {},
        $fault: 'client'
      })
      s3Mock.on(CopyObjectCommand).rejects(error)
      await expect(provider.copy('nonexistent.txt', 'dest.txt'))
        .rejects
        .toThrow(new StorageError(StorageErrorCode.NOT_FOUND, 'Source file not found'))
    })
  })
  describe('getUrl', () => {
    it('should generate presigned URL for private files', async () => {
      const url = await provider.getUrl('private.txt')
      expect(url).toContain('test-bucket')
      expect(url).toContain('test/base/private.txt')
    })
    it('should generate public URL for public files', async () => {
      const url = await provider.getUrl('public.txt', { expiresIn: undefined }) 
      expect(url).not.toContain('X-Amz-Algorithm') 
      expect(url).toContain('test-bucket')
      expect(url).toContain('test/base/public.txt')
    })
  })
}) 