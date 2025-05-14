import { BaseStorageProvider, BaseStorageConfig } from './BaseStorageProvider';
import { StorageOptions, StorageResult, StorageItem, StorageError, StorageErrorCode } from '../../interfaces/storage/StorageProvider';
import { Readable } from 'stream';
import fs from 'fs/promises';
import { createReadStream, createWriteStream } from 'fs';
import path from 'path';
import { pipeline } from 'stream/promises';

/**
 * Configuration for FileSystemStorageProvider
 */
export interface FileSystemStorageConfig extends BaseStorageConfig {
  /**
   * Root directory for file storage
   */
  rootDir: string;

  /**
   * Base URL for generating public URLs (optional)
   */
  baseUrl?: string;

  /**
   * Whether to create directories if they don't exist
   */
  createDirs?: boolean;

  /**
   * Default file permissions (octal)
   */
  defaultPermissions?: number;
}

/**
 * Storage provider implementation for local file system
 */
export class FileSystemStorageProvider extends BaseStorageProvider {
  protected config: Required<FileSystemStorageConfig>;

  constructor(config: FileSystemStorageConfig) {
    super(config);
    this.config = {
      rootDir: path.resolve(config.rootDir),
      baseUrl: config.baseUrl || '',
      createDirs: config.createDirs ?? true,
      defaultPermissions: config.defaultPermissions ?? 0o644,
      basePath: config.basePath || '',
      defaultOptions: config.defaultOptions || {},
      enableProgress: config.enableProgress ?? true
    };
  }

  protected async performSave(
    data: Buffer | Readable,
    fullPath: string,
    options: StorageOptions
  ): Promise<StorageResult> {
    const filePath = this.getAbsolutePath(fullPath);
    const size = Buffer.isBuffer(data) ? data.length : 0;

    try {
      if (Buffer.isBuffer(data)) {
        await fs.writeFile(filePath, data);
        await this.setFilePermissions(filePath);
      } else {
        const writeStream = createWriteStream(filePath, {
          mode: this.config.defaultPermissions
        });

        await pipeline(data, writeStream);
      }

      // Save metadata if provided
      if (options.metadata && Object.keys(options.metadata).length > 0) {
        await this.performUpdateMetadata(fullPath, options.metadata);
      }

      const stats = await fs.stat(filePath);
      return {
        path: fullPath,
        size: stats.size,
        metadata: options.metadata || {}
      };
    } catch (err) {
      throw this.mapError(err);
    }
  }

  protected async performGet(fullPath: string): Promise<Buffer | Readable> {
    const filePath = this.getAbsolutePath(fullPath);

    try {
      const stats = await fs.stat(filePath);
      
      if (stats.size > 1024 * 1024) { // Stream files larger than 1MB
        return createReadStream(filePath);
      } else {
        return await fs.readFile(filePath);
      }
    } catch (err) {
      throw this.mapError(err);
    }
  }

  protected async performDelete(fullPath: string): Promise<boolean> {
    const filePath = this.getAbsolutePath(fullPath);

    try {
      await fs.unlink(filePath);
      
      // Try to remove metadata file if it exists
      const metadataPath = this.getMetadataPath(fullPath);
      await fs.unlink(metadataPath).catch(() => {}); // Ignore errors

      return true;
    } catch (err) {
      if ((err as NodeJS.ErrnoException).code === 'ENOENT') {
        return false;
      }
      throw this.mapError(err);
    }
  }

  protected async performExists(fullPath: string): Promise<boolean> {
    const filePath = this.getAbsolutePath(fullPath);

    try {
      await fs.access(filePath);
      return true;
    } catch {
      return false;
    }
  }

  protected async performGetUrl(fullPath: string): Promise<string> {
    if (!this.config.baseUrl) {
      throw new StorageError(
        StorageErrorCode.NOT_SUPPORTED,
        'URL generation not supported without baseUrl configuration'
      );
    }

    const urlPath = fullPath.split(path.sep).join('/');
    return `${this.config.baseUrl.replace(/\/$/, '')}/${urlPath.replace(/^\//, '')}`;
  }

  protected async performList(fullPath: string): Promise<StorageItem[]> {
    const dirPath = this.getAbsolutePath(fullPath);

    try {
      const entries = await fs.readdir(dirPath, { withFileTypes: true });
      const items: StorageItem[] = [];

      for (const entry of entries) {
        const entryPath = path.join(fullPath, entry.name);
        const absolutePath = this.getAbsolutePath(entryPath);
        const stats = await fs.stat(absolutePath);

        items.push({
          path: entryPath,
          size: stats.size,
          lastModified: stats.mtime,
          isDirectory: entry.isDirectory()
        });
      }

      return items;
    } catch (err) {
      if ((err as NodeJS.ErrnoException).code === 'ENOENT') {
        return [];
      }
      throw this.mapError(err);
    }
  }

