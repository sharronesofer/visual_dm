import SpriteManager, { Sprite } from '../SpriteManager';

describe('SpriteManager', () => {
  let manager: SpriteManager;
  beforeEach(() => {
    manager = SpriteManager.getInstance();
    manager.clearCache();
  });

  it('returns the same singleton instance', () => {
    const m2 = SpriteManager.getInstance();
    expect(manager).toBe(m2);
  });

  it('loads a sprite and caches it', async () => {
    // Mock Image
    const mockImg = {
      width: 32,
      height: 32,
      src: '',
      onload: null,
      onerror: null,
    } as any;
    jest.spyOn(window, 'Image').mockImplementation(() => mockImg);
    const promise = manager.loadSprite('test.png');
    // Simulate load
    setTimeout(() => mockImg.onload && mockImg.onload(null), 0);
    const sprite = await promise;
    expect(sprite.width).toBe(32);
    expect(sprite.height).toBe(32);
    expect(sprite.src).toBe('test.png');
    expect(manager.getSprite('test.png')).toBe(sprite);
    (window.Image as jest.Mock).mockRestore();
  });

  it('returns cached sprite if already loaded', async () => {
    const mockImg = {
      width: 16,
      height: 16,
      src: '',
      onload: null,
      onerror: null,
    } as any;
    jest.spyOn(window, 'Image').mockImplementation(() => mockImg);
    setTimeout(() => mockImg.onload && mockImg.onload(null), 0);
    const sprite1 = await manager.loadSprite('foo.jpg');
    const sprite2 = await manager.loadSprite('foo.jpg');
    expect(sprite1).toBe(sprite2);
    (window.Image as jest.Mock).mockRestore();
  });

  it('supports PNG and JPEG file types', async () => {
    const mockImg = {
      width: 8,
      height: 8,
      src: '',
      onload: null,
      onerror: null,
    } as any;
    jest.spyOn(window, 'Image').mockImplementation(() => mockImg);
    setTimeout(() => mockImg.onload && mockImg.onload(null), 0);
    const spritePng = await manager.loadSprite('sprite.png');
    expect(spritePng.src).toBe('sprite.png');
    setTimeout(() => mockImg.onload && mockImg.onload(null), 0);
    const spriteJpg = await manager.loadSprite('sprite.jpg');
    expect(spriteJpg.src).toBe('sprite.jpg');
    (window.Image as jest.Mock).mockRestore();
  });

  it('clears the cache', async () => {
    const mockImg = {
      width: 4,
      height: 4,
      src: '',
      onload: null,
      onerror: null,
    } as any;
    jest.spyOn(window, 'Image').mockImplementation(() => mockImg);
    setTimeout(() => mockImg.onload && mockImg.onload(null), 0);
    await manager.loadSprite('bar.png');
    expect(manager.getSprite('bar.png')).toBeDefined();
    manager.clearCache();
    expect(manager.getSprite('bar.png')).toBeUndefined();
    (window.Image as jest.Mock).mockRestore();
  });

  it('loads a sprite sheet and slices into frames', async () => {
    // Mock Image and canvas
    const mockImg = {
      width: 32,
      height: 16,
      src: '',
      onload: null,
      onerror: null,
    } as any;
    jest.spyOn(window, 'Image').mockImplementation(() => mockImg);
    const mockCanvas = {
      width: 0,
      height: 0,
      getContext: () => ({
        clearRect: jest.fn(),
        drawImage: jest.fn(),
      }),
    } as any;
    jest
      .spyOn(document, 'createElement')
      .mockImplementation((tag: string) =>
        tag === 'canvas' ? mockCanvas : ({} as any)
      );
    // Mock toDataURL for canvas
    (mockCanvas as any).toDataURL = () => 'data:image/png;base64,frame';
    // Simulate load
    setTimeout(() => mockImg.onload && mockImg.onload(null), 0);
    const frames = await manager.loadSpriteSheet('sheet.png', 16, 16);
    expect(frames.length).toBe(2); // 32x16 with 16x16 frames = 2 frames
    expect(frames[0].width).toBe(16);
    expect(frames[0].height).toBe(16);
    expect(frames[0].src).toContain('sheet.png#0,0');
    expect(frames[1].src).toContain('sheet.png#1,0');
    // Should be cached
    expect(manager.getSpriteSheet('sheet.png', 16, 16)).toEqual(frames);
    (window.Image as jest.Mock).mockRestore();
    (document.createElement as jest.Mock).mockRestore();
  });

  it('clears sprite sheet cache', async () => {
    const mockImg = {
      width: 16,
      height: 16,
      src: '',
      onload: null,
      onerror: null,
    } as any;
    jest.spyOn(window, 'Image').mockImplementation(() => mockImg);
    const mockCanvas = {
      width: 0,
      height: 0,
      getContext: () => ({
        clearRect: jest.fn(),
        drawImage: jest.fn(),
      }),
    } as any;
    jest
      .spyOn(document, 'createElement')
      .mockImplementation((tag: string) =>
        tag === 'canvas' ? mockCanvas : ({} as any)
      );
    (mockCanvas as any).toDataURL = () => 'data:image/png;base64,frame';
    setTimeout(() => mockImg.onload && mockImg.onload(null), 0);
    await manager.loadSpriteSheet('sheet2.png', 16, 16);
    expect(manager.getSpriteSheet('sheet2.png', 16, 16)).toBeDefined();
    manager.clearCache();
    expect(manager.getSpriteSheet('sheet2.png', 16, 16)).toBeUndefined();
    (window.Image as jest.Mock).mockRestore();
    (document.createElement as jest.Mock).mockRestore();
  });

  it('evicts least-recently-used sprites when cache limit is exceeded', async () => {
    manager.setSpriteCacheLimit(2);
    // Mock Image
    const mk = (w: number) => {
      const img = {
        width: w,
        height: w,
        src: '',
        onload: undefined,
        onerror: undefined,
      } as any;
      setTimeout(() => {
        if (typeof img.onload === 'function') img.onload(new Event('load'));
      }, 0);
      return img;
    };
    jest.spyOn(window, 'Image').mockImplementation(() => mk(1));
    await manager.loadSprite('a');
    jest.spyOn(window, 'Image').mockImplementation(() => mk(2));
    await manager.loadSprite('b');
    jest.spyOn(window, 'Image').mockImplementation(() => mk(3));
    await manager.loadSprite('c');
    // Only 'b' and 'c' should remain
    expect(manager.getSprite('a')).toBeUndefined();
    expect(manager.getSprite('b')).toBeDefined();
    expect(manager.getSprite('c')).toBeDefined();
    (window.Image as jest.Mock).mockRestore();
  });

  it('evicts least-recently-used sprite sheets when cache limit is exceeded', async () => {
    manager.setSpriteSheetCacheLimit(1);
    const mk = (w: number) => {
      const img = {
        width: w,
        height: 16,
        src: '',
        onload: undefined,
        onerror: undefined,
      } as any;
      setTimeout(() => {
        if (typeof img.onload === 'function') img.onload(new Event('load'));
      }, 0);
      return img;
    };
    jest.spyOn(window, 'Image').mockImplementation(() => mk(16));
    const mockCanvas = {
      width: 0,
      height: 0,
      getContext: () => ({ clearRect: jest.fn(), drawImage: jest.fn() }),
    } as any;
    jest
      .spyOn(document, 'createElement')
      .mockImplementation((tag: string) =>
        tag === 'canvas' ? mockCanvas : ({} as any)
      );
    (mockCanvas as any).toDataURL = () => 'data:image/png;base64,frame';
    await manager.loadSpriteSheet('sheetA.png', 16, 16);
    jest.spyOn(window, 'Image').mockImplementation(() => mk(16));
    await manager.loadSpriteSheet('sheetB.png', 16, 16);
    // Only sheetB should remain
    expect(manager.getSpriteSheet('sheetA.png', 16, 16)).toBeUndefined();
    expect(manager.getSpriteSheet('sheetB.png', 16, 16)).toBeDefined();
    (window.Image as jest.Mock).mockRestore();
    (document.createElement as jest.Mock).mockRestore();
  });
});
