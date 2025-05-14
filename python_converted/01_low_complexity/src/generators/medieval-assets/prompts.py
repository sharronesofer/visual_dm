from typing import Any, Dict



const basePrompt = {
  parchment: 'medieval parchment texture, aged paper, historical manuscript, detailed fiber texture',
  border: 'medieval manuscript border, illuminated manuscript decoration, ornate frame, celtic knots',
  corner: 'medieval manuscript corner decoration, illuminated corner piece, ornate flourishes',
  icon: 'medieval manuscript icon, illuminated miniature, historical illustration',
  decoration: 'medieval manuscript decoration, illuminated ornament, historical embellishment',
  texture: 'medieval material texture, historical surface pattern, aged material',
  seal: 'medieval wax seal, royal stamp, historical seal impression',
  ink: 'medieval ink texture, calligraphy ink splash, historical writing fluid'
}
const variantModifiers = {
  aged: ', heavily aged, worn, antiqued, time-worn texture, historical patina',
  pristine: ', well-preserved, clean, fresh appearance, vibrant details',
  weathered: ', naturally aged, subtle wear, authentic aging, gentle patina',
  elaborate: ', highly detailed, ornate, complex design, intricate patterns',
  standard: ', balanced detail, traditional style, classic design',
  minimal: ', simple design, clean lines, subtle details'
}
const negativePrompts = {
  base: 'modern, digital, contemporary, plastic, synthetic, computer-generated, lorem ipsum text',
  parchment: 'lined paper, notebook, printed text, modern watermark',
  border: 'modern frames, digital borders, clip art, cartoon style',
  corner: 'modern corners, sharp edges, geometric patterns',
  icon: 'emoji, modern icons, pixel art, digital symbols',
  decoration: 'modern ornaments, digital decorations, clip art style',
  texture: 'modern patterns, digital textures, repeating patterns',
  seal: 'modern stamps, rubber stamps, digital seals',
  ink: 'printer ink, modern markers, digital effects'
}
const styleGuide = {
  parchment: Dict[str, Any],
  border: Dict[str, Any],
  seal: Dict[str, Any]
}
function generatePrompt(
  category: AssetCategory,
  variant: AssetVariant,
  customPrompt?: str
): { prompt: str; negativePrompt: str } {
  const baseText = basePrompt[category]
  const variantText = variantModifiers[variant]
  const specificNegative = negativePrompts[category]
  const prompt = customPrompt 
    ? `${baseText}, ${customPrompt}${variantText}`
    : `${baseText}${variantText}`
  const negativePrompt = `${negativePrompts.base}, ${specificNegative}`
  return { prompt, negativePrompt }
}
const defaultGenerationConfig = {
  steps: 30,
  cfg: 7.5,
  width: 512,
  height: 512,
  batchSize: 1
}
const defaultPostProcessingConfig = {
  format: 'webp' as const,
  quality: 90,
  removeBg: false,
  adjustments: Dict[str, Any]
} 