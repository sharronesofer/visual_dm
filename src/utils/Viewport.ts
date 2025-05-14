/**
 * Viewport class for managing visible map boundaries and culling operations.
 * Stores the visible rectangle in world coordinates and provides methods for updating and querying the viewport.
 */
export class Viewport {
  private _minX!: number;
  private _minY!: number;
  private _maxX!: number;
  private _maxY!: number;
  private _center: [number, number];
  private _zoom: number;
  private _width: number;
  private _height: number;

  constructor(center: [number, number], width: number, height: number, zoom: number) {
    this._center = center;
    this._width = width;
    this._height = height;
    this._zoom = zoom;
    this.updateBounds();
  }

  /**
   * Recalculate the viewport boundaries based on center, size, and zoom.
   */
  updateBounds(): void {
    const scale = Math.pow(2, this._zoom);
    const halfWorldWidth = this._width / (2 * scale);
    const halfWorldHeight = this._height / (2 * scale);
    this._minX = this._center[0] - halfWorldWidth;
    this._maxX = this._center[0] + halfWorldWidth;
    this._minY = this._center[1] - halfWorldHeight;
    this._maxY = this._center[1] + halfWorldHeight;
  }

  /**
   * Set the center of the viewport and update bounds.
   */
  setCenter(center: [number, number]): void {
    this._center = center;
    this.updateBounds();
  }

  /**
   * Set the zoom level and update bounds.
   */
  setZoom(zoom: number): void {
    this._zoom = zoom;
    this.updateBounds();
  }

  /**
   * Set the viewport size and update bounds.
   */
  setSize(width: number, height: number): void {
    this._width = width;
    this._height = height;
    this.updateBounds();
  }

  /**
   * Check if a point is within the viewport.
   */
  containsPoint(point: [number, number]): boolean {
    const [x, y] = point;
    return x >= this._minX && x <= this._maxX && y >= this._minY && y <= this._maxY;
  }

  /**
   * Check if a rectangle intersects with the viewport.
   */
  intersectsRect(rect: { minX: number; minY: number; maxX: number; maxY: number }): boolean {
    return !(
      rect.maxX < this._minX ||
      rect.minX > this._maxX ||
      rect.maxY < this._minY ||
      rect.minY > this._maxY
    );
  }

  /**
   * Expand the viewport by a buffer factor and return a new Viewport instance.
   */
  expandByBuffer(bufferFactor: number = 0.5): Viewport {
    const widthBuffer = (this._maxX - this._minX) * bufferFactor;
    const heightBuffer = (this._maxY - this._minY) * bufferFactor;
    const bufferedViewport = new Viewport(this._center, this._width, this._height, this._zoom);
    bufferedViewport._minX = this._minX - widthBuffer;
    bufferedViewport._maxX = this._maxX + widthBuffer;
    bufferedViewport._minY = this._minY - heightBuffer;
    bufferedViewport._maxY = this._maxY + heightBuffer;
    return bufferedViewport;
  }

  // Getters for boundaries and properties
  get minX() {
    return this._minX;
  }
  get minY() {
    return this._minY;
  }
  get maxX() {
    return this._maxX;
  }
  get maxY() {
    return this._maxY;
  }
  get center() {
    return this._center;
  }
  get zoom() {
    return this._zoom;
  }
  get width() {
    return this._width;
  }
  get height() {
    return this._height;
  }
}
