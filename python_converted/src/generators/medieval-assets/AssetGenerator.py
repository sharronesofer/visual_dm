from typing import Any, List


  AssetRequest,
  GeneratedAsset,
  GenerationConfig,
  PostProcessingConfig,
  AssetMetadata
} from './types'
class AssetGenerator {
  private sdService: StableDiffusionService
  private imageProcessor: ImageProcessor
  private assetCatalog: AssetCatalog
  constructor(
    sdService: StableDiffusionService,
    imageProcessor: ImageProcessor,
    assetCatalog: AssetCatalog
  ) {
    this.sdService = sdService
    this.imageProcessor = imageProcessor
    this.assetCatalog = assetCatalog
  }
  async generateAsset(request: AssetRequest): Promise<GeneratedAsset> {
    try {
      const { prompt, negativePrompt } = generatePrompt(
        request.category,
        request.variant,
        request.customPrompt
      )
      const config: GenerationConfig = {
        ...defaultGenerationConfig,
        ...request.config,
        prompt,
        negativePrompt,
        width: request.size.width,
        height: request.size.height
      }
      logger.info(`Generating ${request.category} asset with variant ${request.variant}`)
      const rawBuffer = await this.sdService.generateImage(config)
      const postConfig: PostProcessingConfig = {
        ...defaultPostProcessingConfig,
        ...request.postProcess
      }
      const processedBuffer = await this.imageProcessor.process(rawBuffer, postConfig)
      const thumbnail = await this.imageProcessor.createThumbnail(processedBuffer)
      const metadata: AssetMetadata = {
        id: uuidv4(),
        category: request.category,
        variant: request.variant,
        tags: request.tags || [],
        dateCreated: new Date().toISOString(),
        prompt,
        size: request.size,
        format: postConfig.format || 'webp'
      }
      await this.assetCatalog.addAsset({
        ...metadata,
        path: `assets/${metadata.category}/${metadata.id}.${metadata.format}`,
        thumbnailPath: `assets/${metadata.category}/thumbnails/${metadata.id}.${metadata.format}`,
        version: 1,
        lastModified: metadata.dateCreated,
        usageCount: 0,
        relatedAssets: []
      })
      return {
        metadata,
        buffer: processedBuffer,
        thumbnail
      }
    } catch (error) {
      logger.error('Asset generation failed:', error)
      throw new Error(`Failed to generate ${request.category} asset: ${error.message}`)
    }
  }
  async generateBatch(
    requests: List[AssetRequest],
    concurrency = 3
  ): Promise<GeneratedAsset[]> {
    const results: List[GeneratedAsset] = []
    const chunks = this.chunkArray(requests, concurrency)
    for (const chunk of chunks) {
      const promises = chunk.map(request => this.generateAsset(request))
      const chunkResults = await Promise.all(promises)
      results.push(...chunkResults)
    }
    return results
  }
  private chunkArray<T>(array: List[T], size: float): T[][] {
    const chunks: List[T][] = []
    for (let i = 0; i < array.length; i += size) {
      chunks.push(array.slice(i, i + size))
    }
    return chunks
  }
} 