import { MapRenderer } from '../MapRenderer';
import { MapData, TerrainType } from '../types';

describe('MapRenderer', () => {
  let container: HTMLElement;
  let mapData: MapData;
  let renderer: MapRenderer;

  beforeEach(() => {
    // Create container
    container = document.createElement('div');
    container.style.width = '800px';
    container.style.height = '600px';
    document.body.appendChild(container);

    // Create test map data
    mapData = {
      size: { width: 10, height: 10 },
      tiles: Array(10).fill(null).map((_, y) => 
        Array(10).fill(null).map((_, x) => ({
          id: `tile-${x}-${y}`,
          type: TerrainType.GRASS,
          position: { x, y },
          elevation: 0,
          walkable: true,
          explored: false,
          visible: false
        }))
      ),
      objects: [
        {
          id: 'test-object',
          type: 'test',
          position: { x: 2, y: 2 },
          size: { width: 1, height: 1 },
          elevation: 0,
          interactive: true,
          data: {}
        }
      ]
    };

    // Create renderer instance
    renderer = new MapRenderer(mapData);
  });

  afterEach(() => {
    renderer.dispose();
    container.remove();
  });

  test('initializes correctly', async () => {
    await renderer.initialize(container);
    expect(container.children.length).toBe(1);
    expect(container.children[0]).toBeInstanceOf(HTMLCanvasElement);
  });

  test('handles viewport changes', async () => {
    await renderer.initialize(container);
    
    const newViewport = {
      position: { x: 5, y: 5 },
      zoom: 2
    };
    
    renderer.setViewport(newViewport);
    // Visual inspection would be needed for actual rendering results
  });

  test('handles render options changes', async () => {
    await renderer.initialize(container);
    
    const newOptions = {
      showGrid: false,
      showFogOfWar: false
    };
    
    renderer.setRenderOptions(newOptions);
    // Visual inspection would be needed for actual rendering results
  });

  test('handles interaction listeners', async () => {
    await renderer.initialize(container);
    
    const mockListener = jest.fn();
    renderer.addInteractionListener(mockListener);
    
    // Simulate a click event
    const event = new MouseEvent('click', {
      clientX: 100,
      clientY: 100
    });
    container.children[0].dispatchEvent(event);
    
    expect(mockListener).toHaveBeenCalled();
  });

  test('cleans up resources on dispose', async () => {
    await renderer.initialize(container);
    renderer.dispose();
    
    expect(container.children.length).toBe(0);
  });
}); 