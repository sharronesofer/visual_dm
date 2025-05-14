import { BaseStorageProvider, BaseStorageConfig } from './BaseStorageProvider';
import { StorageOptions, StorageResult, StorageItem, StorageError, StorageErrorCode } from '../../interfaces/storage/StorageProvider';
import { Readable } from 'stream';
import {
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
} from '@aws-sdk/client-s3';
import { getSignedUrl } from '@aws-sdk/s3-request-presigner';
import { pipeline } from 'stream/promises';
import { createReadStream } from 'fs';

// Size in bytes for using multipart upload (5MB)
const MULTIPART_THRESHOLD = 5 * 1024 * 1024;
// Size of each part for multipart upload (5MB)
const PART_SIZE = 5 * 1024 * 1024;
// Maximum number of retries for operations
const MAX_RETRIES = 3;

/**
 * Configuration for S3StorageProvider
 */
export interface S3StorageConfig extends BaseStorageConfig {
  /**
   * AWS S3 client instance
   */
  s3Client: S3Client;

  /**
   * S3 bucket name
   */
  bucketName: string;

  /**
   * Default URL expiration in seconds for presigned URLs
   */
  urlExpirationSeconds?: number;

  /**
   * Whether to use path style endpoints (for compatibility with some S3-compatible services)
   */
  usePathStyleEndpoint?: boolean;

  /**
   * Default storage class for objects
   */
  defaultStorageClass?: keyof typeof StorageClass;

  /**
   * Size threshold for using multipart upload (in bytes)
   */
  multipartThreshold?: number;

  /**
   * Size of each part for multipart upload (in bytes)
   */
  partSize?: number;

  /**
   * Maximum number of retries for failed operations
   */
  maxRetries?: number;
}

/**
 * Storage provider implementation for Amazon S3
 */
export class S3StorageProvider extends BaseStorageProvider {
  protected config: Required<S3StorageConfig>;

  constructor(config: S3StorageConfig) {
    super(config);

    // Configure S3 client with retry settings
    const s3Client = config.s3Client;
    if (!s3Client.config.maxAttempts) {
      s3Client.config.maxAttempts = async () => (config.maxRetries || MAX_RETRIES) + 1; // maxAttempts includes the initial attempt
    }
    if (!s3Client.config.retryMode) {
      s3Client.config.retryMode = 'standard'; // Use standard retry mode for better reliability
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
    };
  }

  protected async performSave(
    data: Buffer | Readable,
    fullPath: string,
    options: StorageOptions
  ): Promise<StorageResult> {
    try {
      let size = 0;
      
      // If data is a Buffer and larger than threshold, or if it's a Readable stream,
      // use multipart upload
      if (
        (Buffer.isBuffer(data) && data.length > this.config.multipartThreshold) ||
        data instanceof Readable
      ) {
        const result = await this.performMultipartUpload(data, fullPath, options);
        size = result.size;
      } else {
        // Use regular upload for smaller files
        const uploadParams = {
          Bucket: this.config.bucketName,
          Key: fullPath,
          Body: data,
          ContentType: options.contentType,
          Metadata: options.metadata,
          CacheControl: options.cacheControl,
          ACL: options.isPublic ? ('public-read' as ObjectCannedACL) : undefined,
          StorageClass: this.config.defaultStorageClass
        };

        const command = new PutObjectCommand(uploadParams);
        await this.config.s3Client.send(command);

        // Get object attributes to return accurate size
        const attributesCommand = new GetObjectAttributesCommand({
          Bucket: this.config.bucketName,
          Key: fullPath,
          ObjectAttributes: [ObjectAttributes.OBJECT_SIZE]
        });

        const attributes = await this.config.s3Client.send(attributesCommand);
        size = attributes.ObjectSize || 0;
      }

      const result: StorageResult = {
        path: fullPath,
        size,
        metadata: options.metadata || {}
      };

      if (options.isPublic) {
        result.url = await this.performGetUrl(fullPath);
      }

      return result;
    } catch (err) {
      throw this.mapError(err);
    }
  }

