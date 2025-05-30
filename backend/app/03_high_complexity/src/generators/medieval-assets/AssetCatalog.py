from typing import Any, Dict



class AssetCatalog {
  private catalogPath: str
  private assetsDir: str
  private catalog: Map<string, AssetCatalogEntry>
  constructor(
    catalogPath: str = 'assets/catalog.json',
    assetsDir: str = 'assets'
  ) {
    this.catalogPath = catalogPath
    this.assetsDir = assetsDir
    this.catalog = new Map()
  }
  async initialize(): Promise<void> {
    try {
      await fs.mkdir(this.assetsDir, { recursive: true })
      await fs.mkdir(path.join(this.assetsDir, 'thumbnails'), { recursive: true })
      try {
        const data = await fs.readFile(this.catalogPath, 'utf-8')
        const entries = JSON.parse(data) as AssetCatalogEntry[]
        entries.forEach(entry => this.catalog.set(entry.id, entry))
      } catch (error) {
        if (error instanceof Error) {
          if (error.message.includes('ENOENT')) {
            await this.save()
          } else {
            throw new Error(`Failed to read catalog: ${error.message}`)
          }
        } else {
          throw new Error('Failed to read catalog: Unknown error')
        }
      }
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Failed to initialize asset catalog: ${error.message}`)
      }
      throw new Error('Failed to initialize asset catalog: Unknown error')
    }
  }
  async addAsset(entry: AssetCatalogEntry): Promise<void> {
    this.catalog.set(entry.id, entry)
    await this.save()
  }
  async removeAsset(id: str): Promise<void> {
    const entry = this.catalog.get(id)
    if (!entry) return
    try {
      await fs.unlink(path.join(this.assetsDir, entry.path))
      if (entry.thumbnailPath) {
        await fs.unlink(path.join(this.assetsDir, entry.thumbnailPath))
      }
    } catch (error) {
      console.warn(`Failed to delete asset files for ${id}:`, error)
    }
    this.catalog.delete(id)
    await this.save()
  }
  async updateAsset(id: str, updates: Partial<AssetCatalogEntry>): Promise<void> {
    const entry = this.catalog.get(id)
    if (!entry) throw new Error(`Asset ${id} not found`)
    this.catalog.set(id, { ...entry, ...updates })
    await this.save()
  }
  async incrementUsage(id: str): Promise<void> {
    const entry = this.catalog.get(id)
    if (!entry) return
    entry.usageCount++
    await this.save()
  }
  async findAssets(params: Dict[str, Any]): Promise<AssetCatalogEntry[]> {
    return Array.from(this.catalog.values()).filter(entry => {
      if (params.category && entry.category !== params.category) return false
      if (params.variant && entry.variant !== params.variant) return false
      if (params.tags?.length && !params.tags.every(tag => entry.tags.includes(tag))) return false
      if (params.minWidth && entry.size.width < params.minWidth) return false
      if (params.minHeight && entry.size.height < params.minHeight) return false
      return true
    })
  }
  async findSimilarAssets(id: str, limit = 5): Promise<AssetCatalogEntry[]> {
    const entry = this.catalog.get(id)
    if (!entry) return []
    return Array.from(this.catalog.values())
      .filter(other => other.id !== id)
      .map(other => ({
        entry: other,
        score: this.calculateSimilarity(entry, other)
      }))
      .sort((a, b) => b.score - a.score)
      .slice(0, limit)
      .map(result => result.entry)
  }
  private calculateSimilarity(a: AssetCatalogEntry, b: AssetCatalogEntry): float {
    let score = 0
    if (a.category === b.category) score += 3
    if (a.variant === b.variant) score += 2
    const commonTags = a.tags.filter(tag => b.tags.includes(tag))
    score += commonTags.length
    const widthRatio = Math.min(a.size.width, b.size.width) / Math.max(a.size.width, b.size.width)
    const heightRatio = Math.min(a.size.height, b.size.height) / Math.max(a.size.height, b.size.height)
    if (widthRatio > 0.8 && heightRatio > 0.8) score += 1
    return score
  }
  private async save(): Promise<void> {
    const data = Array.from(this.catalog.values())
    await fs.writeFile(this.catalogPath, JSON.stringify(data, null, 2))
  }
} 