from typing import Any, List, Union


AssetCategory = Union[, 'parchment', 'border', 'corner', 'icon', 'decoration', 'texture', 'seal', 'ink']
AssetVariant = Union[, 'aged', 'pristine', 'weathered', 'elaborate', 'standard', 'minimal']
class AssetMetadata:
    id: str
    category: AssetCategory
    variant: AssetVariant
    tags: List[str]
    dateCreated: str
    prompt: str
    size: Size
    format: Union['png', 'webp']
    thumbnail?: str
class GenerationConfig:
    model: str
    prompt: str
    negativePrompt?: str
    steps: float
    cfg: float
    seed?: float
    width: float
    height: float
    batchSize?: float
class PostProcessingConfig:
    resize?: Size
    format?: Union['png', 'webp']
    quality?: float
    removeBg?: bool
    adjustments?: {
    brightness?: float
    contrast?: float
    saturation?: float
    sepia?: float
}
class AssetRequest:
    category: AssetCategory
    variant: AssetVariant
    tags?: List[str]
    size: Size
    customPrompt?: str
    config?: Partial[GenerationConfig]
    postProcess?: \'PostProcessingConfig\'
class GeneratedAsset:
    metadata: \'AssetMetadata\'
    buffer: Buffer
    thumbnail?: Buffer
class AssetCatalogEntry:
    path: str
    thumbnailPath?: str
    version: float
    lastModified: str
    usageCount: float
    relatedAssets: List[str] 