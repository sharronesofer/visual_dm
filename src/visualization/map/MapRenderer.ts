import { Point, Size, Viewport, MapData, Tile, MapObject, RenderOptions, MapInteractionEvent, MapEventListener } from './types';
import { TileManager } from './TileManager';
import { LightingSystem } from './LightingSystem';
import { FogOfWarManager } from './FogOfWarManager';
import { MapInteractionHandler } from './MapInteractionHandler';
import { marketToMapObject } from './types';

export class MapRenderer {
  private canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D;
  private tileManager: TileManager;
  private lightingSystem: LightingSystem;
  private fogOfWar: FogOfWarManager;
  private interactionHandler: MapInteractionHandler;
  private textureCache: Map<string, HTMLImageElement> = new Map();
  private isInitialized: boolean = false;

  private viewport: Viewport = {
    position: { x: 0, y: 0 },
    size: { width: 0, height: 0 },
    zoom: 1,
    rotation: 0
  };

  private renderOptions: RenderOptions = {
    showGrid: true,
    showFogOfWar: true,
    showLighting: true,
    showObjects: true,
    levelOfDetail: 1
  };

  constructor(
    private mapData: MapData,
    private tileSize: number = 32
  ) {
    this.canvas = document.createElement('canvas');
    const context = this.canvas.getContext('2d');
    if (!context) {
      throw new Error('Failed to get 2D rendering context');
    }
    this.ctx = context;

    this.tileManager = new TileManager(mapData);
    this.lightingSystem = new LightingSystem();
    this.fogOfWar = new FogOfWarManager(mapData);
    this.interactionHandler = new MapInteractionHandler(
      this.canvas,
      this.viewport,
      this.getTileAt.bind(this),
      this.getObjectAt.bind(this)
    );
  }

  public async initialize(container: HTMLElement): Promise<void> {
    if (this.isInitialized) {
      return;
    }

    container.appendChild(this.canvas);
    this.resizeCanvas(container);
    await this.loadTextures();

    window.addEventListener('resize', () => this.resizeCanvas(container));
    this.isInitialized = true;
  }

  private resizeCanvas(container: HTMLElement): void {
    this.canvas.width = container.clientWidth;
    this.canvas.height = container.clientHeight;
    this.viewport.size = {
      width: this.canvas.width,
      height: this.canvas.height
    };
  }

  private async loadTextures(): Promise<void> {
    const textureUrls = {
      grass: '/assets/textures/grass.png',
      forest: '/assets/textures/forest.png',
      mountain: '/assets/textures/mountain.png',
      water: '/assets/textures/water.png',
      urban: '/assets/textures/urban.png'
    };

    const loadPromises = Object.entries(textureUrls).map(([key, url]) => {
      return new Promise<void>((resolve, reject) => {
        const img = new Image();
        img.onload = () => {
          this.textureCache.set(key, img);
          resolve();
        };
        img.onerror = () => reject(new Error(`Failed to load texture: ${url}`));
        img.src = url;
      });
    });

    await Promise.all(loadPromises);
  }

  private getTileAt(x: number, y: number): Tile | null {
    return this.tileManager.loadTile(Math.floor(x), Math.floor(y));
  }

  private getObjectAt(x: number, y: number): MapObject | null {
    const objects = this.mapData.objects.filter(obj => {
      const inX = x >= obj.position.x && x < obj.position.x + obj.size.width;
      const inY = y >= obj.position.y && y < obj.position.y + obj.size.height;
      return inX && inY;
    });

    return objects.length > 0 ? objects[0] : null;
  }

  private worldToScreen(worldX: number, worldY: number): Point {
    const x = (worldX - this.viewport.position.x) * this.viewport.zoom;
    const y = (worldY - this.viewport.position.y) * this.viewport.zoom;
    return { x, y };
  }

  private renderTile(tile: Tile): void {
    const screenPos = this.worldToScreen(tile.position.x, tile.position.y);
    const size = this.tileSize * this.viewport.zoom;

    // Skip rendering if tile is outside viewport
    if (screenPos.x + size < 0 || screenPos.x > this.viewport.size.width ||
      screenPos.y + size < 0 || screenPos.y > this.viewport.size.height) {
      return;
    }

    // Get tile visibility
    const { visible, explored } = this.fogOfWar.getTileVisibility(tile);
    if (!explored && this.renderOptions.showFogOfWar) {
      return;
    }

    // Draw tile texture
    const texture = this.textureCache.get(tile.type);
    if (texture) {
      this.ctx.save();

      // Apply lighting if enabled
      if (this.renderOptions.showLighting) {
        const lighting = this.lightingSystem.calculateTileLighting(tile);
        this.ctx.globalAlpha = lighting;
      }

      // Draw the base texture
      this.ctx.drawImage(texture, screenPos.x, screenPos.y, size, size);

      // Apply fog of war effect
      if (this.renderOptions.showFogOfWar && !visible) {
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
        this.ctx.fillRect(screenPos.x, screenPos.y, size, size);
      }

      // Draw grid if enabled
      if (this.renderOptions.showGrid) {
        this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
        this.ctx.strokeRect(screenPos.x, screenPos.y, size, size);
      }

      this.ctx.restore();
    }
  }

