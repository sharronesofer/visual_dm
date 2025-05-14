import { BaseStorageProvider } from './base-provider';
import { 
  StorageMetadata, 
  StorageOperationOptions, 
  StorageOperationResult,
  FileNotFoundError,
  StorageError,
  DirectoryOperationOptions,
  DirectoryOperationResult
} from './interfaces';
import { join, dirname } from 'path';
import { lookup } from 'mime-types';

interface MemoryFile {
  content: Buffer;
  metadata: StorageMetadata;
}

export interface MemoryStorageOptions {
  basePath?: string;
  operationTimeout?: number;
}

/**
 * In-memory storage provider implementation.
 * Useful for testing and temporary storage needs.
 */
export class MemoryStorageProvider extends BaseStorageProvider {
  private files: Map<string, MemoryFile>;

  constructor(options: MemoryStorageOptions = {}) {
    super({
      basePath: options.basePath || process.cwd(),
      operationTimeout: options.operationTimeout
    });
    this.files = new Map();
  }

  protected normalizePath(path: string): string {
    return join('/', path).replace(/\\/g, '/');
  }

  protected getRelativePath(path: string): string {
    return path.startsWith('/') ? path.slice(1) : path;
  }

  protected createMetadata(path: string, size: number, options: { isDirectory?: boolean } = {}): StorageMetadata {
    const now = new Date();
    const metadata: StorageMetadata = {
      name: path.split('/').pop() || '',
      size,
      mimeType: options.isDirectory ? 'inode/directory' : lookup(path) || 'application/octet-stream',
      createdAt: now,
      modifiedAt: now
    };

    if (options.isDirectory) {
      metadata.metadata = { isDirectory: true };
    }

    return metadata;
  }

  protected isDirectory(path: string): boolean {
    const file = this.files.get(this.getRelativePath(this.normalizePath(path)));
    return file?.metadata.metadata?.isDirectory === true;
  }

  private getDirectoryContents(path: string, recursive: boolean = false): string[] {
    const normalizedPath = this.getRelativePath(this.normalizePath(path));
    const prefix = normalizedPath ? normalizedPath + '/' : '';
    const contents: string[] = [];

    for (const [filePath, file] of this.files.entries()) {
      if (filePath.startsWith(prefix)) {
        const relativePath = filePath.slice(prefix.length);
        if (!recursive && relativePath.includes('/')) {
          const firstLevel = relativePath.split('/')[0];
          if (!contents.includes(prefix + firstLevel)) {
            contents.push(prefix + firstLevel);
          }
        } else {
          contents.push(filePath);
        }
      }
    }

    return contents;
  }

  async save(
    path: string,
    data: string | Buffer,
    options?: StorageOperationOptions
  ): Promise<StorageOperationResult> {
    return this.withTimeout(async () => {
      const normalizedPath = this.getRelativePath(this.normalizePath(path));
      await this.validateOverwrite(normalizedPath, options);

      const content = Buffer.isBuffer(data) ? data : Buffer.from(data);
      const metadata = this.createMetadata(normalizedPath, content.length);

      this.files.set(normalizedPath, { content, metadata });

      return {
        path: normalizedPath,
        metadata
      };
    }, path, 'save');
  }

  async read(path: string): Promise<Buffer> {
    return this.withTimeout(async () => {
      const normalizedPath = this.getRelativePath(this.normalizePath(path));
      const file = this.files.get(normalizedPath);

      if (!file) {
        throw new FileNotFoundError(path);
      }

      return file.content;
    }, path, 'read');
  }

  async delete(path: string): Promise<boolean> {
    return this.withTimeout(async () => {
      const normalizedPath = this.getRelativePath(this.normalizePath(path));
      return this.files.delete(normalizedPath);
    }, path, 'delete');
  }

  async exists(path: string): Promise<boolean> {
    return this.withTimeout(async () => {
      const normalizedPath = this.getRelativePath(this.normalizePath(path));
      return this.files.has(normalizedPath);
    }, path, 'exists');
  }

  async list(path: string = '', recursive: boolean = false): Promise<string[]> {
    return this.withTimeout(async () => {
      const normalizedBasePath = this.getRelativePath(this.normalizePath(path));
      const prefix = normalizedBasePath ? normalizedBasePath + '/' : '';
      
      return Array.from(this.files.keys())
        .filter(filePath => {
          if (!filePath.startsWith(prefix)) {
            return false;
          }
          
          if (!recursive) {
            const relativePath = filePath.slice(prefix.length);
            return !relativePath.includes('/');
          }
          
          return true;
        });
    }, path, 'list');
  }

  async getMetadata(path: string): Promise<StorageMetadata> {
    return this.withTimeout(async () => {
      const normalizedPath = this.getRelativePath(this.normalizePath(path));
      const file = this.files.get(normalizedPath);

      if (!file) {
        throw new FileNotFoundError(path);
      }

      return file.metadata;
    }, path, 'getMetadata');
  }

  getUrl(path: string): string {
    const normalizedPath = this.getRelativePath(this.normalizePath(path));
    return `memory://${normalizedPath}`;
  }

