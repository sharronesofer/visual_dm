import { Sprite } from '../../services/SpriteManager';

export interface IAnimationLayer {
  id: string;
  visible: boolean;
  update(dt: number): void;
  render(ctx: CanvasRenderingContext2D, camera: any): void;
  setVisibility(visible: boolean): void;
}

export class LayerManager {
  private layers: Map<string, IAnimationLayer> = new Map();
  private zOrder: string[] = [];

  addLayer(layer: IAnimationLayer) {
    this.layers.set(layer.id, layer);
    this.zOrder.push(layer.id);
  }

  removeLayer(id: string) {
    this.layers.delete(id);
    this.zOrder = this.zOrder.filter(lid => lid !== id);
  }

  setLayerVisibility(id: string, visible: boolean) {
    const layer = this.layers.get(id);
    if (layer) layer.setVisibility(visible);
  }

  update(dt: number) {
    for (const id of this.zOrder) {
      const layer = this.layers.get(id);
      if (layer && layer.visible) layer.update(dt);
    }
  }

  render(ctx: CanvasRenderingContext2D, camera: any) {
    for (const id of this.zOrder) {
      const layer = this.layers.get(id);
      if (layer && layer.visible) layer.render(ctx, camera);
    }
  }

  getLayer(id: string): IAnimationLayer | undefined {
    return this.layers.get(id);
  }

  setZOrder(order: string[]) {
    this.zOrder = order.filter(id => this.layers.has(id));
  }

  getZOrder(): string[] {
    return [...this.zOrder];
  }
} 