from typing import Any, Dict, List



  S3Client,
  PutObjectCommand,
  GetObjectCommand,
  DeleteObjectCommand,
  HeadObjectCommand,
  ListObjectsV2Command,
  CopyObjectCommand,
  GetObjectAttributesCommand,
  ObjectAttributes,
  S3ServiceException,
  CreateMultipartUploadCommand,
  UploadPartCommand,
  CompleteMultipartUploadCommand,
  AbortMultipartUploadCommand,
  StorageClass,
  ObjectCannedACL
} from '@aws-sdk/client-s3'
const MULTIPART_THRESHOLD = 5 * 1024 * 1024
const PART_SIZE = 5 * 1024 * 1024
const MAX_RETRIES = 3
/**
 * Configuration for S3StorageProvider
 */
class S3StorageConfig:
    /**
   * AWS S3 client instance
   */
  s3Client: S3Client
    /**
   * S3 bucket name
   */
  bucketName: str
    /**
   * Default URL expiration in seconds for presigned URLs
   */
  urlExpirationSeconds?: float
    /**
   * Whether to use path style endpoints (for compatibility with some S3-compatible services)
   */
  usePathStyleEndpoint?: bool
    /**
   * Default storage class for objects
   */
  defaultStorageClass?: keyof typeof StorageClass
    /**
   * Size threshold for using multipart upload (in bytes)
   */
  multipartThreshold?: float
    /**
   * Size of each part for multipart upload (in bytes)
   */
  partSize?: float
    /**
   * Maximum number of retries for failed operations
   */
  maxRetries?: float
/**
 * Storage provider implementation for Amazon S3
 */
