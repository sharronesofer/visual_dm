from typing import Any, Dict


class MapRenderer {
  private canvas: HTMLCanvasElement
  private ctx: CanvasRenderingContext2D
  private tileManager: TileManager
  private lightingSystem: LightingSystem
  private fogOfWar: FogOfWarManager
  private interactionHandler: MapInteractionHandler
  private textureCache: Map<string, HTMLImageElement> = new Map()
  private isInitialized: bool = false
  private viewport: Viewport = {
    position: Dict[str, Any],
    size: Dict[str, Any],
    zoom: 1,
    rotation: 0
  }
  private renderOptions: RenderOptions = {
    showGrid: true,
    showFogOfWar: true,
    showLighting: true,
    showObjects: true,
    levelOfDetail: 1
  }
  constructor(
    private mapData: MapData,
    private tileSize: float = 32
  ) {
    this.canvas = document.createElement('canvas')
    const context = this.canvas.getContext('2d')
    if (!context) {
      throw new Error('Failed to get 2D rendering context')
    }
    this.ctx = context
    this.tileManager = new TileManager(mapData)
    this.lightingSystem = new LightingSystem()
    this.fogOfWar = new FogOfWarManager(mapData)
    this.interactionHandler = new MapInteractionHandler(
      this.canvas,
      this.viewport,
      this.getTileAt.bind(this),
      this.getObjectAt.bind(this)
    )
  }
  public async initialize(container: HTMLElement): Promise<void> {
    if (this.isInitialized) {
      return
    }
    container.appendChild(this.canvas)
    this.resizeCanvas(container)
    await this.loadTextures()
    window.addEventListener('resize', () => this.resizeCanvas(container))
    this.isInitialized = true
  }
  private resizeCanvas(container: HTMLElement): void {
    this.canvas.width = container.clientWidth
    this.canvas.height = container.clientHeight
    this.viewport.size = {
      width: this.canvas.width,
      height: this.canvas.height
    }
  }
  private async loadTextures(): Promise<void> {
    const textureUrls = {
      grass: '/assets/textures/grass.png',
      forest: '/assets/textures/forest.png',
      mountain: '/assets/textures/mountain.png',
      water: '/assets/textures/water.png',
      urban: '/assets/textures/urban.png'
    }
    const loadPromises = Object.entries(textureUrls).map(([key, url]) => {
      return new Promise<void>((resolve, reject) => {
        const img = new Image()
        img.onload = () => {
          this.textureCache.set(key, img)
          resolve()
        }
        img.onerror = () => reject(new Error(`Failed to load texture: ${url}`))
        img.src = url
      })
    })
    await Promise.all(loadPromises)
  }
  private getTileAt(x: float, y: float): Tile | null {
    return this.tileManager.loadTile(Math.floor(x), Math.floor(y))
  }
  private getObjectAt(x: float, y: float): MapObject | null {
    const objects = this.mapData.objects.filter(obj => {
      const inX = x >= obj.position.x && x < obj.position.x + obj.size.width
      const inY = y >= obj.position.y && y < obj.position.y + obj.size.height
      return inX && inY
    })
    return objects.length > 0 ? objects[0] : null
  }
  private worldToScreen(worldX: float, worldY: float): Point {
    const x = (worldX - this.viewport.position.x) * this.viewport.zoom
    const y = (worldY - this.viewport.position.y) * this.viewport.zoom
    return { x, y }
  }
  private renderTile(tile: Tile): void {
    const screenPos = this.worldToScreen(tile.position.x, tile.position.y)
    const size = this.tileSize * this.viewport.zoom
    if (screenPos.x + size < 0 || screenPos.x > this.viewport.size.width ||
        screenPos.y + size < 0 || screenPos.y > this.viewport.size.height) {
      return
    }
    const { visible, explored } = this.fogOfWar.getTileVisibility(tile)
    if (!explored && this.renderOptions.showFogOfWar) {
      return
    }
    const texture = this.textureCache.get(tile.type)
    if (texture) {
      this.ctx.save()
      if (this.renderOptions.showLighting) {
        const lighting = this.lightingSystem.calculateTileLighting(tile)
        this.ctx.globalAlpha = lighting
      }
      this.ctx.drawImage(texture, screenPos.x, screenPos.y, size, size)
      if (this.renderOptions.showFogOfWar && !visible) {
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.5)'
        this.ctx.fillRect(screenPos.x, screenPos.y, size, size)
      }
      if (this.renderOptions.showGrid) {
        this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)'
        this.ctx.strokeRect(screenPos.x, screenPos.y, size, size)
      }
      this.ctx.restore()
    }
  }
  private renderObject(object: MapObject): void {
    if (!this.renderOptions.showObjects) {
      return
    }
    const screenPos = this.worldToScreen(object.position.x, object.position.y)
    const width = object.size.width * this.tileSize * this.viewport.zoom
    const height = object.size.height * this.tileSize * this.viewport.zoom
    if (screenPos.x + width < 0 || screenPos.x > this.viewport.size.width ||
        screenPos.y + height < 0 || screenPos.y > this.viewport.size.height) {
      return
    }
    this.ctx.fillStyle = 'rgba(255, 0, 0, 0.5)'
    this.ctx.fillRect(screenPos.x, screenPos.y, width, height)
  }
  public render(): void {
    if (!this.isInitialized) {
      return
    }
    this.ctx.clearRect(0, 0, this.viewport.size.width, this.viewport.size.height)
    const visibleTiles = this.tileManager.getTilesInViewport(
      this.viewport.position,
      {
        width: this.viewport.size.width / (this.tileSize * this.viewport.zoom),
        height: this.viewport.size.height / (this.tileSize * this.viewport.zoom)
      }
    )
    for (const tile of visibleTiles) {
      this.renderTile(tile)
    }
    if (this.renderOptions.showObjects) {
      for (const object of this.mapData.objects) {
        this.renderObject(object)
      }
    }
    this.tileManager.unloadTilesOutsideViewport(
      this.viewport.position,
      {
        width: this.viewport.size.width / (this.tileSize * this.viewport.zoom),
        height: this.viewport.size.height / (this.tileSize * this.viewport.zoom)
      }
    )
  }
  public setViewport(viewport: Partial<Viewport>): void {
    Object.assign(this.viewport, viewport)
    this.render()
  }
  public setRenderOptions(options: Partial<RenderOptions>): void {
    Object.assign(this.renderOptions, options)
    this.render()
  }
  public addInteractionListener(listener: MapEventListener): void {
    this.interactionHandler.addListener(listener)
  }
  public removeInteractionListener(listener: MapEventListener): void {
    this.interactionHandler.removeListener(listener)
  }
  public dispose(): void {
    this.interactionHandler.dispose()
    window.removeEventListener('resize', () => this.resizeCanvas(this.canvas.parentElement!))
    this.canvas.remove()
    this.tileManager.clear()
    this.lightingSystem.clear()
    this.fogOfWar.clear()
    this.textureCache.clear()
  }
} 