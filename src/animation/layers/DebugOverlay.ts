import { IAnimationLayer } from './LayerManager';

interface DebugOverlayOptions {
  showLayerBounds?: boolean;
  showSpriteHitboxes?: boolean;
  layerColors?: Record<string, string>;
}

export function renderDebugOverlay(
  ctx: CanvasRenderingContext2D,
  layers: IAnimationLayer[],
  options: DebugOverlayOptions = {}
) {
  for (const layer of layers) {
    if (options.showLayerBounds) {
      ctx.save();
      ctx.strokeStyle = options.layerColors?.[layer.id] || 'magenta';
      ctx.lineWidth = 2;
      ctx.strokeRect(0, 0, ctx.canvas.width, ctx.canvas.height);
      ctx.restore();
    }
    // Optionally, add sprite hitbox rendering if layer exposes sprite info
    if (options.showSpriteHitboxes && (layer as any).sprites) {
      ctx.save();
      ctx.strokeStyle = 'red';
      ctx.lineWidth = 1;
      for (const sprite of (layer as any).sprites) {
        ctx.strokeRect(0, 0, sprite.width, sprite.height);
      }
      ctx.restore();
    }
  }
} 