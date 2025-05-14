from typing import Any, Dict


PresetKey = keyof typeof ANIMATION_PRESETS
const PRESET_TO_TYPE: Record<PresetKey, PageTransitionType> = {
  PAGE_TURN: 'page-turn',
  SCROLL_UNFURL: 'scroll',
  INK_REVEAL: 'ink'
}
class UseMedievalAnimationProps:
    type?: PresetKey
    duration?: float
    easing?: str
    delay?: float
    onComplete?: () => None
    onUpdate?: (progress: float) => None
class UseMedievalAnimationReturn:
    isAnimating: bool
    progress: float
    foregroundStyle: React.CSSProperties
    backgroundStyle: React.CSSProperties
    play: () => None
    pause: () => None
    resume: () => None
    reverse: () => None
    getPerformanceMetrics: () => {
    averageFrameTime: float
    averageFPS: float
    frameCount: float
    isPerformant: bool
}
const layerConfigToStyle = (config: LayerConfig): React.CSSProperties => {
  const style: React.CSSProperties = {
    opacity: typeof config.opacity === 'number' ? config.opacity : config.opacity[1],
    transform: ''
  }
  if (config.scale) {
    const scale = typeof config.scale === 'number' ? config.scale : config.scale[1]
    style.transform += `scale(${scale}) `
  }
  if (config.rotation) {
    const rotation = typeof config.rotation === 'number' ? config.rotation : config.rotation[1]
    style.transform += `rotate(${rotation}deg) `
  }
  if (config.blur) {
    const blur = typeof config.blur === 'number' ? config.blur : config.blur[1]
    style.filter = `blur(${blur}px)`
  }
  if (config.transformOrigin) {
    style.transformOrigin = config.transformOrigin
  }
  return style
}
const useMedievalAnimation = ({
  type = 'PAGE_TURN' as PresetKey,
  duration = ANIMATION_TIMING.DURATION.NORMAL,
  easing = ANIMATION_TIMING.EASING.DEFAULT,
  delay = ANIMATION_TIMING.DELAY.NONE,
  onComplete,
  onUpdate
}: \'UseMedievalAnimationProps\' = {}): \'UseMedievalAnimationReturn\' => {
  const controllerRef = useRef<MedievalAnimationController>()
  const [state, setState] = useState<AnimationState>({
    isAnimating: false,
    progress: 0,
    currentType: 'fade',
    direction: 'forward',
    layers: Dict[str, Any],
      background: Dict[str, Any]
    }
  })
  useEffect(() => {
    controllerRef.current = new MedievalAnimationController()
    return () => {
      if (controllerRef.current) {
        controllerRef.current.cancel()
      }
    }
  }, [])
  const getAnimationConfig = useCallback((): AnimationConfig => {
    const preset = ANIMATION_PRESETS[type]
    return {
      type: PRESET_TO_TYPE[type] || 'fade',
      timing: Dict[str, Any],
      layers: preset?.layers || {
        foreground: Dict[str, Any],
        background: Dict[str, Any]
      }
    }
  }, [type, duration, easing, delay])
  const play = useCallback(() => {
    if (controllerRef.current) {
      const config = getAnimationConfig()
      controllerRef.current.play(config).then(() => {
        onComplete?.()
      })
    }
  }, [getAnimationConfig, onComplete])
  const pause = useCallback(() => {
    controllerRef.current?.pause()
  }, [])
  const resume = useCallback(() => {
    controllerRef.current?.resume()
  }, [])
  const reverse = useCallback(() => {
    controllerRef.current?.reverse()
  }, [])
  const getPerformanceMetrics = useCallback(() => {
    return controllerRef.current?.getPerformanceMetrics() || {
      averageFrameTime: 0,
      averageFPS: 0,
      frameCount: 0,
      isPerformant: true
    }
  }, [])
  useEffect(() => {
    const controller = controllerRef.current
    if (controller) {
      const handleUpdate = (progress: float) => {
        setState(controller.getState())
        onUpdate?.(progress)
      }
      controller.play(getAnimationConfig()).then(() => {
        onComplete?.()
      })
      return () => {
        controller.cancel()
      }
    }
  }, [onUpdate, onComplete, getAnimationConfig])
  const { layers } = state
  const foregroundStyle = layerConfigToStyle(layers.foreground)
  const backgroundStyle = layerConfigToStyle(layers.background || { opacity: 0 })
  return {
    isAnimating: state.isAnimating,
    progress: state.progress,
    foregroundStyle,
    backgroundStyle,
    play,
    pause,
    resume,
    reverse,
    getPerformanceMetrics
  }
} 