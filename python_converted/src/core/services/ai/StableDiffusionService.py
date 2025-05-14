from typing import Any, Dict


class StableDiffusionService {
  private apiKey: str
  private baseUrl: str
  private defaultModel: str
  constructor(
    apiKey: str,
    baseUrl = 'https:
    defaultModel = 'stable-diffusion-xl-1024-v1-0'
  ) {
    this.apiKey = apiKey
    this.baseUrl = baseUrl
    this.defaultModel = defaultModel
  }
  async generateImage(config: GenerationConfig): Promise<Buffer> {
    try {
      const response = await fetch(`${this.baseUrl}/${config.model || this.defaultModel}/text-to-image`, {
        method: 'POST',
        headers: Dict[str, Any]`
        },
        body: JSON.stringify({
          text_prompts: [
            {
              text: config.prompt,
              weight: 1
            },
            {
              text: config.negativePrompt,
              weight: -1
            }
          ],
          cfg_scale: config.cfg,
          height: config.height,
          width: config.width,
          steps: config.steps,
          samples: config.batchSize,
          seed: config.seed
        })
      })
      if (!response.ok) {
        const error = await response.json()
        throw new Error(`Stable Diffusion API error: ${error.message}`)
      }
      const result = await response.json()
      const base64Image = result.artifacts[0].base64
      return Buffer.from(base64Image, 'base64')
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Image generation failed: ${error.message}`)
      }
      throw new Error('Image generation failed with unknown error')
    }
  }
} 