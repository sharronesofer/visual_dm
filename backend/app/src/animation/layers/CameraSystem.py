from typing import Any


class CameraState:
    x: float
    y: float
    zoom: float
class CameraSystem {
  private state: \'CameraState\'
  private targetState: \'CameraState\' | null = null
  private transitionDuration: float = 0
  private transitionElapsed: float = 0
  constructor(initial: \'CameraState\' = { x: 0, y: 0, zoom: 1 }) {
    this.state = { ...initial }
  }
  getState(): \'CameraState\' {
    return { ...this.state }
  }
  setState(newState: CameraState) {
    this.state = { ...newState }
    this.targetState = null
    this.transitionDuration = 0
    this.transitionElapsed = 0
  }
  pan(dx: float, dy: float) {
    this.state.x += dx
    this.state.y += dy
  }
  zoomTo(zoom: float) {
    this.state.zoom = zoom
  }
  transitionTo(target: \'CameraState\', duration: float) {
    this.targetState = { ...target }
    this.transitionDuration = duration
    this.transitionElapsed = 0
  }
  update(dt: float) {
    if (this.targetState && this.transitionDuration > 0) {
      this.transitionElapsed += dt
      const t = Math.min(this.transitionElapsed / this.transitionDuration, 1)
      this.state.x = this.state.x + (this.targetState.x - this.state.x) * t
      this.state.y = this.state.y + (this.targetState.y - this.state.y) * t
      this.state.zoom = this.state.zoom + (this.targetState.zoom - this.state.zoom) * t
      if (t >= 1) {
        this.state = { ...this.targetState }
        this.targetState = null
        this.transitionDuration = 0
        this.transitionElapsed = 0
      }
    }
  }
  applyLayerTransform(ctx: CanvasRenderingContext2D) {
    ctx.setTransform(this.state.zoom, 0, 0, this.state.zoom, -this.state.x, -this.state.y)
  }
} 