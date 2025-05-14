from typing import Any, Dict



/**
 * Animation timing constants and configuration for medieval UI theme
 */
const ANIMATION_TIMING = {
  DURATION: Dict[str, Any],
  EASING: Dict[str, Any],
  DELAY: Dict[str, Any]
} as const
const PERFORMANCE_THRESHOLDS = {
  FPS: Dict[str, Any],
  FRAME_TIME: Dict[str, Any]
} as const
const ANIMATION_DEFAULTS = {
  targetFPS: 60,
  frameInterval: 1000 / 60,
  defaultEasing: ANIMATION_TIMING.EASING.DEFAULT,
  defaultDuration: ANIMATION_TIMING.DURATION.NORMAL,
  defaultDelay: ANIMATION_TIMING.DELAY.NONE,
  performanceMonitoring: true
} as const
const ANIMATION_PRESETS = {
  PAGE_TURN: Dict[str, Any],
      background: Dict[str, Any]
    }
  },
  SCROLL_UNFURL: Dict[str, Any]
    }
  },
  INK_REVEAL: Dict[str, Any]
    }
  }
} as const
const TEXTURE_ASSETS = {
  DUST: '/assets/textures/dust.png',
  PARCHMENT: '/assets/textures/parchment-normal.png',
  INK_DRIPS: '/assets/textures/ink-drips.png'
} as const 