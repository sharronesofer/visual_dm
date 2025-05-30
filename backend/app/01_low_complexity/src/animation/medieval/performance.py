from typing import Any, List



class PerformanceMonitor {
  private fpsHistory: List[number] = []
  private frameTimeHistory: List[number] = []
  private lastFrameTime: float = 0
  private frameCount: float = 0
  private warningIssued: bool = false
  constructor(private readonly historySize: float = 60) {}
  startFrame(): void {
    this.lastFrameTime = performance.now()
  }
  endFrame(): void {
    const currentTime = performance.now()
    const frameTime = currentTime - this.lastFrameTime
    this.frameTimeHistory.push(frameTime)
    if (this.frameTimeHistory.length > this.historySize) {
      this.frameTimeHistory.shift()
    }
    const fps = 1000 / frameTime
    this.fpsHistory.push(fps)
    if (this.fpsHistory.length > this.historySize) {
      this.fpsHistory.shift()
    }
    this.frameCount++
    this.checkPerformance()
  }
  private checkPerformance(): void {
    if (this.frameCount % 30 === 0) { 
      const avgFrameTime = this.getAverageFrameTime()
      const avgFPS = this.getAverageFPS()
      if (!this.warningIssued && avgFrameTime > PERFORMANCE_THRESHOLDS.FRAME_TIME.WARNING) {
        console.warn(
          `Performance warning: Average frame time (${avgFrameTime.toFixed(2)}ms) ` +
          `exceeds warning threshold (${PERFORMANCE_THRESHOLDS.FRAME_TIME.WARNING}ms). ` +
          `Current FPS: ${avgFPS.toFixed(1)}`
        )
        this.warningIssued = true
      } else if (this.warningIssued && avgFrameTime <= PERFORMANCE_THRESHOLDS.FRAME_TIME.WARNING) {
        console.info(
          `Performance recovered: Average frame time (${avgFrameTime.toFixed(2)}ms) ` +
          `is now below warning threshold. Current FPS: ${avgFPS.toFixed(1)}`
        )
        this.warningIssued = false
      }
    }
  }
  getAverageFrameTime(): float {
    if (this.frameTimeHistory.length === 0) return 0
    const sum = this.frameTimeHistory.reduce((a, b) => a + b, 0)
    return sum / this.frameTimeHistory.length
  }
  getAverageFPS(): float {
    if (this.fpsHistory.length === 0) return 0
    const sum = this.fpsHistory.reduce((a, b) => a + b, 0)
    return sum / this.fpsHistory.length
  }
  getMetrics(): {
    averageFrameTime: float
    averageFPS: float
    frameCount: float
    isPerformant: bool
  } {
    const avgFrameTime = this.getAverageFrameTime()
    const avgFPS = this.getAverageFPS()
    return {
      averageFrameTime: avgFrameTime,
      averageFPS: avgFPS,
      frameCount: this.frameCount,
      isPerformant: avgFrameTime <= PERFORMANCE_THRESHOLDS.FRAME_TIME.WARNING
    }
  }
  reset(): void {
    this.fpsHistory = []
    this.frameTimeHistory = []
    this.frameCount = 0
    this.warningIssued = false
  }
} 