from typing import Any, Dict


describe('MedievalAnimationController', () => {
  let controller: MedievalAnimationController
  let requestAnimationFrameMock: jest.SpyInstance
  let performanceNowMock: jest.SpyInstance
  let consoleWarnMock: jest.SpyInstance
  beforeEach(() => {
    controller = new MedievalAnimationController()
    requestAnimationFrameMock = jest.spyOn(window, 'requestAnimationFrame').mockImplementation(cb => setTimeout(cb, 0))
    performanceNowMock = jest.spyOn(performance, 'now').mockReturnValue(0)
    consoleWarnMock = jest.spyOn(console, 'warn').mockImplementation(() => {})
  })
  afterEach(() => {
    requestAnimationFrameMock.mockRestore()
    performanceNowMock.mockRestore()
    consoleWarnMock.mockRestore()
    jest.clearAllTimers()
  })
  const createTestConfig = (overrides?: Partial<AnimationConfig>): AnimationConfig => ({
    type: 'page-turn',
    timing: Dict[str, Any],
    layers: ANIMATION_PRESETS.PAGE_TURN.layers,
    ...overrides
  })
  describe('initialization', () => {
    it('should initialize with default state', () => {
      const state = controller.getState()
      expect(state.isAnimating).toBe(false)
      expect(state.progress).toBe(0)
      expect(state.direction).toBe('forward')
    })
  })
  describe('animation control', () => {
    it('should start animation when play is called', async () => {
      const config = createTestConfig()
      const promise = controller.play(config)
      const state = controller.getState()
      expect(state.isAnimating).toBe(true)
      expect(state.currentType).toBe('page-turn')
      await promise
    })
    it('should pause animation', () => {
      const config = createTestConfig()
      controller.play(config)
      controller.pause()
      expect(controller.getState().isAnimating).toBe(false)
    })
    it('should resume animation', () => {
      const config = createTestConfig()
      controller.play(config)
      controller.pause()
      controller.resume()
      expect(controller.getState().isAnimating).toBe(true)
    })
    it('should cancel animation', () => {
      const config = createTestConfig()
      controller.play(config)
      controller.cancel()
      const state = controller.getState()
      expect(state.isAnimating).toBe(false)
      expect(state.progress).toBe(0)
    })
    it('should reverse animation direction', () => {
      const config = createTestConfig()
      controller.play(config)
      controller.reverse()
      expect(controller.getState().direction).toBe('backward')
    })
  })
  describe('performance monitoring', () => {
    it('should track performance metrics', async () => {
      const config = createTestConfig()
      await controller.play(config)
      const metrics = controller.getPerformanceMetrics()
      expect(metrics.averageFrameTime).toBeGreaterThan(0)
      expect(metrics.averageFPS).toBeGreaterThan(0)
      expect(metrics.frameCount).toBeGreaterThan(0)
      expect(metrics.isPerformant).toBeDefined()
    })
    it('should issue performance warning when frame time exceeds threshold', async () => {
      performanceNowMock
        .mockReturnValueOnce(0)
        .mockReturnValueOnce(50) 
      const config = createTestConfig()
      await controller.play(config)
      expect(consoleWarnMock).toHaveBeenCalled()
    })
  })
  describe('layer interpolation', () => {
    it('should interpolate layer properties correctly', async () => {
      const config = createTestConfig({
        layers: Dict[str, Any]
        }
      })
      controller.play(config)
      performanceNowMock.mockReturnValue(ANIMATION_TIMING.DURATION.NORMAL / 2)
      await new Promise(resolve => setTimeout(resolve, 0))
      const state = controller.getState()
      expect(state.layers.foreground.opacity).toBeCloseTo(0.5)
      expect(state.layers.foreground.scale).toBeCloseTo(0.75)
    })
  })
}) 