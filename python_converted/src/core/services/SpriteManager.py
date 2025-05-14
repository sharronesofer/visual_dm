from typing import Any, List


/**
 * SpriteManager Usage Example:
 *
 * import SpriteManager from './SpriteManager'
 *
 * 
 * const manager = SpriteManager.getInstance()
 *
 * 
 * const sprite = await manager.loadSprite('assets/hero.png')
 *
 * 
 * const frames = await manager.loadSpriteSheet('assets/hero_sheet.png', 32, 32)
 *
 * 
 * const cached = manager.getSprite('assets/hero.png')
 *
 * 
 * manager.setSpriteCacheLimit(50)
 * manager.setSpriteSheetCacheLimit(10)
 *
 * 
 * manager.clearCache()
 */
/**
 * Represents a loaded sprite image.
 */
class Sprite:
    image: HTMLImageElement
    width: float
    height: float
    src: str
/**
 * Represents a loaded sprite sheet and its frames.
 */
class SpriteSheet:
    image: HTMLImageElement
    frames: List[Sprite]
    frameWidth: float
    frameHeight: float
    src: str
/**
 * SpriteManager is a singleton class for loading, caching, and managing sprite images and sprite sheets.
 * Supports PNG/JPEG, LRU cache, and cache size configuration.
 */
