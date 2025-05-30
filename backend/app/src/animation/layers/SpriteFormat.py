from typing import Any, Dict, List


class AnimationFrame:
    image: HTMLImageElement
    duration: float
class AnimationSet:
    name: str
    frames: List[AnimationFrame]
    loop: bool
class SharedSpriteFormat:
    id: str
    anchor: Dict[str, Any]
function validateSpriteFormat(sprite: Any): sprite is SharedSpriteFormat {
  return (
    typeof sprite.id === 'string' &&
    typeof sprite.anchor === 'object' &&
    Array.isArray(sprite.animationSets) &&
    typeof sprite.width === 'number' &&
    typeof sprite.height === 'number'
  )
} 