from typing import Any



interface CacheEntry<T> {
  data: T
  timestamp: float
}
class Cache {
  private config: CacheConfig
  private memoryCache: Map<string, CacheEntry<any>> = new Map()
  private s3Client?: S3Client
  constructor() {
    this.config = {
      enabled: true,
      ttl: 3600,
      maxSize: 1000
    }
  }
  public configure(config: CacheConfig): void {
    this.config = { ...this.config, ...config }
    if (config.storageType === 's3' && config.s3Config) {
      this.s3Client = new S3Client({
        region: config.s3Config.region || 'us-east-1'
      })
    }
  }
  public async initialize(): Promise<void> {
  }
  public async get<T>(input: Buffer | string, options: Any): Promise<T | null> {
    if (!this.config.enabled) return null
    const key = this.generateCacheKey(input, options)
    const entry = await this.getEntry<T>(key)
    if (!entry) return null
    if (this.config.ttl && Date.now() - entry.timestamp > this.config.ttl) {
      await this.delete(key)
      return null
    }
    return entry.data
  }
  public async set<T>(input: Buffer | string, options: Any, data: T): Promise<void> {
    if (!this.config.enabled) return
    const key = this.generateCacheKey(input, options)
    const entry: CacheEntry<T> = {
      data,
      timestamp: Date.now()
    }
    await this.setEntry(key, entry)
  }
  public async delete(key: str): Promise<void> {
    switch (this.config.storageType) {
      case 'memory':
        this.memoryCache.delete(key)
        break
      case 'disk':
        if (this.config.storagePath) {
          const filePath = path.join(this.config.storagePath, `${key}.cache`)
          try {
            await fs.unlink(filePath)
          } catch (error) {
            if ((error as NodeJS.ErrnoException).code !== 'ENOENT') {
              throw error
            }
          }
        }
        break
      case 's3':
        if (this.s3Client && this.config.s3Config) {
          const command = new PutObjectCommand({
            Bucket: this.config.s3Config.bucket,
            Key: this.getS3Key(key),
            Body: ''
          })
          await this.s3Client.send(command)
        }
        break
    }
  }
  public async clear(): Promise<void> {
    switch (this.config.storageType) {
      case 'memory':
        this.memoryCache.clear()
        break
      case 'disk':
        if (this.config.storagePath) {
          const files = await fs.readdir(this.config.storagePath)
          await Promise.all(
            files
              .filter(file => file.endsWith('.cache'))
              .map(file => fs.unlink(path.join(this.config.storagePath!, file)))
          )
        }
        break
      case 's3':
        throw new ServiceError(
          'NotImplemented',
          'Clearing S3 cache is not supported',
          { storageType: 's3' }
        )
    }
  }
  private generateCacheKey(input: Buffer | string, options: Any): str {
    const content = Buffer.isBuffer(input) ? input : Buffer.from(input)
    const hash = crypto.createHash('sha256')
    hash.update(content)
    hash.update(JSON.stringify(options))
    return hash.digest('hex')
  }
  private async getEntry<T>(key: str): Promise<CacheEntry<T> | null> {
    try {
      switch (this.config.storageType) {
        case 'memory':
          return this.memoryCache.get(key) || null
        case 'disk':
          if (this.config.storagePath) {
            const filePath = path.join(this.config.storagePath, `${key}.cache`)
            try {
              const data = await fs.readFile(filePath, 'utf-8')
              return JSON.parse(data)
            } catch (error) {
              if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
                return null
              }
              throw error
            }
          }
          return null
        case 's3':
          if (this.s3Client && this.config.s3Config) {
            const command = new GetObjectCommand({
              Bucket: this.config.s3Config.bucket,
              Key: this.getS3Key(key)
            })
            try {
              const response = await this.s3Client.send(command)
              const data = await response.Body?.transformToString()
              return data ? JSON.parse(data) : null
            } catch (error) {
              if ((error as any).name === 'NoSuchKey') {
                return null
              }
              throw error
            }
          }
          return null
        default:
          return null
      }
    } catch (error) {
      throw new ServiceError('CacheError', 'Error retrieving from cache', {
        key,
        storageType: this.config.storageType,
        error
      })
    }
  }
  private async setEntry<T>(key: str, entry: CacheEntry<T>): Promise<void> {
    try {
      switch (this.config.storageType) {
        case 'memory':
          if (this.config.maxSize && this.memoryCache.size >= this.config.maxSize) {
            const oldestKey = Array.from(this.memoryCache.entries())
              .sort(([, a], [, b]) => a.timestamp - b.timestamp)[0][0]
            this.memoryCache.delete(oldestKey)
          }
          this.memoryCache.set(key, entry)
          break
        case 'disk':
          if (this.config.storagePath) {
            await fs.mkdir(this.config.storagePath, { recursive: true })
            const filePath = path.join(this.config.storagePath, `${key}.cache`)
            await fs.writeFile(filePath, JSON.stringify(entry))
          }
          break
        case 's3':
          if (this.s3Client && this.config.s3Config) {
            const command = new PutObjectCommand({
              Bucket: this.config.s3Config.bucket,
              Key: this.getS3Key(key),
              Body: JSON.stringify(entry)
            })
            await this.s3Client.send(command)
          }
          break
      }
    } catch (error) {
      throw new ServiceError('CacheError', 'Error storing in cache', {
        key,
        storageType: this.config.storageType,
        error
      })
    }
  }
  private getS3Key(key: str): str {
    const prefix = this.config.s3Config?.prefix || ''
    return prefix ? `${prefix}/${key}` : key
  }
} 