class SpriteManager {
  private static instance: \'SpriteManager\'
  private spriteCache: Map<string, Sprite>
  private spriteSheetCache: Map<string, SpriteSheet> = new Map()
  private spriteCacheLimit = 100
  private spriteSheetCacheLimit = 20
  private constructor() {
    this.spriteCache = new Map()
  }
  /**
   * Returns the singleton SpriteManager instance.
   */
  public static getInstance(): \'SpriteManager\' {
    if (!SpriteManager.instance) {
      SpriteManager.instance = new SpriteManager()
    }
    return SpriteManager.instance
  }
  /**
   * Set the maximum number of individual sprites to cache. Oldest are evicted if exceeded.
   * @param limit Maximum number of sprites to cache.
   */
  public setSpriteCacheLimit(limit: float) {
    this.spriteCacheLimit = limit
    this.evictSpriteCacheIfNeeded()
  }
  /**
   * Set the maximum number of sprite sheets to cache. Oldest are evicted if exceeded.
   * @param limit Maximum number of sprite sheets to cache.
   */
  public setSpriteSheetCacheLimit(limit: float) {
    this.spriteSheetCacheLimit = limit
    this.evictSpriteSheetCacheIfNeeded()
  }
  private evictSpriteCacheIfNeeded() {
    while (this.spriteCache.size > this.spriteCacheLimit) {
      const firstKey = this.spriteCache.keys().next().value
      if (typeof firstKey === 'string') {
        this.spriteCache.delete(firstKey)
      } else {
        break
      }
    }
  }
  private evictSpriteSheetCacheIfNeeded() {
    while (this.spriteSheetCache.size > this.spriteSheetCacheLimit) {
      const firstKey = this.spriteSheetCache.keys().next().value
      if (typeof firstKey === 'string') {
        this.spriteSheetCache.delete(firstKey)
      } else {
        break
      }
    }
  }
  /**
   * Loads a sprite from a file path. Returns a Promise that resolves to the Sprite object.
   * Uses cache if already loaded. Supports PNG/JPEG.
   * @param path File path or URL to the sprite image.
   * @returns Promise<Sprite>
   */
  public async loadSprite(path: str): Promise<Sprite> {
    if (this.spriteCache.has(path)) {
      const sprite = this.spriteCache.get(path)!
      this.spriteCache.delete(path)
      this.spriteCache.set(path, sprite)
      return sprite
    }
    return new Promise((resolve, reject) => {
      const img = new window.Image()
      img.onload = () => {
        const sprite: \'Sprite\' = {
          image: img,
          width: img.width,
          height: img.height,
          src: path,
        }
        this.spriteCache.set(path, sprite)
        this.evictSpriteCacheIfNeeded()
        resolve(sprite)
      }
      img.onerror = e => reject(e)
      img.src = path
    })
  }
  /**
   * Returns a cached sprite if available, or undefined.
   * @param path File path or URL to the sprite image.
   * @returns Sprite | undefined
   */
  public getSprite(path: str): \'Sprite\' | undefined {
    if (!this.spriteCache.has(path)) return undefined
    const sprite = this.spriteCache.get(path)!
    this.spriteCache.delete(path)
    this.spriteCache.set(path, sprite)
    return sprite
  }
  /**
   * Loads a sprite sheet and slices it into frames of given size.
   * Returns a Promise that resolves to an array of Sprite objects (one per frame).
   * Uses cache if already loaded.
   * @param path File path or URL to the sprite sheet image.
   * @param frameWidth Width of each frame in pixels.
   * @param frameHeight Height of each frame in pixels.
   * @returns Promise<Sprite[]>
   */
  public async loadSpriteSheet(
    path: str,
    frameWidth: float,
    frameHeight: float
  ): Promise<Sprite[]> {
    const key = `${path}|${frameWidth}x${frameHeight}`
    if (this.spriteSheetCache.has(key)) {
      const sheet = this.spriteSheetCache.get(key)!
      this.spriteSheetCache.delete(key)
      this.spriteSheetCache.set(key, sheet)
      return sheet.frames
    }
    return new Promise((resolve, reject) => {
      const img = new window.Image()
      img.onload = () => {
        const frames: List[Sprite] = []
        const cols = Math.floor(img.width / frameWidth)
        const rows = Math.floor(img.height / frameHeight)
        for (let y = 0; y < rows; y++) {
          for (let x = 0; x < cols; x++) {
            const canvas = document.createElement('canvas')
            canvas.width = frameWidth
            canvas.height = frameHeight
            const ctx = canvas.getContext('2d')!
            ctx.clearRect(0, 0, frameWidth, frameHeight)
            ctx.drawImage(
              img,
              x * frameWidth,
              y * frameHeight,
              frameWidth,
              frameHeight,
              0,
              0,
              frameWidth,
              frameHeight
            )
            const frameImg = new window.Image()
            frameImg.src = canvas.toDataURL()
            frames.push({
              image: frameImg,
              width: frameWidth,
              height: frameHeight,
              src: `${path}#${x},${y}`,
            })
          }
        }
        const sheet: \'SpriteSheet\' = {
          image: img,
          frames,
          frameWidth,
          frameHeight,
          src: path,
        }
        this.spriteSheetCache.set(key, sheet)
        this.evictSpriteSheetCacheIfNeeded()
        resolve(frames)
      }
      img.onerror = e => reject(e)
      img.src = path
    })
  }
  /**
   * Returns cached sprite sheet frames if available, or undefined.
   * @param path File path or URL to the sprite sheet image.
   * @param frameWidth Width of each frame in pixels.
   * @param frameHeight Height of each frame in pixels.
   * @returns Sprite[] | undefined
   */
  public getSpriteSheet(
    path: str,
    frameWidth: float,
    frameHeight: float
  ): Sprite[] | undefined {
    const key = `${path}|${frameWidth}x${frameHeight}`
    if (!this.spriteSheetCache.has(key)) return undefined
    const sheet = this.spriteSheetCache.get(key)!
    this.spriteSheetCache.delete(key)
    this.spriteSheetCache.set(key, sheet)
    return sheet.frames
  }
  /**
   * Clears all sprite and sprite sheet caches.
   */
  public clearCache(): void {
    this.spriteCache.clear()
    this.spriteSheetCache.clear()
  }
}
/**
 * Applies a tint/color overlay to a sprite and returns a new Sprite.
 * @param sprite The original sprite
 * @param tint CSS color string or {r,g,b,a}
 * @returns New Sprite with tint applied
 */
function applyTintToSprite(
  sprite: \'Sprite\',
  tint: str | { r: float; g: float; b: float; a?: float }
): \'Sprite\' {
  const canvas = document.createElement('canvas')
  canvas.width = sprite.width
  canvas.height = sprite.height
  const ctx = canvas.getContext('2d')!
  ctx.clearRect(0, 0, sprite.width, sprite.height)
  ctx.drawImage(sprite.image, 0, 0, sprite.width, sprite.height)
  ctx.globalCompositeOperation = 'source-atop'
  let color: str
  if (typeof tint === 'string') {
    color = tint
  } else {
    const { r, g, b, a } = tint
    color = `rgba(${r},${g},${b},${a !== undefined ? a : 1})`
  }
  ctx.fillStyle = color
  ctx.fillRect(0, 0, sprite.width, sprite.height)
  ctx.globalCompositeOperation = 'source-over'
  const tintedImg = new window.Image()
  tintedImg.src = canvas.toDataURL()
  return {
    image: tintedImg,
    width: sprite.width,
    height: sprite.height,
    src: sprite.src + `#tint=${encodeURIComponent(color)}`,
  }
}
default SpriteManager