from typing import Any, Dict, List



class DebugOverlayOptions:
    showLayerBounds?: bool
    showSpriteHitboxes?: bool
    layerColors?: Dict[str, str>
function renderDebugOverlay(
  ctx: CanvasRenderingContext2D,
  layers: List[IAnimationLayer],
  options: \'DebugOverlayOptions\' = {}
) {
  for (const layer of layers) {
    if (options.showLayerBounds) {
      ctx.save()
      ctx.strokeStyle = options.layerColors?.[layer.id] || 'magenta'
      ctx.lineWidth = 2
      ctx.strokeRect(0, 0, ctx.canvas.width, ctx.canvas.height)
      ctx.restore()
    }
    if (options.showSpriteHitboxes && (layer as any).sprites) {
      ctx.save()
      ctx.strokeStyle = 'red'
      ctx.lineWidth = 1
      for (const sprite of (layer as any).sprites) {
        ctx.strokeRect(0, 0, sprite.width, sprite.height)
      }
      ctx.restore()
    }
  }
} 