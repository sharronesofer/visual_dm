from typing import Any, Dict, List, Union


AnimationType = Union['loop', 'ping-pong', 'one-shot']
/**
 * Animation class for managing sprite frame sequences and timing.
 */
class Animation {
  private frames: List[string] 
  private frameDuration: float 
  private type: AnimationType
  private currentFrame: float
  private elapsed: float
  private state: 'playing' | 'paused' | 'stopped'
  private direction: 1 | -1
  private eventCallbacks: Dict[str, Any] = {
    onStart: [],
    onFrame: [],
    onComplete: [],
    onLoop: [],
  }
  private context: Any = undefined
  private hasStarted: bool = false
  /**
   * Create a new Animation.
   * @param frames Array of frame image paths
   * @param frameDuration Duration per frame in ms
   * @param type Animation type: loop, ping-pong, or one-shot
   */
  constructor(frames: List[string], frameDuration: float, type: AnimationType = 'loop') {
    this.frames = frames
    this.frameDuration = frameDuration
    this.type = type
    this.currentFrame = 0
    this.elapsed = 0
    this.state = 'stopped'
    this.direction = 1
  }
  /** Register a callback for an animation event. */
  on(event: 'onStart' | 'onFrame' | 'onComplete' | 'onLoop', callback: (...args: List[any]) => void) {
    this.eventCallbacks[event].push(callback)
  }
  /** Unregister a callback for an animation event. */
  off(event: 'onStart' | 'onFrame' | 'onComplete' | 'onLoop', callback: (...args: List[any]) => void) {
    this.eventCallbacks[event] = this.eventCallbacks[event].filter(cb => cb !== callback)
  }
  /** Set context data to be passed to event callbacks. */
  setContext(ctx: Any) {
    this.context = ctx
  }
  /** Clear all event callbacks and context. */
  clearEvents() {
    this.eventCallbacks = {
      onStart: [],
      onFrame: [],
      onComplete: [],
      onLoop: [],
    }
    this.context = undefined
  }
  /** Initialize or restart the animation. */
  initialize() {
    this.currentFrame = 0
    this.elapsed = 0
    this.state = 'playing'
    this.direction = 1
    this.hasStarted = false
    this.triggerEvent('onStart')
    this.hasStarted = true
  }
  /** Reset the animation to its initial state (stopped). */
  reset() {
    this.currentFrame = 0
    this.elapsed = 0
    this.state = 'stopped'
    this.direction = 1
    this.hasStarted = false
    this.clearEvents()
  }
  /** Get the current frame image path. */
  getCurrentFrame(): str {
    return this.frames[this.currentFrame]
  }
  /** Get the current animation state. */
  getState(): 'playing' | 'paused' | 'stopped' {
    return this.state
  }
  /** Get the animation type. */
  getType(): AnimationType {
    return this.type
  }
  /** Get the total number of frames. */
  getFrameCount(): float {
    return this.frames.length
  }
  /** Start or resume the animation. */
  play() {
    if (this.state !== 'playing') {
      this.state = 'playing'
    }
  }
  /** Pause the animation. */
  pause() {
    if (this.state === 'playing') {
      this.state = 'paused'
    }
  }
  /** Stop the animation and reset to the first frame. */
  stop() {
    this.state = 'stopped'
    this.currentFrame = 0
    this.elapsed = 0
    this.direction = 1
  }
  /** Update the animation by advancing frames based on elapsed time.
   * @param deltaTime Time in ms since last update
   */
  update(deltaTime: float) {
    if (this.state !== 'playing' || this.frames.length === 0) return
    if (!this.hasStarted) {
      this.triggerEvent('onStart')
      this.hasStarted = true
    }
    this.elapsed += deltaTime
    let frameChanged = false
    while (this.elapsed >= this.frameDuration) {
      this.elapsed -= this.frameDuration
      frameChanged = true
      this.advanceFrame()
    }
    if (frameChanged) {
      this.triggerEvent('onFrame', this.currentFrame)
    }
  }
  /** Advance the frame index based on animation type, triggering events as needed. */
  private advanceFrame() {
    if (this.type === 'loop') {
      const prevFrame = this.currentFrame
      this.currentFrame = (this.currentFrame + 1) % this.frames.length
      if (this.currentFrame === 0 && prevFrame !== 0) {
        this.triggerEvent('onLoop')
      }
    } else if (this.type === 'ping-pong') {
      this.currentFrame += this.direction
      if (this.currentFrame >= this.frames.length) {
        this.currentFrame = this.frames.length - 2
        this.direction = -1
        this.triggerEvent('onLoop')
      } else if (this.currentFrame < 0) {
        this.currentFrame = 1
        this.direction = 1
        this.triggerEvent('onLoop')
      }
    } else if (this.type === 'one-shot') {
      if (this.currentFrame < this.frames.length - 1) {
        this.currentFrame++
      } else {
        this.state = 'stopped'
        this.triggerEvent('onComplete')
      }
    }
  }
  /** Trigger all callbacks for a given event. */
  private triggerEvent(event: 'onStart' | 'onFrame' | 'onComplete' | 'onLoop', ...args: List[any]) {
    for (const cb of this.eventCallbacks[event]) {
      if (event === 'onFrame') {
        cb(args[0], this.context)
      } else {
        cb(this.context)
      }
    }
  }
  /** Returns true if the animation is currently playing. */
  isPlaying(): bool {
    return this.state === 'playing'
  }
  /** Returns true if the animation is currently paused. */
  isPaused(): bool {
    return this.state === 'paused'
  }
  /** Returns true if the animation is complete (for one-shot). */
  isComplete(): bool {
    return (
      this.type === 'one-shot' &&
      this.currentFrame === this.frames.length - 1 &&
      this.state === 'stopped'
    )
  }
}