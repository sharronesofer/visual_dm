from typing import Any, Dict, List



  AnimationConfig,
  AnimationController,
  AnimationEventHandlers,
  AnimationState,
  LayerConfig,
  PageTransitionType,
  AnimationValue
} from './types'
  ANIMATION_TIMING,
  PERFORMANCE_THRESHOLDS,
  ANIMATION_DEFAULTS
} from './constants'
class MedievalAnimationController implements AnimationController {
  private state: AnimationState
  private animationFrame: float | null = null
  private startTime: float | null = null
  private handlers: AnimationEventHandlers = {}
  private lastFrameTime: float = 0
  private readonly targetFPS: float = ANIMATION_DEFAULTS.targetFPS
  private readonly frameInterval: float = ANIMATION_DEFAULTS.frameInterval
  private frameCount: float = 0
  private fpsHistory: List[number] = []
  private performanceWarningIssued: bool = false
  private performanceMonitor: PerformanceMonitor
  constructor() {
    this.performanceMonitor = new PerformanceMonitor()
    this.state = {
      isAnimating: false,
      progress: 0,
      currentType: 'fade',
      direction: 'forward',
      layers: Dict[str, Any]
    }
  }
  public play(config: AnimationConfig): Promise<void> {
    return new Promise<void>((resolve) => {
      this.state = {
        ...this.state,
        isAnimating: true,
        progress: 0,
        currentType: config.type,
        config
      }
      this.handlers.onComplete = () => {
        resolve()
      }
      this.animationFrame = requestAnimationFrame(this.animate.bind(this))
    })
  }
  public pause(): void {
    if (this.animationFrame !== null) {
      cancelAnimationFrame(this.animationFrame)
      this.animationFrame = null
    }
  }
  public resume(): void {
    if (!this.state.isAnimating && this.state.progress < 1) {
      this.startTime = performance.now() - (this.state.progress * this.state.config!.timing.duration)
      this.animationFrame = requestAnimationFrame(this.animate.bind(this))
    }
  }
  public cancel(): void {
    if (this.animationFrame !== null) {
      cancelAnimationFrame(this.animationFrame)
      this.animationFrame = null
    }
    this.startTime = null
    this.state.isAnimating = false
    this.performanceMonitor.reset()
  }
  public reverse(): void {
    if (this.state.config) {
      const { layers } = this.state.config
      this.state.config.layers = {
        foreground: Dict[str, Any],
        background: layers.background ? {
          ...layers.background,
          opacity: Array.isArray(layers.background.opacity)
            ? [layers.background.opacity[1], layers.background.opacity[0]]
            : layers.background.opacity
        } : undefined
      }
      this.state.direction = this.state.direction === 'forward' ? 'backward' : 'forward'
      this.play(this.state.config)
    }
  }
  public getState(): AnimationState {
    return this.state
  }
  private startAnimation(): void {
    this.startTime = performance.now()
    this.lastFrameTime = this.startTime
    this.animate()
  }
  private animate = (): void => {
    if (!this.startTime || !this.state.isAnimating) return
    const currentTime = performance.now()
    const timeSinceLastFrame = currentTime - this.lastFrameTime
    if (timeSinceLastFrame < this.frameInterval) {
      this.animationFrame = requestAnimationFrame(this.animate)
      return
    }
    const fps = 1000 / timeSinceLastFrame
    this.fpsHistory.push(fps)
    if (this.fpsHistory.length > 60) {
      this.fpsHistory.shift()
    }
    this.frameCount++
    this.lastFrameTime = currentTime
    if (ANIMATION_DEFAULTS.performanceMonitoring && !this.performanceWarningIssued) {
      const avgFps = this.fpsHistory.reduce((a, b) => a + b, 0) / this.fpsHistory.length
      if (avgFps < PERFORMANCE_THRESHOLDS.FPS.WARNING) {
        console.warn(`Animation performance warning - FPS: ${avgFps.toFixed(2)}`)
        this.performanceWarningIssued = true
      }
    }
    const elapsed = currentTime - this.startTime
    const duration = ANIMATION_TIMING.DURATION.NORMAL 
    let progress = Math.min(elapsed / duration, 1)
    if (this.state.direction === 'backward') {
      progress = 1 - progress
    }
    this.state.progress = progress
    this.handlers.onUpdate?.(progress)
    if (progress < 1 && this.state.direction === 'forward' || 
        progress > 0 && this.state.direction === 'backward') {
      this.animationFrame = requestAnimationFrame(this.animate)
    } else {
      this.handlers.onComplete?.()
    }
  }
  private interpolateValue(value: AnimationValue, progress: float): float {
    if (Array.isArray(value)) {
      const [start, end] = value
      return start + (end - start) * progress
    }
    return value
  }
  private interpolateLayer(config: LayerConfig, progress: float): LayerConfig {
    const result: LayerConfig = {
      opacity: this.interpolateValue(config.opacity, progress)
    }
    if (config.blur !== undefined) {
      result.blur = this.interpolateValue(config.blur, progress)
    }
    if (config.scale !== undefined) {
      result.scale = this.interpolateValue(config.scale, progress)
    }
    if (config.rotation !== undefined) {
      result.rotation = this.interpolateValue(config.rotation, progress)
    }
    if (config.transformOrigin) {
      result.transformOrigin = config.transformOrigin
    }
    return result
  }
  private getDefaultLayer(): LayerConfig {
    return {
      opacity: 0,
      scale: 1,
      rotation: 0,
      blur: 0
    }
  }
  private updateLayers(progress: float, config: AnimationConfig): void {
    const { foreground, background } = config.layers
    const easedProgress = this.applyEasing(
      progress, 
      config.timing?.easing || ANIMATION_DEFAULTS.defaultEasing
    )
    const layers = {
      foreground: this.interpolateLayer(foreground, easedProgress),
      background: this.interpolateLayer(
        background || this.getDefaultLayer(), 
        easedProgress
      )
    }
    this.state = {
      ...this.state,
      layers
    }
  }
  private applyEasing(progress: float, easing: str): float {
    const easingLookup: Dict[str, Any] } = {
      0: Dict[str, Any],
      0.25: Dict[str, Any],
      0.5: Dict[str, Any],
      0.75: Dict[str, Any],
      1: Dict[str, Any]
    }
    const closestProgress = Math.round(progress * 4) / 4
    if (easing !== 'linear' && easingLookup[closestProgress]?.[easing]) {
      return easingLookup[closestProgress][easing]
    }
    switch (easing) {
      case 'linear':
        return progress
      case 'easeInOut':
        return progress < 0.5
          ? 2 * progress * progress
          : 1 - Math.pow(-2 * progress + 2, 2) / 2
      case 'easeIn':
        return progress * progress
      case 'easeOut':
        return 1 - Math.pow(1 - progress, 2)
      default:
        return progress
    }
  }
  private cleanup(): void {
    if (this.animationFrame) {
      cancelAnimationFrame(this.animationFrame)
      this.animationFrame = null
    }
    this.startTime = null
    this.state.isAnimating = false
    this.handlers = {}
    this.frameCount = 0
    this.fpsHistory = []
    this.lastFrameTime = 0
    this.performanceWarningIssued = false
  }
  public getPerformanceMetrics() {
    return this.performanceMonitor.getMetrics()
  }
} 