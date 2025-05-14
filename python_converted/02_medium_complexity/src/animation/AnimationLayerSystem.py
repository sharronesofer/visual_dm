from typing import Any



const canvas = document.getElementById('animation-canvas') as HTMLCanvasElement || document.createElement('canvas')
canvas.width = 800
canvas.height = 600
if (!canvas.parentElement) document.body.appendChild(canvas)
const ctx = canvas.getContext('2d')!
const layerManager = new LayerManager()
const cameraSystem = new CameraSystem()
const spriteManager = SpriteManager.getInstance()
const placeholderSprite = {
  image: new window.Image(),
  width: 64,
  height: 64,
  src: ''
}
const worldSprites = [placeholderSprite]
const buildingSprites = [placeholderSprite]
const regionLayer = new RegionWorldLayer('region', worldSprites)
const poiLayer = new POIBuildingLayer('poi', buildingSprites)
layerManager.addLayer(regionLayer)
layerManager.addLayer(poiLayer)
layerManager.setZOrder(['region', 'poi'])
let debugEnabled = true
function mainRenderLoop(dt: float) {
  cameraSystem.update(dt)
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  for (const id of layerManager.getZOrder()) {
    const layer = layerManager.getLayer(id)
    if (layer && layer.visible) {
      ctx.save()
      cameraSystem.applyLayerTransform(ctx)
      layer.update(dt)
      layer.render(ctx, cameraSystem.getState())
      ctx.restore()
    }
  }
  if (debugEnabled) {
    renderDebugOverlay(ctx, [regionLayer, poiLayer], { showLayerBounds: true, showSpriteHitboxes: true })
  }
  requestAnimationFrame(mainRenderLoop)
}
requestAnimationFrame(mainRenderLoop)
{ layerManager, cameraSystem, regionLayer, poiLayer } 