  /**
   * Perform multipart upload for large files
   */
  private async performMultipartUpload(
    data: Buffer | Readable,
    fullPath: string,
    options: StorageOptions
  ): Promise<{ size: number }> {
    // Start multipart upload
    const createCommand = new CreateMultipartUploadCommand({
      Bucket: this.config.bucketName,
      Key: fullPath,
      ContentType: options.contentType,
      Metadata: options.metadata,
      CacheControl: options.cacheControl,
      ACL: options.isPublic ? ('public-read' as ObjectCannedACL) : undefined,
      StorageClass: this.config.defaultStorageClass
    });

    const { UploadId } = await this.config.s3Client.send(createCommand);
    if (!UploadId) {
      throw new StorageError(
        StorageErrorCode.UNKNOWN,
        'Failed to initiate multipart upload'
      );
    }

    const parts: { ETag: string; PartNumber: number }[] = [];
    let totalSize = 0;
    let partNumber = 1;

    try {
      if (Buffer.isBuffer(data)) {
        // Handle Buffer input
        for (let i = 0; i < data.length; i += this.config.partSize) {
          const partData = data.slice(i, i + this.config.partSize);
          const uploadCommand = new UploadPartCommand({
            Bucket: this.config.bucketName,
            Key: fullPath,
            UploadId,
            PartNumber: partNumber,
            Body: partData
          });

          const response = await this.config.s3Client.send(uploadCommand);
          if (!response.ETag) {
            throw new StorageError(
              StorageErrorCode.UNKNOWN,
              `Failed to upload part ${partNumber}`
            );
          }

          parts.push({ ETag: response.ETag, PartNumber: partNumber });
          totalSize += partData.length;
          partNumber++;

          if (this.config.enableProgress) {
            this.emit('progress', {
              loaded: totalSize,
              total: data.length
            });
          }
        }
      } else {
        // Handle Readable stream input
        let buffer = Buffer.alloc(0);
        
        for await (const chunk of data) {
          buffer = Buffer.concat([buffer, chunk]);
          
          while (buffer.length >= this.config.partSize) {
            const partData = buffer.slice(0, this.config.partSize);
            buffer = buffer.slice(this.config.partSize);

            const uploadCommand = new UploadPartCommand({
              Bucket: this.config.bucketName,
              Key: fullPath,
              UploadId,
              PartNumber: partNumber,
              Body: partData
            });

            const response = await this.config.s3Client.send(uploadCommand);
            if (!response.ETag) {
              throw new StorageError(
                StorageErrorCode.UNKNOWN,
                `Failed to upload part ${partNumber}`
              );
            }

            parts.push({ ETag: response.ETag, PartNumber: partNumber });
            totalSize += partData.length;
            partNumber++;

            if (this.config.enableProgress) {
              this.emit('progress', {
                loaded: totalSize,
                total: undefined
              });
            }
          }
        }

        // Upload remaining data if any
        if (buffer.length > 0) {
          const uploadCommand = new UploadPartCommand({
            Bucket: this.config.bucketName,
            Key: fullPath,
            UploadId,
            PartNumber: partNumber,
            Body: buffer
          });

          const response = await this.config.s3Client.send(uploadCommand);
          if (!response.ETag) {
            throw new StorageError(
              StorageErrorCode.UNKNOWN,
              `Failed to upload final part ${partNumber}`
            );
          }

          parts.push({ ETag: response.ETag, PartNumber: partNumber });
          totalSize += buffer.length;

          if (this.config.enableProgress) {
            this.emit('progress', {
              loaded: totalSize,
              total: totalSize
            });
          }
        }
      }

      // Complete multipart upload
      const completeCommand = new CompleteMultipartUploadCommand({
        Bucket: this.config.bucketName,
        Key: fullPath,
        UploadId,
        MultipartUpload: { Parts: parts }
      });

      await this.config.s3Client.send(completeCommand);
      return { size: totalSize };
    } catch (err) {
      // Abort multipart upload on failure
      try {
        const abortCommand = new AbortMultipartUploadCommand({
          Bucket: this.config.bucketName,
          Key: fullPath,
          UploadId
        });
        await this.config.s3Client.send(abortCommand);
      } catch (abortErr) {
        // Log abort error but throw the original error
        console.error('Failed to abort multipart upload:', abortErr);
      }
      throw this.mapError(err);
    }
  }

  protected async performGet(fullPath: string): Promise<Buffer | Readable> {
    try {
      const command = new GetObjectCommand({
        Bucket: this.config.bucketName,
        Key: fullPath
      });

      const response = await this.config.s3Client.send(command);
      
      if (!response.Body) {
        throw new StorageError(
          StorageErrorCode.NOT_FOUND,
          'Object body is empty'
        );
      }

      // Return the stream directly if it's a Readable
      if (response.Body instanceof Readable) {
        return response.Body;
      }

      // Convert other types to Buffer
      if ('transformToByteArray' in response.Body) {
        const bytes = await response.Body.transformToByteArray();
        return Buffer.from(bytes);
      }

      throw new StorageError(
        StorageErrorCode.UNKNOWN,
        'Unsupported response body type'
      );
    } catch (err) {
      throw this.mapError(err);
    }
  }

  protected async performDelete(fullPath: string): Promise<boolean> {
    try {
      const command = new DeleteObjectCommand({
        Bucket: this.config.bucketName,
        Key: fullPath
      });

      await this.config.s3Client.send(command);
      return true;
    } catch (err) {
      if (err instanceof S3ServiceException && err.name === 'NoSuchKey') {
        return false;
      }
      throw this.mapError(err);
    }
  }

  protected async performExists(fullPath: string): Promise<boolean> {
    try {
      const command = new HeadObjectCommand({
        Bucket: this.config.bucketName,
        Key: fullPath
      });

      await this.config.s3Client.send(command);
      return true;
    } catch (err) {
      if (err instanceof S3ServiceException && err.name === 'NotFound') {
        return false;
      }
      throw this.mapError(err);
    }
  }

