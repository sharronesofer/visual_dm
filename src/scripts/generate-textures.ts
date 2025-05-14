import { AssetGenerator } from '../generators/medieval-assets/AssetGenerator';
import { StableDiffusionService } from '../services/ai/StableDiffusionService';
import { ImageProcessor } from '../services/image/ImageProcessor';
import { AssetCatalog } from '../generators/medieval-assets/AssetCatalog';
import { AssetRequest } from '../generators/medieval-assets/types';
import path from 'path';
import fs from 'fs/promises';

// Initialize services
const sdService = new StableDiffusionService(process.env.STABILITY_API_KEY || '');
const imageProcessor = new ImageProcessor();
const assetCatalog = new AssetCatalog();
const generator = new AssetGenerator(sdService, imageProcessor, assetCatalog);

async function generateAnimationTextures() {
  const textures: AssetRequest[] = [
    {
      category: 'texture',
      variant: 'aged',
      tags: ['dust', 'particles', 'animation'],
      size: { width: 512, height: 512 },
      customPrompt: 'floating dust particles, atmospheric particles, black background, seamless texture',
      postProcess: {
        removeBg: true,
        format: 'png',
        quality: 100
      }
    },
    {
      category: 'texture',
      variant: 'pristine',
      tags: ['parchment', 'normal-map', 'animation'],
      size: { width: 512, height: 512 },
      customPrompt: 'parchment paper normal map, height map, seamless texture, grayscale',
      postProcess: {
        format: 'png',
        quality: 100,
        adjustments: {
          contrast: 1.2
        }
      }
    },
    {
      category: 'texture',
      variant: 'weathered',
      tags: ['ink', 'drips', 'animation'],
      size: { width: 512, height: 128 },
      customPrompt: 'black ink drips, liquid dripping effect, transparent background',
      postProcess: {
        removeBg: true,
        format: 'png',
        quality: 100
      }
    }
  ];

  try {
    console.log('Initializing asset catalog...');
    await assetCatalog.initialize();

    console.log('Generating animation textures...');
    const assets = await generator.generateBatch(textures);

    // Save textures to the public assets directory
    for (const asset of assets) {
      const fileName = asset.metadata.tags[0];
      const outputPath = path.join(process.cwd(), 'public/assets/textures', `${fileName}.png`);
      
      // Ensure directory exists
      await fs.mkdir(path.dirname(outputPath), { recursive: true });
      
      // Save the texture
      await fs.writeFile(outputPath, asset.buffer);
      console.log(`Generated texture: ${fileName}.png`);
    }

    console.log('All textures generated successfully!');
  } catch (error) {
    console.error('Failed to generate textures:', error);
    process.exit(1);
  }
}

// Run the generation
generateAnimationTextures().catch(console.error); 