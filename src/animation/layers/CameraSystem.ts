export interface CameraState {
  x: number;
  y: number;
  zoom: number;
}

export class CameraSystem {
  private state: CameraState;
  private targetState: CameraState | null = null;
  private transitionDuration: number = 0;
  private transitionElapsed: number = 0;

  constructor(initial: CameraState = { x: 0, y: 0, zoom: 1 }) {
    this.state = { ...initial };
  }

  getState(): CameraState {
    return { ...this.state };
  }

  setState(newState: CameraState) {
    this.state = { ...newState };
    this.targetState = null;
    this.transitionDuration = 0;
    this.transitionElapsed = 0;
  }

  pan(dx: number, dy: number) {
    this.state.x += dx;
    this.state.y += dy;
  }

  zoomTo(zoom: number) {
    this.state.zoom = zoom;
  }

  transitionTo(target: CameraState, duration: number) {
    this.targetState = { ...target };
    this.transitionDuration = duration;
    this.transitionElapsed = 0;
  }

  update(dt: number) {
    if (this.targetState && this.transitionDuration > 0) {
      this.transitionElapsed += dt;
      const t = Math.min(this.transitionElapsed / this.transitionDuration, 1);
      this.state.x = this.state.x + (this.targetState.x - this.state.x) * t;
      this.state.y = this.state.y + (this.targetState.y - this.state.y) * t;
      this.state.zoom = this.state.zoom + (this.targetState.zoom - this.state.zoom) * t;
      if (t >= 1) {
        this.state = { ...this.targetState };
        this.targetState = null;
        this.transitionDuration = 0;
        this.transitionElapsed = 0;
      }
    }
  }

  // Hook for layer-specific camera logic
  applyLayerTransform(ctx: CanvasRenderingContext2D) {
    ctx.setTransform(this.state.zoom, 0, 0, this.state.zoom, -this.state.x, -this.state.y);
  }
} 