  async copy(
    sourcePath: string,
    targetPath: string,
    options?: StorageOperationOptions
  ): Promise<StorageOperationResult> {
    return this.withTimeout(async () => {
      const normalizedSource = this.getRelativePath(this.normalizePath(sourcePath));
      const normalizedTarget = this.getRelativePath(this.normalizePath(targetPath));
      
      const sourceFile = this.files.get(normalizedSource);
      if (!sourceFile) {
        throw new FileNotFoundError(sourcePath);
      }

      await this.validateOverwrite(normalizedTarget, options);

      const newMetadata = this.createMetadata(
        normalizedTarget,
        sourceFile.content.length,
        sourceFile.metadata.metadata
      );

      this.files.set(normalizedTarget, {
        content: Buffer.from(sourceFile.content),
        metadata: newMetadata
      });

      return {
        path: normalizedTarget,
        metadata: newMetadata
      };
    }, sourcePath, 'copy');
  }

  async move(
    sourcePath: string,
    targetPath: string,
    options?: StorageOperationOptions
  ): Promise<StorageOperationResult> {
    return this.withTimeout(async () => {
      const normalizedSource = this.getRelativePath(this.normalizePath(sourcePath));
      const normalizedTarget = this.getRelativePath(this.normalizePath(targetPath));
      
      const sourceFile = this.files.get(normalizedSource);
      if (!sourceFile) {
        throw new FileNotFoundError(sourcePath);
      }

      await this.validateOverwrite(normalizedTarget, options);

      const newMetadata = this.createMetadata(
        normalizedTarget,
        sourceFile.content.length,
        sourceFile.metadata.metadata
      );

      this.files.set(normalizedTarget, {
        content: sourceFile.content,
        metadata: newMetadata
      });
      this.files.delete(normalizedSource);

      return {
        path: normalizedTarget,
        metadata: newMetadata
      };
    }, sourcePath, 'move');
  }

  async createDirectory(
    path: string,
    options: DirectoryOperationOptions = {}
  ): Promise<DirectoryOperationResult> {
    return this.withTimeout(async () => {
      const normalizedPath = this.getRelativePath(this.normalizePath(path));
      
      // Check if directory already exists
      if (this.files.has(normalizedPath)) {
        return {
          path: normalizedPath,
          success: false,
          error: new StorageError('Directory already exists', 'DIR_EXISTS', path)
        };
      }

      // Create parent directories if needed
      if (options.createParents) {
        const parentPath = dirname(normalizedPath);
        if (parentPath !== '.' && !this.files.has(parentPath)) {
          await this.createDirectory(parentPath, options);
        }
      }

      // Create an empty entry to represent the directory
      this.files.set(normalizedPath, {
        content: Buffer.alloc(0),
        metadata: this.createMetadata(normalizedPath, 0, { isDirectory: true })
      });

      return {
        path: normalizedPath,
        success: true
      };
    }, path, 'createDirectory');
  }

  async removeDirectory(
    path: string,
    options: DirectoryOperationOptions = {}
  ): Promise<DirectoryOperationResult> {
    return this.withTimeout(async () => {
      const normalizedPath = this.getRelativePath(this.normalizePath(path));
      
      // Check if directory exists
      if (!this.files.has(normalizedPath)) {
        return {
          path: normalizedPath,
          success: false,
          error: new FileNotFoundError(path)
        };
      }

      // Check if it's actually a directory
      if (!this.isDirectory(normalizedPath)) {
        return {
          path: normalizedPath,
          success: false,
          error: new StorageError('Path is not a directory', 'NOT_A_DIRECTORY', path)
        };
      }

      // Get directory contents
      const contents = this.getDirectoryContents(normalizedPath);
      
      // Check if directory is empty when failIfNotEmpty is true
      if (options.failIfNotEmpty && contents.length > 0) {
        return {
          path: normalizedPath,
          success: false,
          error: new StorageError('Directory is not empty', 'DIR_NOT_EMPTY', path)
        };
      }

      // Remove all contents and the directory itself
      contents.forEach(filePath => this.files.delete(filePath));
      this.files.delete(normalizedPath);

      return {
        path: normalizedPath,
        success: true
      };
    }, path, 'removeDirectory');
  }

  async listDirectory(
    path: string,
    options: {
      recursive?: boolean;
      filter?: (path: string) => boolean;
      includeDirectories?: boolean;
    } = {}
  ): Promise<string[]> {
    return this.withTimeout(async () => {
      const normalizedPath = this.getRelativePath(this.normalizePath(path));
      
      // Check if directory exists
      if (!this.files.has(normalizedPath)) {
        throw new FileNotFoundError(path);
      }

      // Check if it's actually a directory
      if (!this.isDirectory(normalizedPath)) {
        throw new StorageError('Path is not a directory', 'NOT_A_DIRECTORY', path);
      }

      // Get directory contents
      let contents = this.getDirectoryContents(normalizedPath, options.recursive);

      // Apply directory filter if needed
      if (!options.includeDirectories) {
        contents = contents.filter(path => !this.isDirectory(path));
      }

      // Apply custom filter if provided
      if (options.filter) {
        contents = contents.filter(options.filter);
      }

      return contents;
    }, path, 'listDirectory');
  }

  async clear(): Promise<void> {
    this.files.clear();
  }
} 