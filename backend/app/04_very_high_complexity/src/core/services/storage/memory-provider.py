from typing import Any, Dict, List



  StorageMetadata, 
  StorageOperationOptions, 
  StorageOperationResult,
  FileNotFoundError,
  StorageError,
  DirectoryOperationOptions,
  DirectoryOperationResult
} from './interfaces'
class MemoryFile:
    content: Buffer
    metadata: StorageMetadata
class MemoryStorageOptions:
    basePath?: str
    operationTimeout?: float
/**
 * In-memory storage provider implementation.
 * Useful for testing and temporary storage needs.
 */
class MemoryStorageProvider extends BaseStorageProvider {
  private files: Map<string, MemoryFile>
  constructor(options: \'MemoryStorageOptions\' = {}) {
    super({
      basePath: options.basePath || process.cwd(),
      operationTimeout: options.operationTimeout
    })
    this.files = new Map()
  }
  protected normalizePath(path: str): str {
    return join('/', path).replace(/\\/g, '/')
  }
  protected getRelativePath(path: str): str {
    return path.startsWith('/') ? path.slice(1) : path
  }
  protected createMetadata(path: str, size: float, options: Dict[str, Any] = {}): StorageMetadata {
    const now = new Date()
    const metadata: StorageMetadata = {
      name: path.split('/').pop() || '',
      size,
      mimeType: options.isDirectory ? 'inode/directory' : lookup(path) || 'application/octet-stream',
      createdAt: now,
      modifiedAt: now
    }
    if (options.isDirectory) {
      metadata.metadata = { isDirectory: true }
    }
    return metadata
  }
  protected isDirectory(path: str): bool {
    const file = this.files.get(this.getRelativePath(this.normalizePath(path)))
    return file?.metadata.metadata?.isDirectory === true
  }
  private getDirectoryContents(path: str, recursive: bool = false): string[] {
    const normalizedPath = this.getRelativePath(this.normalizePath(path))
    const prefix = normalizedPath ? normalizedPath + '/' : ''
    const contents: List[string] = []
    for (const [filePath, file] of this.files.entries()) {
      if (filePath.startsWith(prefix)) {
        const relativePath = filePath.slice(prefix.length)
        if (!recursive && relativePath.includes('/')) {
          const firstLevel = relativePath.split('/')[0]
          if (!contents.includes(prefix + firstLevel)) {
            contents.push(prefix + firstLevel)
          }
        } else {
          contents.push(filePath)
        }
      }
    }
    return contents
  }
  async save(
    path: str,
    data: str | Buffer,
    options?: StorageOperationOptions
  ): Promise<StorageOperationResult> {
    return this.withTimeout(async () => {
      const normalizedPath = this.getRelativePath(this.normalizePath(path))
      await this.validateOverwrite(normalizedPath, options)
      const content = Buffer.isBuffer(data) ? data : Buffer.from(data)
      const metadata = this.createMetadata(normalizedPath, content.length)
      this.files.set(normalizedPath, { content, metadata })
      return {
        path: normalizedPath,
        metadata
      }
    }, path, 'save')
  }
  async read(path: str): Promise<Buffer> {
    return this.withTimeout(async () => {
      const normalizedPath = this.getRelativePath(this.normalizePath(path))
      const file = this.files.get(normalizedPath)
      if (!file) {
        throw new FileNotFoundError(path)
      }
      return file.content
    }, path, 'read')
  }
  async delete(path: str): Promise<boolean> {
    return this.withTimeout(async () => {
      const normalizedPath = this.getRelativePath(this.normalizePath(path))
      return this.files.delete(normalizedPath)
    }, path, 'delete')
  }
  async exists(path: str): Promise<boolean> {
    return this.withTimeout(async () => {
      const normalizedPath = this.getRelativePath(this.normalizePath(path))
      return this.files.has(normalizedPath)
    }, path, 'exists')
  }
  async list(path: str = '', recursive: bool = false): Promise<string[]> {
    return this.withTimeout(async () => {
      const normalizedBasePath = this.getRelativePath(this.normalizePath(path))
      const prefix = normalizedBasePath ? normalizedBasePath + '/' : ''
      return Array.from(this.files.keys())
        .filter(filePath => {
          if (!filePath.startsWith(prefix)) {
            return false
          }
          if (!recursive) {
            const relativePath = filePath.slice(prefix.length)
            return !relativePath.includes('/')
          }
          return true
        })
    }, path, 'list')
  }
  async getMetadata(path: str): Promise<StorageMetadata> {
    return this.withTimeout(async () => {
      const normalizedPath = this.getRelativePath(this.normalizePath(path))
      const file = this.files.get(normalizedPath)
      if (!file) {
        throw new FileNotFoundError(path)
      }
      return file.metadata
    }, path, 'getMetadata')
  }
  getUrl(path: str): str {
    const normalizedPath = this.getRelativePath(this.normalizePath(path))
    return `memory:
  }
  async copy(
    sourcePath: str,
    targetPath: str,
    options?: StorageOperationOptions
  ): Promise<StorageOperationResult> {
    return this.withTimeout(async () => {
      const normalizedSource = this.getRelativePath(this.normalizePath(sourcePath))
      const normalizedTarget = this.getRelativePath(this.normalizePath(targetPath))
      const sourceFile = this.files.get(normalizedSource)
      if (!sourceFile) {
        throw new FileNotFoundError(sourcePath)
      }
      await this.validateOverwrite(normalizedTarget, options)
      const newMetadata = this.createMetadata(
        normalizedTarget,
        sourceFile.content.length,
        sourceFile.metadata.metadata
      )
      this.files.set(normalizedTarget, {
        content: Buffer.from(sourceFile.content),
        metadata: newMetadata
      })
      return {
        path: normalizedTarget,
        metadata: newMetadata
      }
    }, sourcePath, 'copy')
  }
  async move(
    sourcePath: str,
    targetPath: str,
    options?: StorageOperationOptions
  ): Promise<StorageOperationResult> {
    return this.withTimeout(async () => {
      const normalizedSource = this.getRelativePath(this.normalizePath(sourcePath))
      const normalizedTarget = this.getRelativePath(this.normalizePath(targetPath))
      const sourceFile = this.files.get(normalizedSource)
      if (!sourceFile) {
        throw new FileNotFoundError(sourcePath)
      }
      await this.validateOverwrite(normalizedTarget, options)
      const newMetadata = this.createMetadata(
        normalizedTarget,
        sourceFile.content.length,
        sourceFile.metadata.metadata
      )
      this.files.set(normalizedTarget, {
        content: sourceFile.content,
        metadata: newMetadata
      })
      this.files.delete(normalizedSource)
      return {
        path: normalizedTarget,
        metadata: newMetadata
      }
    }, sourcePath, 'move')
  }
  async createDirectory(
    path: str,
    options: DirectoryOperationOptions = {}
  ): Promise<DirectoryOperationResult> {
    return this.withTimeout(async () => {
      const normalizedPath = this.getRelativePath(this.normalizePath(path))
      if (this.files.has(normalizedPath)) {
        return {
          path: normalizedPath,
          success: false,
          error: new StorageError('Directory already exists', 'DIR_EXISTS', path)
        }
      }
      if (options.createParents) {
        const parentPath = dirname(normalizedPath)
        if (parentPath !== '.' && !this.files.has(parentPath)) {
          await this.createDirectory(parentPath, options)
        }
      }
      this.files.set(normalizedPath, {
        content: Buffer.alloc(0),
        metadata: this.createMetadata(normalizedPath, 0, { isDirectory: true })
      })
      return {
        path: normalizedPath,
        success: true
      }
    }, path, 'createDirectory')
  }
  async removeDirectory(
    path: str,
    options: DirectoryOperationOptions = {}
  ): Promise<DirectoryOperationResult> {
    return this.withTimeout(async () => {
      const normalizedPath = this.getRelativePath(this.normalizePath(path))
      if (!this.files.has(normalizedPath)) {
        return {
          path: normalizedPath,
          success: false,
          error: new FileNotFoundError(path)
        }
      }
      if (!this.isDirectory(normalizedPath)) {
        return {
          path: normalizedPath,
          success: false,
          error: new StorageError('Path is not a directory', 'NOT_A_DIRECTORY', path)
        }
      }
      const contents = this.getDirectoryContents(normalizedPath)
      if (options.failIfNotEmpty && contents.length > 0) {
        return {
          path: normalizedPath,
          success: false,
          error: new StorageError('Directory is not empty', 'DIR_NOT_EMPTY', path)
        }
      }
      contents.forEach(filePath => this.files.delete(filePath))
      this.files.delete(normalizedPath)
      return {
        path: normalizedPath,
        success: true
      }
    }, path, 'removeDirectory')
  }
  async listDirectory(
    path: str,
    options: Dict[str, Any] = {}
  ): Promise<string[]> {
    return this.withTimeout(async () => {
      const normalizedPath = this.getRelativePath(this.normalizePath(path))
      if (!this.files.has(normalizedPath)) {
        throw new FileNotFoundError(path)
      }
      if (!this.isDirectory(normalizedPath)) {
        throw new StorageError('Path is not a directory', 'NOT_A_DIRECTORY', path)
      }
      let contents = this.getDirectoryContents(normalizedPath, options.recursive)
      if (!options.includeDirectories) {
        contents = contents.filter(path => !this.isDirectory(path))
      }
      if (options.filter) {
        contents = contents.filter(options.filter)
      }
      return contents
    }, path, 'listDirectory')
  }
  async clear(): Promise<void> {
    this.files.clear()
  }
} 