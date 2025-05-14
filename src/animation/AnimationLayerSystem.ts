import { LayerManager } from './layers/LayerManager';
import { RegionWorldLayer } from './layers/RegionWorldLayer';
import { POIBuildingLayer } from './layers/POIBuildingLayer';
import { CameraSystem } from './layers/CameraSystem';
import { renderDebugOverlay } from './layers/DebugOverlay';
import { SpriteManager } from '../services/SpriteManager';

// Placeholder: create or get a <canvas> element
const canvas = document.getElementById('animation-canvas') as HTMLCanvasElement || document.createElement('canvas');
canvas.width = 800;
canvas.height = 600;
if (!canvas.parentElement) document.body.appendChild(canvas);
const ctx = canvas.getContext('2d')!;

const layerManager = new LayerManager();
const cameraSystem = new CameraSystem();
const spriteManager = SpriteManager.getInstance();

// Placeholder sprites (mocked for now)
const placeholderSprite = {
  image: new window.Image(),
  width: 64,
  height: 64,
  src: ''
};
const worldSprites = [placeholderSprite];
const buildingSprites = [placeholderSprite];

const regionLayer = new RegionWorldLayer('region', worldSprites);
const poiLayer = new POIBuildingLayer('poi', buildingSprites);
layerManager.addLayer(regionLayer);
layerManager.addLayer(poiLayer);
layerManager.setZOrder(['region', 'poi']);

let debugEnabled = true;

function mainRenderLoop(dt: number) {
  cameraSystem.update(dt);
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  // Render each layer with camera transform
  for (const id of layerManager.getZOrder()) {
    const layer = layerManager.getLayer(id);
    if (layer && layer.visible) {
      ctx.save();
      cameraSystem.applyLayerTransform(ctx);
      layer.update(dt);
      layer.render(ctx, cameraSystem.getState());
      ctx.restore();
    }
  }
  if (debugEnabled) {
    renderDebugOverlay(ctx, [regionLayer, poiLayer], { showLayerBounds: true, showSpriteHitboxes: true });
  }
  requestAnimationFrame(mainRenderLoop);
}

requestAnimationFrame(mainRenderLoop);

// Export for integration
export { layerManager, cameraSystem, regionLayer, poiLayer }; 