from typing import Any, List



class POIBuildingLayer implements IAnimationLayer {
  id: str
  visible: bool = true
  private sprites: List[Sprite]
  constructor(id: str, sprites: List[Sprite]) {
    this.id = id
    this.sprites = sprites
  }
  update(dt: float): void {
  }
  render(ctx: CanvasRenderingContext2D, camera: Any): void {
    for (const sprite of this.sprites) {
      ctx.drawImage(sprite.image, 0, 0, sprite.width, sprite.height)
    }
  }
  setVisibility(visible: bool): void {
    this.visible = visible
  }
} 