  protected async performCopy(fullSourcePath: string, fullDestPath: string): Promise<boolean> {
    const sourcePath = this.getAbsolutePath(fullSourcePath);
    const destPath = this.getAbsolutePath(fullDestPath);

    try {
      await fs.copyFile(sourcePath, destPath);
      await this.setFilePermissions(destPath);

      // Copy metadata if it exists
      const sourceMetadataPath = this.getMetadataPath(fullSourcePath);
      const destMetadataPath = this.getMetadataPath(fullDestPath);

      try {
        await fs.copyFile(sourceMetadataPath, destMetadataPath);
      } catch {
        // Ignore metadata copy errors
      }

      return true;
    } catch (err) {
      throw this.mapError(err);
    }
  }

  protected async performMove(fullSourcePath: string, fullDestPath: string): Promise<boolean> {
    const sourcePath = this.getAbsolutePath(fullSourcePath);
    const destPath = this.getAbsolutePath(fullDestPath);

    try {
      await fs.rename(sourcePath, destPath);

      // Move metadata if it exists
      const sourceMetadataPath = this.getMetadataPath(fullSourcePath);
      const destMetadataPath = this.getMetadataPath(fullDestPath);

      try {
        await fs.rename(sourceMetadataPath, destMetadataPath);
      } catch {
        // Ignore metadata move errors
      }

      return true;
    } catch (err) {
      throw this.mapError(err);
    }
  }

  protected async performGetMetadata(fullPath: string): Promise<Record<string, any>> {
    const metadataPath = this.getMetadataPath(fullPath);

    try {
      const data = await fs.readFile(metadataPath, 'utf8');
      return JSON.parse(data);
    } catch (err) {
      if ((err as NodeJS.ErrnoException).code === 'ENOENT') {
        return {};
      }
      throw this.mapError(err);
    }
  }

  protected async performUpdateMetadata(
    fullPath: string,
    metadata: Record<string, any>
  ): Promise<Record<string, any>> {
    const metadataPath = this.getMetadataPath(fullPath);

    try {
      await fs.writeFile(metadataPath, JSON.stringify(metadata, null, 2));
      await this.setFilePermissions(metadataPath);
      return metadata;
    } catch (err) {
      throw this.mapError(err);
    }
  }

  protected async ensureParentDirectory(fullPath: string): Promise<void> {
    if (!this.config.createDirs) {
      return;
    }

    const dirPath = path.dirname(this.getAbsolutePath(fullPath));

    try {
      await fs.mkdir(dirPath, { recursive: true });
    } catch (err) {
      if ((err as NodeJS.ErrnoException).code !== 'EEXIST') {
        throw this.mapError(err);
      }
    }
  }

  protected mapError(error: unknown): StorageError {
    if (error instanceof StorageError) {
      return error;
    }

    const err = error as NodeJS.ErrnoException;
    switch (err.code) {
      case 'ENOENT':
        return new StorageError(StorageErrorCode.NOT_FOUND, 'File not found', { path: err.path });
      case 'EACCES':
        return new StorageError(StorageErrorCode.PERMISSION_DENIED, 'Permission denied', { path: err.path });
      case 'EEXIST':
        return new StorageError(StorageErrorCode.ALREADY_EXISTS, 'File already exists', { path: err.path });
      case 'ENOSPC':
        return new StorageError(StorageErrorCode.INSUFFICIENT_SPACE, 'Insufficient space', { path: err.path });
      default:
        return new StorageError(
          StorageErrorCode.UNKNOWN,
          err.message || 'Unknown error occurred',
          { code: err.code, path: err.path }
        );
    }
  }

  /**
   * Get absolute file system path
   */
  private getAbsolutePath(relativePath: string): string {
    return path.join(this.config.rootDir, relativePath);
  }

  /**
   * Get path for metadata file
   */
  private getMetadataPath(filePath: string): string {
    return `${this.getAbsolutePath(filePath)}.metadata.json`;
  }

  /**
   * Set default file permissions
   */
  private async setFilePermissions(filePath: string): Promise<void> {
    try {
      await fs.chmod(filePath, this.config.defaultPermissions);
    } catch {
      // Ignore permission setting errors
    }
  }
} 