class S3StorageProvider extends BaseStorageProvider {
  protected config: Required<S3StorageConfig>
  constructor(config: S3StorageConfig) {
    super(config)
    const s3Client = config.s3Client
    if (!s3Client.config.maxAttempts) {
      s3Client.config.maxAttempts = async () => (config.maxRetries || MAX_RETRIES) + 1 
    }
    if (!s3Client.config.retryMode) {
      s3Client.config.retryMode = 'standard' 
    }
    this.config = {
      s3Client,
      bucketName: config.bucketName,
      urlExpirationSeconds: config.urlExpirationSeconds ?? 3600,
      usePathStyleEndpoint: config.usePathStyleEndpoint ?? false,
      basePath: config.basePath || '',
      defaultOptions: config.defaultOptions || {},
      enableProgress: config.enableProgress ?? true,
      defaultStorageClass: config.defaultStorageClass || 'STANDARD',
      multipartThreshold: config.multipartThreshold || MULTIPART_THRESHOLD,
      partSize: config.partSize || PART_SIZE,
      maxRetries: config.maxRetries || MAX_RETRIES
    }
  }
  protected async performSave(
    data: Buffer | Readable,
    fullPath: str,
    options: StorageOptions
  ): Promise<StorageResult> {
    try {
      let size = 0
      if (
        (Buffer.isBuffer(data) && data.length > this.config.multipartThreshold) ||
        data instanceof Readable
      ) {
        const result = await this.performMultipartUpload(data, fullPath, options)
        size = result.size
      } else {
        const uploadParams = {
          Bucket: this.config.bucketName,
          Key: fullPath,
          Body: data,
          ContentType: options.contentType,
          Metadata: options.metadata,
          CacheControl: options.cacheControl,
          ACL: options.isPublic ? ('public-read' as ObjectCannedACL) : undefined,
          StorageClass: this.config.defaultStorageClass
        }
        const command = new PutObjectCommand(uploadParams)
        await this.config.s3Client.send(command)
        const attributesCommand = new GetObjectAttributesCommand({
          Bucket: this.config.bucketName,
          Key: fullPath,
          ObjectAttributes: [ObjectAttributes.OBJECT_SIZE]
        })
        const attributes = await this.config.s3Client.send(attributesCommand)
        size = attributes.ObjectSize || 0
      }
      const result: StorageResult = {
        path: fullPath,
        size,
        metadata: options.metadata || {}
      }
      if (options.isPublic) {
        result.url = await this.performGetUrl(fullPath)
      }
      return result
    } catch (err) {
      throw this.mapError(err)
    }
  }
  /**
   * Perform multipart upload for large files
   */
  private async performMultipartUpload(
    data: Buffer | Readable,
    fullPath: str,
    options: StorageOptions
  ): Promise<{ size: float }> {
    const createCommand = new CreateMultipartUploadCommand({
      Bucket: this.config.bucketName,
      Key: fullPath,
      ContentType: options.contentType,
      Metadata: options.metadata,
      CacheControl: options.cacheControl,
      ACL: options.isPublic ? ('public-read' as ObjectCannedACL) : undefined,
      StorageClass: this.config.defaultStorageClass
    })
    const { UploadId } = await this.config.s3Client.send(createCommand)
    if (!UploadId) {
      throw new StorageError(
        StorageErrorCode.UNKNOWN,
        'Failed to initiate multipart upload'
      )
    }
    const parts: Dict[str, Any][] = []
    let totalSize = 0
    let partNumber = 1
    try {
      if (Buffer.isBuffer(data)) {
        for (let i = 0; i < data.length; i += this.config.partSize) {
          const partData = data.slice(i, i + this.config.partSize)
          const uploadCommand = new UploadPartCommand({
            Bucket: this.config.bucketName,
            Key: fullPath,
            UploadId,
            PartNumber: partNumber,
            Body: partData
          })
          const response = await this.config.s3Client.send(uploadCommand)
          if (!response.ETag) {
            throw new StorageError(
              StorageErrorCode.UNKNOWN,
              `Failed to upload part ${partNumber}`
            )
          }
          parts.push({ ETag: response.ETag, PartNumber: partNumber })
          totalSize += partData.length
          partNumber++
          if (this.config.enableProgress) {
            this.emit('progress', {
              loaded: totalSize,
              total: data.length
            })
          }
        }
      } else {
        let buffer = Buffer.alloc(0)
        for await (const chunk of data) {
          buffer = Buffer.concat([buffer, chunk])
          while (buffer.length >= this.config.partSize) {
            const partData = buffer.slice(0, this.config.partSize)
            buffer = buffer.slice(this.config.partSize)
            const uploadCommand = new UploadPartCommand({
              Bucket: this.config.bucketName,
              Key: fullPath,
              UploadId,
              PartNumber: partNumber,
              Body: partData
            })
            const response = await this.config.s3Client.send(uploadCommand)
            if (!response.ETag) {
              throw new StorageError(
                StorageErrorCode.UNKNOWN,
                `Failed to upload part ${partNumber}`
              )
            }
            parts.push({ ETag: response.ETag, PartNumber: partNumber })
            totalSize += partData.length
            partNumber++
            if (this.config.enableProgress) {
              this.emit('progress', {
                loaded: totalSize,
                total: undefined
              })
            }
          }
        }
        if (buffer.length > 0) {
          const uploadCommand = new UploadPartCommand({
            Bucket: this.config.bucketName,
            Key: fullPath,
            UploadId,
            PartNumber: partNumber,
            Body: buffer
          })
          const response = await this.config.s3Client.send(uploadCommand)
          if (!response.ETag) {
            throw new StorageError(
              StorageErrorCode.UNKNOWN,
              `Failed to upload final part ${partNumber}`
            )
          }
          parts.push({ ETag: response.ETag, PartNumber: partNumber })
          totalSize += buffer.length
          if (this.config.enableProgress) {
            this.emit('progress', {
              loaded: totalSize,
              total: totalSize
            })
          }
        }
      }
      const completeCommand = new CompleteMultipartUploadCommand({
        Bucket: this.config.bucketName,
        Key: fullPath,
        UploadId,
        MultipartUpload: Dict[str, Any]
      })
      await this.config.s3Client.send(completeCommand)
      return { size: totalSize }
    } catch (err) {
      try {
        const abortCommand = new AbortMultipartUploadCommand({
          Bucket: this.config.bucketName,
          Key: fullPath,
          UploadId
        })
        await this.config.s3Client.send(abortCommand)
      } catch (abortErr) {
        console.error('Failed to abort multipart upload:', abortErr)
      }
      throw this.mapError(err)
    }
  }
  protected async performGet(fullPath: str): Promise<Buffer | Readable> {
    try {
      const command = new GetObjectCommand({
        Bucket: this.config.bucketName,
        Key: fullPath
      })
      const response = await this.config.s3Client.send(command)
      if (!response.Body) {
        throw new StorageError(
          StorageErrorCode.NOT_FOUND,
          'Object body is empty'
        )
      }
      if (response.Body instanceof Readable) {
        return response.Body
      }
      if ('transformToByteArray' in response.Body) {
        const bytes = await response.Body.transformToByteArray()
        return Buffer.from(bytes)
      }
      throw new StorageError(
        StorageErrorCode.UNKNOWN,
        'Unsupported response body type'
      )
    } catch (err) {
      throw this.mapError(err)
    }
  }
  protected async performDelete(fullPath: str): Promise<boolean> {
    try {
      const command = new DeleteObjectCommand({
        Bucket: this.config.bucketName,
        Key: fullPath
      })
      await this.config.s3Client.send(command)
      return true
    } catch (err) {
      if (err instanceof S3ServiceException && err.name === 'NoSuchKey') {
        return false
      }
      throw this.mapError(err)
    }
  }
  protected async performExists(fullPath: str): Promise<boolean> {
    try {
      const command = new HeadObjectCommand({
        Bucket: this.config.bucketName,
        Key: fullPath
      })
      await this.config.s3Client.send(command)
      return true
    } catch (err) {
      if (err instanceof S3ServiceException && err.name === 'NotFound') {
        return false
      }
      throw this.mapError(err)
    }
  }
  protected async performGetUrl(fullPath: str): Promise<string> {
    try {
      if (this.config.defaultOptions.isPublic) {
        return this.getPublicUrl(fullPath)
      }
      const command = new GetObjectCommand({
        Bucket: this.config.bucketName,
        Key: fullPath
      })
      return getSignedUrl(this.config.s3Client, command, {
        expiresIn: this.config.urlExpirationSeconds
      })
    } catch (err) {
      throw this.mapError(err)
    }
  }
  protected async performList(fullPath: str): Promise<StorageItem[]> {
    try {
      const command = new ListObjectsV2Command({
        Bucket: this.config.bucketName,
        Prefix: fullPath
      })
      const response = await this.config.s3Client.send(command)
      const items: List[StorageItem] = []
      if (!response.Contents) {
        return items
      }
      for (const object of response.Contents) {
        if (!object.Key) continue
        items.push({
          path: object.Key,
          size: object.Size || 0,
          lastModified: object.LastModified || new Date(),
          isDirectory: object.Key.endsWith('/')
        })
      }
      return items
    } catch (err) {
      throw this.mapError(err)
    }
  }
  protected async performCopy(
    fullSourcePath: str,
    fullDestPath: str
  ): Promise<boolean> {
    try {
      const command = new CopyObjectCommand({
        Bucket: this.config.bucketName,
        CopySource: `${this.config.bucketName}/${fullSourcePath}`,
        Key: fullDestPath
      })
      await this.config.s3Client.send(command)
      return true
    } catch (err) {
      throw this.mapError(err)
    }
  }
  protected async performMove(
    fullSourcePath: str,
    fullDestPath: str
  ): Promise<boolean> {
    try {
      await this.performCopy(fullSourcePath, fullDestPath)
      await this.performDelete(fullSourcePath)
      return true
    } catch (err) {
      try {
        await this.performDelete(fullDestPath)
      } catch {
      }
      throw this.mapError(err)
    }
  }
  protected async performGetMetadata(fullPath: str): Promise<Record<string, any>> {
    try {
      const command = new HeadObjectCommand({
        Bucket: this.config.bucketName,
        Key: fullPath
      })
      const response = await this.config.s3Client.send(command)
      return response.Metadata || {}
    } catch (err) {
      if (err instanceof S3ServiceException && err.name === 'NotFound') {
        return {}
      }
      throw this.mapError(err)
    }
  }
  protected async performUpdateMetadata(
    fullPath: str,
    metadata: Record<string, any>
  ): Promise<Record<string, any>> {
    try {
      const command = new CopyObjectCommand({
        Bucket: this.config.bucketName,
        CopySource: `${this.config.bucketName}/${fullPath}`,
        Key: fullPath,
        Metadata: metadata,
        MetadataDirective: 'REPLACE'
      })
      await this.config.s3Client.send(command)
      return metadata
    } catch (err) {
      throw this.mapError(err)
    }
  }
  protected async ensureParentDirectory(): Promise<void> {
  }
  protected mapError(error: unknown): StorageError {
    if (error instanceof StorageError) {
      return error
    }
    if (error instanceof S3ServiceException) {
      switch (error.name) {
        case 'NoSuchKey':
        case 'NotFound':
          return new StorageError(StorageErrorCode.NOT_FOUND, error.message)
        case 'NoSuchBucket':
          return new StorageError(StorageErrorCode.NOT_FOUND, 'Bucket not found')
        case 'AccessDenied':
          return new StorageError(StorageErrorCode.PERMISSION_DENIED, error.message)
        case 'BucketAlreadyExists':
          return new StorageError(StorageErrorCode.ALREADY_EXISTS, error.message)
        case 'InvalidRequest':
          return new StorageError(StorageErrorCode.INVALID_ARGUMENT, error.message)
        default:
          return new StorageError(
            StorageErrorCode.UNKNOWN,
            error.message || 'Unknown S3 error occurred',
            { code: error.name }
          )
      }
    }
    return new StorageError(
      StorageErrorCode.UNKNOWN,
      error instanceof Error ? error.message : 'Unknown error occurred'
    )
  }
  /**
   * Get public URL for an object
   */
  private getPublicUrl(fullPath: str): str {
    const encodedKey = encodeURIComponent(fullPath)
    if (this.config.usePathStyleEndpoint) {
      return `https:
    }
    return `https:
  }
} 