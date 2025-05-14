import { IAnimationLayer } from './LayerManager';
import { Sprite } from '../../services/SpriteManager';

export class RegionWorldLayer implements IAnimationLayer {
  id: string;
  visible: boolean = true;
  private sprites: Sprite[];

  constructor(id: string, sprites: Sprite[]) {
    this.id = id;
    this.sprites = sprites;
  }

  update(dt: number): void {
    // Update logic for region/world layer (e.g., animate tiles)
  }

  render(ctx: CanvasRenderingContext2D, camera: any): void {
    // Render all sprites in the region/world layer
    for (const sprite of this.sprites) {
      ctx.drawImage(sprite.image, 0, 0, sprite.width, sprite.height);
    }
  }

  setVisibility(visible: boolean): void {
    this.visible = visible;
  }
} 