  private renderObject(object: MapObject): void {
    if (!this.renderOptions.showObjects) {
      return;
    }

    const screenPos = this.worldToScreen(object.position.x, object.position.y);
    const width = object.size.width * this.tileSize * this.viewport.zoom;
    const height = object.size.height * this.tileSize * this.viewport.zoom;

    // Skip rendering if object is outside viewport
    if (screenPos.x + width < 0 || screenPos.x > this.viewport.size.width ||
      screenPos.y + height < 0 || screenPos.y > this.viewport.size.height) {
      return;
    }

    if (object.type === 'market') {
      // Draw a distinct market marker (e.g., blue circle with icon)
      this.ctx.save();
      this.ctx.beginPath();
      this.ctx.arc(screenPos.x + width / 2, screenPos.y + height / 2, Math.max(width, height) / 2, 0, 2 * Math.PI);
      this.ctx.fillStyle = 'rgba(0, 120, 255, 0.7)';
      this.ctx.fill();
      this.ctx.strokeStyle = '#003366';
      this.ctx.lineWidth = 2;
      this.ctx.stroke();
      // Optionally draw a market icon or the first letter of the market name
      this.ctx.fillStyle = '#fff';
      this.ctx.font = `${Math.floor(height / 1.5)}px sans-serif`;
      this.ctx.textAlign = 'center';
      this.ctx.textBaseline = 'middle';
      this.ctx.fillText((object.data.name || 'M')[0], screenPos.x + width / 2, screenPos.y + height / 2);
      this.ctx.restore();
      return;
    }

    // Draw object placeholder (replace with actual object rendering)
    this.ctx.fillStyle = 'rgba(255, 0, 0, 0.5)';
    this.ctx.fillRect(screenPos.x, screenPos.y, width, height);
  }

  public render(): void {
    if (!this.isInitialized) {
      return;
    }

    // Clear canvas
    this.ctx.clearRect(0, 0, this.viewport.size.width, this.viewport.size.height);

    // Calculate visible area
    const visibleTiles = this.tileManager.getTilesInViewport(
      this.viewport.position,
      {
        width: this.viewport.size.width / (this.tileSize * this.viewport.zoom),
        height: this.viewport.size.height / (this.tileSize * this.viewport.zoom)
      }
    );

    // Render tiles
    for (const tile of visibleTiles) {
      this.renderTile(tile);
    }

    // Render objects
    if (this.renderOptions.showObjects) {
      for (const object of this.mapData.objects) {
        this.renderObject(object);
      }
    }

    // Clean up tiles outside viewport
    this.tileManager.unloadTilesOutsideViewport(
      this.viewport.position,
      {
        width: this.viewport.size.width / (this.tileSize * this.viewport.zoom),
        height: this.viewport.size.height / (this.tileSize * this.viewport.zoom)
      }
    );
  }

  public setViewport(viewport: Partial<Viewport>): void {
    Object.assign(this.viewport, viewport);
    this.render();
  }

  public setRenderOptions(options: Partial<RenderOptions>): void {
    Object.assign(this.renderOptions, options);
    this.render();
  }

  public addInteractionListener(listener: MapEventListener): void {
    this.interactionHandler.addListener(listener);
  }

  public removeInteractionListener(listener: MapEventListener): void {
    this.interactionHandler.removeListener(listener);
  }

  public dispose(): void {
    this.interactionHandler.dispose();
    window.removeEventListener('resize', () => this.resizeCanvas(this.canvas.parentElement!));
    this.canvas.remove();
    this.tileManager.clear();
    this.lightingSystem.clear();
    this.fogOfWar.clear();
    this.textureCache.clear();
  }

  public syncMarketMarkers(markets: any[]): void {
    // Remove existing market objects
    this.mapData.objects = this.mapData.objects.filter(obj => obj.type !== 'market');
    // Add new market objects
    for (const market of markets) {
      this.mapData.objects.push(marketToMapObject(market));
    }
    this.render();
  }

  public onMarketMarkerClick(callback: (marketObject: MapObject) => void): void {
    this.addInteractionListener(event => {
      if (event.type === 'click' && event.object && event.object.type === 'market') {
        callback(event.object);
      }
    });
  }
} 