import { Point, MapInteractionEvent, MapObject, Tile, Viewport } from './types';

export class MapInteractionHandler {
  private listeners: Set<(event: MapInteractionEvent) => void> = new Set();
  private isDragging: boolean = false;
  private dragStart: Point | null = null;
  private lastMousePosition: Point | null = null;
  private selectedObject: MapObject | null = null;
  private hoveredTile: Tile | null = null;

  constructor(
    private canvas: HTMLCanvasElement,
    private viewport: Viewport,
    private getTileAt: (x: number, y: number) => Tile | null,
    private getObjectAt: (x: number, y: number) => MapObject | null
  ) {
    this.setupEventListeners();
  }

  private setupEventListeners(): void {
    this.canvas.addEventListener('mousedown', this.handleMouseDown.bind(this));
    this.canvas.addEventListener('mousemove', this.handleMouseMove.bind(this));
    this.canvas.addEventListener('mouseup', this.handleMouseUp.bind(this));
    this.canvas.addEventListener('wheel', this.handleWheel.bind(this));
    this.canvas.addEventListener('contextmenu', (e) => e.preventDefault());
  }

  private screenToWorld(screenX: number, screenY: number): Point {
    const rect = this.canvas.getBoundingClientRect();
    const x = (screenX - rect.left) / this.viewport.zoom + this.viewport.position.x;
    const y = (screenY - rect.top) / this.viewport.zoom + this.viewport.position.y;
    return { x, y };
  }

  private handleMouseDown(event: MouseEvent): void {
    event.preventDefault();
    const worldPos = this.screenToWorld(event.clientX, event.clientY);
    this.lastMousePosition = worldPos;

    if (event.button === 2) { // Right click
      this.isDragging = true;
      this.dragStart = worldPos;
    } else if (event.button === 0) { // Left click
      const tile = this.getTileAt(worldPos.x, worldPos.y);
      const object = this.getObjectAt(worldPos.x, worldPos.y);

      if (object) {
        this.selectedObject = object;
        this.notifyListeners({
          type: 'click',
          position: worldPos,
          tile: tile || undefined,
          object
        });
      } else if (tile) {
        this.selectedObject = null;
        this.notifyListeners({
          type: 'click',
          position: worldPos,
          tile
        });
      }
    }
  }

  private handleMouseMove(event: MouseEvent): void {
    event.preventDefault();
    const worldPos = this.screenToWorld(event.clientX, event.clientY);

    if (this.isDragging && this.lastMousePosition) {
      const dx = worldPos.x - this.lastMousePosition.x;
      const dy = worldPos.y - this.lastMousePosition.y;

      this.viewport.position.x -= dx;
      this.viewport.position.y -= dy;

      this.notifyListeners({
        type: 'drag',
        position: worldPos
      });
    } else {
      const tile = this.getTileAt(worldPos.x, worldPos.y);
      const object = this.getObjectAt(worldPos.x, worldPos.y);

      if (tile !== this.hoveredTile || object !== this.selectedObject) {
        this.hoveredTile = tile || null;
        this.notifyListeners({
          type: 'hover',
          position: worldPos,
          tile: tile || undefined,
          object: object || undefined
        });
      }
    }

    this.lastMousePosition = worldPos;
  }

  private handleMouseUp(event: MouseEvent): void {
    event.preventDefault();
    if (event.button === 2) {
      this.isDragging = false;
      this.dragStart = null;
    }
  }

  private handleWheel(event: WheelEvent): void {
    event.preventDefault();
    const zoomFactor = 1 - event.deltaY * 0.001;
    const worldPos = this.screenToWorld(event.clientX, event.clientY);

    // Calculate new zoom
    const newZoom = Math.max(0.1, Math.min(10, this.viewport.zoom * zoomFactor));
    const zoomChange = newZoom / this.viewport.zoom;

    // Adjust position to zoom toward cursor
    this.viewport.position.x += (worldPos.x - this.viewport.position.x) * (1 - zoomChange);
    this.viewport.position.y += (worldPos.y - this.viewport.position.y) * (1 - zoomChange);
    this.viewport.zoom = newZoom;

    this.notifyListeners({
      type: 'drag',
      position: worldPos
    });
  }

  public addListener(listener: (event: MapInteractionEvent) => void): void {
    this.listeners.add(listener);
  }

  public removeListener(listener: (event: MapInteractionEvent) => void): void {
    this.listeners.delete(listener);
  }

  private notifyListeners(event: MapInteractionEvent): void {
    for (const listener of this.listeners) {
      listener(event);
    }
  }

  public getSelectedObject(): MapObject | null {
    return this.selectedObject;
  }

  public getHoveredTile(): Tile | null {
    return this.hoveredTile;
  }

  public isDraggingMap(): boolean {
    return this.isDragging;
  }

  public dispose(): void {
    this.canvas.removeEventListener('mousedown', this.handleMouseDown.bind(this));
    this.canvas.removeEventListener('mousemove', this.handleMouseMove.bind(this));
    this.canvas.removeEventListener('mouseup', this.handleMouseUp.bind(this));
    this.canvas.removeEventListener('wheel', this.handleWheel.bind(this));
    this.listeners.clear();
  }
} 