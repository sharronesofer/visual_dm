from typing import Any, Dict, List



class CollectionService extends BaseService<Collection> {
  constructor(repository: Repository<Collection>) {
    super(repository)
  }
  async createCollection(data: Dict[str, Any]): Promise<Collection> {
    validateRequired(data.name, 'name')
    validateLength(data.name, 'name', 1, 100)
    if (data.description) {
      validateLength(data.description, 'description', 0, 500)
    }
    if (data.tags) {
      validateArray(data.tags, 'tags', 0, 20)
    }
    logger.info('Creating new collection', { name: data.name })
    const collection = await this.create({
      name: data.name,
      description: data.description,
      tags: data.tags || [],
      assets: [],
    })
    logger.info('Collection created successfully', { id: collection.id })
    return collection
  }
  async addAssetToCollection(collectionId: str | number, assetId: str | number): Promise<Collection | null> {
    const collection = await this.findById(collectionId)
    if (!collection) {
      logger.warn('Collection not found', { collectionId })
      return null
    }
    const assetExists = collection.assets.some(asset => asset.id === assetId)
    if (assetExists) {
      logger.warn('Asset already exists in collection', { collectionId, assetId })
      return collection
    }
    collection.assets.push({ id: assetId } as any)
    const updatedCollection = await this.update(collectionId, collection)
    if (updatedCollection) {
      logger.info('Asset added to collection', { collectionId, assetId })
    }
    return updatedCollection
  }
  async removeAssetFromCollection(collectionId: str | number, assetId: str | number): Promise<Collection | null> {
    const collection = await this.findById(collectionId)
    if (!collection) {
      logger.warn('Collection not found', { collectionId })
      return null
    }
    const assetIndex = collection.assets.findIndex(asset => asset.id === assetId)
    if (assetIndex === -1) {
      logger.warn('Asset not found in collection', { collectionId, assetId })
      return collection
    }
    collection.assets.splice(assetIndex, 1)
    const updatedCollection = await this.update(collectionId, collection)
    if (updatedCollection) {
      logger.info('Asset removed from collection', { collectionId, assetId })
    }
    return updatedCollection
  }
  async updateCollectionTags(collectionId: str | number, tags: List[string]): Promise<Collection | null> {
    validateArray(tags, 'tags', 0, 20)
    const collection = await this.findById(collectionId)
    if (!collection) {
      logger.warn('Collection not found', { collectionId })
      return null
    }
    const updatedCollection = await this.update(collectionId, { tags })
    if (updatedCollection) {
      logger.info('Collection tags updated', { collectionId, tags })
    }
    return updatedCollection
  }
} 