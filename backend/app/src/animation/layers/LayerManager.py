from typing import Any, List


class IAnimationLayer:
    id: str
    visible: bool
    update(dt: float): None
    render(ctx: CanvasRenderingContext2D, camera: Any): None
    setVisibility(visible: bool): None
class LayerManager {
  private layers: Map<string, IAnimationLayer> = new Map()
  private zOrder: List[string] = []
  addLayer(layer: IAnimationLayer) {
    this.layers.set(layer.id, layer)
    this.zOrder.push(layer.id)
  }
  removeLayer(id: str) {
    this.layers.delete(id)
    this.zOrder = this.zOrder.filter(lid => lid !== id)
  }
  setLayerVisibility(id: str, visible: bool) {
    const layer = this.layers.get(id)
    if (layer) layer.setVisibility(visible)
  }
  update(dt: float) {
    for (const id of this.zOrder) {
      const layer = this.layers.get(id)
      if (layer && layer.visible) layer.update(dt)
    }
  }
  render(ctx: CanvasRenderingContext2D, camera: Any) {
    for (const id of this.zOrder) {
      const layer = this.layers.get(id)
      if (layer && layer.visible) layer.render(ctx, camera)
    }
  }
  getLayer(id: str): \'IAnimationLayer\' | undefined {
    return this.layers.get(id)
  }
  setZOrder(order: List[string]) {
    this.zOrder = order.filter(id => this.layers.has(id))
  }
  getZOrder(): string[] {
    return [...this.zOrder]
  }
} 