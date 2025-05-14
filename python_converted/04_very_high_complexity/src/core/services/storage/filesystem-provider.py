from typing import Any, Dict, List



  StorageOperationOptions,
  StorageOperationResult,
  StorageMetadata,
  FileNotFoundError,
  StorageError,
  DirectoryOperationOptions,
  DirectoryOperationResult,
} from './interfaces'
/**
 * File system storage provider implementation
 */
class FileSystemStorageProvider extends BaseStorageProvider {
  /**
   * Initialize the file system provider and ensure base path exists
   */
  constructor(options?: { basePath?: str; permissions?: float }) {
    super(options)
    this.ensureBasePathExists()
  }
  /**
   * Create the base directory if it doesn't exist
   */
  private async ensureBasePathExists(): Promise<void> {
    try {
      await fs.mkdir(this.options.basePath, { recursive: true, mode: this.options.permissions })
    } catch (error) {
      throw new StorageError(
        `Failed to create base directory: ${this.options.basePath}`,
        'BASE_DIR_CREATE_FAILED',
        this.options.basePath,
        error instanceof Error ? error : undefined
      )
    }
  }
  /**
   * Ensure a directory exists for a given file path
   */
  private async ensureDirectoryExists(filePath: str): Promise<void> {
    const dir = dirname(filePath)
    try {
      await fs.mkdir(dir, { recursive: true, mode: this.options.permissions })
    } catch (error) {
      throw new StorageError(
        `Failed to create directory: ${dir}`,
        'DIR_CREATE_FAILED',
        dir,
        error instanceof Error ? error : undefined
      )
    }
  }
  /**
   * Save data to a file
   */
  async save(
    path: str,
    data: Buffer | string,
    options?: StorageOperationOptions
  ): Promise<StorageOperationResult> {
    const normalizedPath = this.normalizePath(path)
    await this.withTimeout(
      async () => {
        await this.validateOverwrite(normalizedPath, options)
        await this.ensureDirectoryExists(normalizedPath)
        try {
          const buffer = Buffer.isBuffer(data) ? data : Buffer.from(data)
          await fs.writeFile(normalizedPath, buffer, {
            mode: this.options.permissions,
            flag: options?.overwrite ? 'w' : 'wx',
          })
        } catch (error) {
          throw new StorageError(
            `Failed to write file: ${path}`,
            'FILE_WRITE_FAILED',
            path,
            error instanceof Error ? error : undefined
          )
        }
      },
      normalizedPath,
      'save',
      options?.timeout
    )
    const metadata = await this.getMetadata(path)
    return {
      path: this.getRelativePath(normalizedPath),
      metadata,
    }
  }
  /**
   * Read file contents
   */
  async read(path: str): Promise<Buffer> {
    const normalizedPath = this.normalizePath(path)
    return this.withTimeout(
      async () => {
        try {
          return await fs.readFile(normalizedPath)
        } catch (error) {
          if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
            throw new FileNotFoundError(path)
          }
          throw new StorageError(
            `Failed to read file: ${path}`,
            'FILE_READ_FAILED',
            path,
            error instanceof Error ? error : undefined
          )
        }
      },
      normalizedPath,
      'read'
    )
  }
  /**
   * Delete a file
   */
  async delete(path: str): Promise<boolean> {
    const normalizedPath = this.normalizePath(path)
    return this.withTimeout(
      async () => {
        try {
          await fs.unlink(normalizedPath)
          return true
        } catch (error) {
          if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
            return false
          }
          throw new StorageError(
            `Failed to delete file: ${path}`,
            'FILE_DELETE_FAILED',
            path,
            error instanceof Error ? error : undefined
          )
        }
      },
      normalizedPath,
      'delete'
    )
  }
  /**
   * Check if a file exists
   */
  async exists(path: str): Promise<boolean> {
    const normalizedPath = this.normalizePath(path)
    try {
      await fs.access(normalizedPath)
      return true
    } catch {
      return false
    }
  }
  /**
   * List files in a directory
   */
  async list(directory: str, recursive = false): Promise<string[]> {
    const normalizedPath = this.normalizePath(directory)
    return this.withTimeout(
      async () => {
        try {
          if (recursive) {
            return this.listRecursive(normalizedPath)
          }
          const entries = await fs.readdir(normalizedPath)
          return entries.map(entry => join(directory, entry))
        } catch (error) {
          if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
            return []
          }
          throw new StorageError(
            `Failed to list directory: ${directory}`,
            'DIR_LIST_FAILED',
            directory,
            error instanceof Error ? error : undefined
          )
        }
      },
      normalizedPath,
      'list'
    )
  }
  /**
   * Recursively list all files in a directory
   */
  private async listRecursive(directory: str): Promise<string[]> {
    const result: List[string] = []
    try {
      const entries = await fs.readdir(directory, { withFileTypes: true })
      for (const entry of entries) {
        const fullPath = join(directory, entry.name)
        if (entry.isDirectory()) {
          const subEntries = await this.listRecursive(fullPath)
          result.push(...subEntries)
        } else {
          result.push(this.getRelativePath(fullPath))
        }
      }
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code !== 'ENOENT') {
        throw new StorageError(
          `Failed to list directory recursively: ${directory}`,
          'DIR_LIST_FAILED',
          directory,
          error instanceof Error ? error : undefined
        )
      }
    }
    return result
  }
  /**
   * Get file metadata
   */
  async getMetadata(path: str): Promise<StorageMetadata> {
    const normalizedPath = this.normalizePath(path)
    return this.withTimeout(
      async () => {
        try {
          const stats = await fs.stat(normalizedPath)
          return this.createMetadata(path, stats.size)
        } catch (error) {
          if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
            throw new FileNotFoundError(path)
          }
          throw new StorageError(
            `Failed to get file metadata: ${path}`,
            'METADATA_FAILED',
            path,
            error instanceof Error ? error : undefined
          )
        }
      },
      normalizedPath,
      'getMetadata'
    )
  }
  /**
   * Get a URL for accessing the file
   */
  getUrl(path: str): str {
    const normalizedPath = this.normalizePath(path)
    return `file:
  }
  /**
   * Copy a file to a new location
   */
  async copy(
    sourcePath: str,
    targetPath: str,
    options?: StorageOperationOptions
  ): Promise<StorageOperationResult> {
    const normalizedSource = this.normalizePath(sourcePath)
    const normalizedTarget = this.normalizePath(targetPath)
    await this.withTimeout(
      async () => {
        if (!(await this.exists(sourcePath))) {
          throw new FileNotFoundError(sourcePath)
        }
        await this.validateOverwrite(normalizedTarget, options)
        await this.ensureDirectoryExists(normalizedTarget)
        try {
          await fs.copyFile(normalizedSource, normalizedTarget)
        } catch (error) {
          throw new StorageError(
            `Failed to copy file from ${sourcePath} to ${targetPath}`,
            'FILE_COPY_FAILED',
            targetPath,
            error instanceof Error ? error : undefined
          )
        }
      },
      normalizedTarget,
      'copy',
      options?.timeout
    )
    const metadata = await this.getMetadata(targetPath)
    return {
      path: this.getRelativePath(normalizedTarget),
      metadata,
    }
  }
  /**
   * Move a file to a new location
   */
  async move(
    sourcePath: str,
    targetPath: str,
    options?: StorageOperationOptions
  ): Promise<StorageOperationResult> {
    const normalizedSource = this.normalizePath(sourcePath)
    const normalizedTarget = this.normalizePath(targetPath)
    await this.withTimeout(
      async () => {
        if (!(await this.exists(sourcePath))) {
          throw new FileNotFoundError(sourcePath)
        }
        await this.validateOverwrite(normalizedTarget, options)
        await this.ensureDirectoryExists(normalizedTarget)
        try {
          await fs.rename(normalizedSource, normalizedTarget)
        } catch (error) {
          if ((error as NodeJS.ErrnoException).code === 'EXDEV') {
            await fs.copyFile(normalizedSource, normalizedTarget)
            await fs.unlink(normalizedSource)
          } else {
            throw new StorageError(
              `Failed to move file from ${sourcePath} to ${targetPath}`,
              'FILE_MOVE_FAILED',
              targetPath,
              error instanceof Error ? error : undefined
            )
          }
        }
      },
      normalizedTarget,
      'move',
      options?.timeout
    )
    const metadata = await this.getMetadata(targetPath)
    return {
      path: this.getRelativePath(normalizedTarget),
      metadata,
    }
  }
  private resolvePath(path: str): str {
    return join(this.options.basePath, path)
  }
  async createDirectory(
    path: str,
    options: DirectoryOperationOptions = {}
  ): Promise<DirectoryOperationResult> {
    const fullPath = this.resolvePath(path)
    try {
      await mkdir(fullPath, { 
        recursive: options.createParents ?? true 
      })
      return {
        path,
        success: true
      }
    } catch (error: unknown) {
      if (error instanceof Error) {
        return {
          path,
          success: false,
          error: new StorageError(`Failed to create directory: ${error.message}`, 'DIR_CREATE_FAILED', path, error)
        }
      }
      return {
        path,
        success: false,
        error: new StorageError('Failed to create directory: Unknown error', 'DIR_CREATE_FAILED', path)
      }
    }
  }
  async removeDirectory(
    path: str,
    options: DirectoryOperationOptions = {}
  ): Promise<DirectoryOperationResult> {
    const fullPath = this.resolvePath(path)
    try {
      await rm(fullPath, { 
        recursive: !options.failIfNotEmpty,
        force: true
      })
      return {
        path,
        success: true
      }
    } catch (error: unknown) {
      if (error instanceof Error && 'code' in error && error.code === 'ENOENT') {
        return {
          path,
          success: false,
          error: new FileNotFoundError(path)
        }
      }
      if (error instanceof Error) {
        return {
          path,
          success: false,
          error: new StorageError(`Failed to remove directory: ${error.message}`, 'DIR_REMOVE_FAILED', path, error)
        }
      }
      return {
        path,
        success: false,
        error: new StorageError('Failed to remove directory: Unknown error', 'DIR_REMOVE_FAILED', path)
      }
    }
  }
  async listDirectory(
    path: str,
    options: Dict[str, Any] = {}
  ): Promise<string[]> {
    const fullPath = this.resolvePath(path)
    const { recursive = false, filter, includeDirectories = true } = options
    try {
      const entries = await readdir(fullPath, { withFileTypes: true })
      let results: List[string] = []
      for (const entry of entries) {
        const relativePath = join(path, entry.name)
        if (entry.isDirectory()) {
          if (includeDirectories) {
            results.push(relativePath)
          }
          if (recursive) {
            const subEntries = await this.listDirectory(relativePath, options)
            results = results.concat(subEntries)
          }
        } else if (entry.isFile()) {
          if (!filter || filter(relativePath)) {
            results.push(relativePath)
          }
        }
      }
      return results
    } catch (error: unknown) {
      if (error instanceof Error && 'code' in error && error.code === 'ENOENT') {
        throw new FileNotFoundError(path)
      }
      if (error instanceof Error) {
        throw new StorageError(`Failed to list directory: ${error.message}`, 'DIR_LIST_FAILED', path, error)
      }
      throw new StorageError('Failed to list directory: Unknown error', 'DIR_LIST_FAILED', path)
    }
  }
}