from typing import Any, Dict



describe('MapRenderer', () => {
  let container: HTMLElement
  let mapData: MapData
  let renderer: MapRenderer
  beforeEach(() => {
    container = document.createElement('div')
    container.style.width = '800px'
    container.style.height = '600px'
    document.body.appendChild(container)
    mapData = {
      size: Dict[str, Any],
      tiles: Array(10).fill(null).map((_, y) => 
        Array(10).fill(null).map((_, x) => ({
          id: `tile-${x}-${y}`,
          type: TerrainType.GRASS,
          position: Dict[str, Any],
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
          position: Dict[str, Any],
          size: Dict[str, Any],
          elevation: 0,
          interactive: true,
          data: {}
        }
      ]
    }
    renderer = new MapRenderer(mapData)
  })
  afterEach(() => {
    renderer.dispose()
    container.remove()
  })
  test('initializes correctly', async () => {
    await renderer.initialize(container)
    expect(container.children.length).toBe(1)
    expect(container.children[0]).toBeInstanceOf(HTMLCanvasElement)
  })
  test('handles viewport changes', async () => {
    await renderer.initialize(container)
    const newViewport = {
      position: Dict[str, Any],
      zoom: 2
    }
    renderer.setViewport(newViewport)
  })
  test('handles render options changes', async () => {
    await renderer.initialize(container)
    const newOptions = {
      showGrid: false,
      showFogOfWar: false
    }
    renderer.setRenderOptions(newOptions)
  })
  test('handles interaction listeners', async () => {
    await renderer.initialize(container)
    const mockListener = jest.fn()
    renderer.addInteractionListener(mockListener)
    const event = new MouseEvent('click', {
      clientX: 100,
      clientY: 100
    })
    container.children[0].dispatchEvent(event)
    expect(mockListener).toHaveBeenCalled()
  })
  test('cleans up resources on dispose', async () => {
    await renderer.initialize(container)
    renderer.dispose()
    expect(container.children.length).toBe(0)
  })
}) 