  protected async performGetUrl(fullPath: string): Promise<string> {
    try {
      if (this.config.defaultOptions.isPublic) {
        // Return public URL for public objects
        return this.getPublicUrl(fullPath);
      }

      // Generate presigned URL for private objects
      const command = new GetObjectCommand({
        Bucket: this.config.bucketName,
        Key: fullPath
      });

      return getSignedUrl(this.config.s3Client, command, {
        expiresIn: this.config.urlExpirationSeconds
      });
    } catch (err) {
      throw this.mapError(err);
    }
  }

  protected async performList(fullPath: string): Promise<StorageItem[]> {
    try {
      const command = new ListObjectsV2Command({
        Bucket: this.config.bucketName,
        Prefix: fullPath
      });

      const response = await this.config.s3Client.send(command);
      const items: StorageItem[] = [];

      if (!response.Contents) {
        return items;
      }

      for (const object of response.Contents) {
        if (!object.Key) continue;

        items.push({
          path: object.Key,
          size: object.Size || 0,
          lastModified: object.LastModified || new Date(),
          isDirectory: object.Key.endsWith('/')
        });
      }

      return items;
    } catch (err) {
      throw this.mapError(err);
    }
  }

  protected async performCopy(
    fullSourcePath: string,
    fullDestPath: string
  ): Promise<boolean> {
    try {
      const command = new CopyObjectCommand({
        Bucket: this.config.bucketName,
        CopySource: `${this.config.bucketName}/${fullSourcePath}`,
        Key: fullDestPath
      });

      await this.config.s3Client.send(command);
      return true;
    } catch (err) {
      throw this.mapError(err);
    }
  }

  protected async performMove(
    fullSourcePath: string,
    fullDestPath: string
  ): Promise<boolean> {
    try {
      // Copy first
      await this.performCopy(fullSourcePath, fullDestPath);
      
      // Then delete the source
      await this.performDelete(fullSourcePath);
      
      return true;
    } catch (err) {
      // Try to clean up the destination if the move failed
      try {
        await this.performDelete(fullDestPath);
      } catch {
        // Ignore cleanup errors
      }
      throw this.mapError(err);
    }
  }

  protected async performGetMetadata(fullPath: string): Promise<Record<string, any>> {
    try {
      const command = new HeadObjectCommand({
        Bucket: this.config.bucketName,
        Key: fullPath
      });

      const response = await this.config.s3Client.send(command);
      return response.Metadata || {};
    } catch (err) {
      if (err instanceof S3ServiceException && err.name === 'NotFound') {
        return {};
      }
      throw this.mapError(err);
    }
  }

  protected async performUpdateMetadata(
    fullPath: string,
    metadata: Record<string, any>
  ): Promise<Record<string, any>> {
    try {
      // S3 requires copying the object to itself to update metadata
      const command = new CopyObjectCommand({
        Bucket: this.config.bucketName,
        CopySource: `${this.config.bucketName}/${fullPath}`,
        Key: fullPath,
        Metadata: metadata,
        MetadataDirective: 'REPLACE'
      });

      await this.config.s3Client.send(command);
      return metadata;
    } catch (err) {
      throw this.mapError(err);
    }
  }

  protected async ensureParentDirectory(): Promise<void> {
    // No-op for S3 as it doesn't require directory creation
  }

  protected mapError(error: unknown): StorageError {
    if (error instanceof StorageError) {
      return error;
    }

    if (error instanceof S3ServiceException) {
      switch (error.name) {
        case 'NoSuchKey':
        case 'NotFound':
          return new StorageError(StorageErrorCode.NOT_FOUND, error.message);
        case 'NoSuchBucket':
          return new StorageError(StorageErrorCode.NOT_FOUND, 'Bucket not found');
        case 'AccessDenied':
          return new StorageError(StorageErrorCode.PERMISSION_DENIED, error.message);
        case 'BucketAlreadyExists':
          return new StorageError(StorageErrorCode.ALREADY_EXISTS, error.message);
        case 'InvalidRequest':
          return new StorageError(StorageErrorCode.INVALID_ARGUMENT, error.message);
        default:
          return new StorageError(
            StorageErrorCode.UNKNOWN,
            error.message || 'Unknown S3 error occurred',
            { code: error.name }
          );
      }
    }

    return new StorageError(
      StorageErrorCode.UNKNOWN,
      error instanceof Error ? error.message : 'Unknown error occurred'
    );
  }

  /**
   * Get public URL for an object
   */
  private getPublicUrl(fullPath: string): string {
    const encodedKey = encodeURIComponent(fullPath);
    if (this.config.usePathStyleEndpoint) {
      return `https://${this.config.s3Client.config.endpoint}/${this.config.bucketName}/${encodedKey}`;
    }
    return `https://${this.config.bucketName}.${this.config.s3Client.config.endpoint}/${encodedKey}`;
  }
} 