from typing import Any, Dict, List


const sdService = new StableDiffusionService(process.env.STABILITY_API_KEY || '')
const imageProcessor = new ImageProcessor()
const assetCatalog = new AssetCatalog()
const generator = new AssetGenerator(sdService, imageProcessor, assetCatalog)
async function generateAnimationTextures() {
  const textures: List[AssetRequest] = [
    {
      category: 'texture',
      variant: 'aged',
      tags: ['dust', 'particles', 'animation'],
      size: Dict[str, Any],
      customPrompt: 'floating dust particles, atmospheric particles, black background, seamless texture',
      postProcess: Dict[str, Any]
    },
    {
      category: 'texture',
      variant: 'pristine',
      tags: ['parchment', 'normal-map', 'animation'],
      size: Dict[str, Any],
      customPrompt: 'parchment paper normal map, height map, seamless texture, grayscale',
      postProcess: Dict[str, Any]
      }
    },
    {
      category: 'texture',
      variant: 'weathered',
      tags: ['ink', 'drips', 'animation'],
      size: Dict[str, Any],
      customPrompt: 'black ink drips, liquid dripping effect, transparent background',
      postProcess: Dict[str, Any]
    }
  ]
  try {
    console.log('Initializing asset catalog...')
    await assetCatalog.initialize()
    console.log('Generating animation textures...')
    const assets = await generator.generateBatch(textures)
    for (const asset of assets) {
      const fileName = asset.metadata.tags[0]
      const outputPath = path.join(process.cwd(), 'public/assets/textures', `${fileName}.png`)
      await fs.mkdir(path.dirname(outputPath), { recursive: true })
      await fs.writeFile(outputPath, asset.buffer)
      console.log(`Generated texture: ${fileName}.png`)
    }
    console.log('All textures generated successfully!')
  } catch (error) {
    console.error('Failed to generate textures:', error)
    process.exit(1)
  }
}
generateAnimationTextures().catch(console.error) 