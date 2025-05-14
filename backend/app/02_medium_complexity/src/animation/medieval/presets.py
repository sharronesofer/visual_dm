from typing import Any, Dict



const presets: Record<string, AnimationPreset> = {
  classicPageTurn: Dict[str, Any],
      layers: ANIMATION_PRESETS.PAGE_TURN.layers
    },
    description: 'A classic medieval book page turning animation',
    tags: ['page', 'book', 'turn', 'classic']
  },
  scrollUnfurl: Dict[str, Any],
      layers: ANIMATION_PRESETS.SCROLL_UNFURL.layers
    },
    description: 'Unfurls content like an ancient scroll',
    tags: ['scroll', 'unfurl', 'reveal']
  },
  inkReveal: Dict[str, Any],
      layers: ANIMATION_PRESETS.INK_REVEAL.layers
    },
    description: 'Reveals content with an ink-spreading effect',
    tags: ['ink', 'reveal', 'fade']
  },
  ambientParchment: Dict[str, Any],
      layers: Dict[str, Any]
      }
    },
    description: 'Subtle ambient movement for parchment backgrounds',
    tags: ['ambient', 'background', 'subtle']
  },
  quickFade: Dict[str, Any],
      layers: Dict[str, Any]
      }
    },
    description: 'Fast fade transition for quick content updates',
    tags: ['fade', 'quick', 'simple']
  }
}
const getPreset = (name: keyof typeof presets): AnimationPreset => {
  if (!presets[name]) {
    throw new Error(`Animation preset "${name}" not found`)
  }
  return presets[name]
}
const getPresetsByTag = (tag: str): AnimationPreset[] => {
  return Object.values(presets).filter(preset => preset.tags.includes(tag))
}
const getAllPresets = (): AnimationPreset[] => {
  return Object.values(presets)
} 