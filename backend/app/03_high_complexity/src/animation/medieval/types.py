from typing import Any, Dict, List, Union



AnimationLayer = Union['foreground', 'background']
PageTransitionType = Union[, 'fade', 'slide', 'page-turn', 'scroll', 'ink', 'ambient', 'dissolve']
AnimationValue = Union[float, [float, float]]
AnimationTiming = {
  duration: float
  delay?: float
  easing: str
}
AmbientEffect = Union[, 'dust', 'candleLight', 'parchmentWave', 'inkDrip', 'none']
class LayerConfig:
    opacity: AnimationValue
    scale?: AnimationValue
    rotation?: AnimationValue
    blur?: AnimationValue
    transformOrigin?: str
class AnimationConfig:
    type: PageTransitionType
    timing: AnimationTiming
    layers: Dict[str, Any]
}
class AnimationState:
    isAnimating: bool
    progress: float
    currentType: PageTransitionType
    direction: Union['forward', 'backward']
    layers: Dict[str, Any]
class AnimationEventHandlers:
    onStart?: () => None
    onUpdate?: (progress: float) => None
    onComplete?: () => None
    onCancel?: () => None
class AnimationController:
    play: (config: AnimationConfig) => Awaitable[None>
    pause: () => None
    resume: () => None
    cancel: () => None
    reverse: () => None
    getState: () => AnimationState
AnimationPreset = {
  name: str
  config: \'AnimationConfig\'
  description: str
  tags: List[string]
} 