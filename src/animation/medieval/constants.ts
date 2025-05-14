/**
 * Animation timing constants and configuration for medieval UI theme
 */

export const ANIMATION_TIMING = {
  DURATION: {
    FAST: 200,
    NORMAL: 500,
    SLOW: 800,
    PAGE_TURN: 600,
    SCROLL_UNFURL: 700,
    INK_REVEAL: 400,
    AMBIENT: 1500
  },
  EASING: {
    DEFAULT: 'cubic-bezier(0.4, 0, 0.2, 1)',
    PAGE_TURN: 'cubic-bezier(0.68, -0.6, 0.32, 1.6)',
    SCROLL: 'cubic-bezier(0.16, 1, 0.3, 1)',
    INK: 'cubic-bezier(0.22, 1, 0.36, 1)'
  },
  DELAY: {
    NONE: 0,
    SHORT: 100,
    MEDIUM: 200,
    LONG: 400
  }
} as const;

export const PERFORMANCE_THRESHOLDS = {
  FPS: {
    OPTIMAL: 60,
    WARNING: 45,
    CRITICAL: 30
  },
  FRAME_TIME: {
    TARGET: 1000 / 60, // ~16.67ms for 60fps
    WARNING: 1000 / 45, // ~22.22ms
    CRITICAL: 1000 / 30 // ~33.33ms
  }
} as const;

export const ANIMATION_DEFAULTS = {
  targetFPS: 60,
  frameInterval: 1000 / 60,
  defaultEasing: ANIMATION_TIMING.EASING.DEFAULT,
  defaultDuration: ANIMATION_TIMING.DURATION.NORMAL,
  defaultDelay: ANIMATION_TIMING.DELAY.NONE,
  performanceMonitoring: true
} as const;

export const ANIMATION_PRESETS = {
  PAGE_TURN: {
    layers: {
      foreground: {
        opacity: [1, 0] as [number, number],
        rotation: [-180, 0] as [number, number],
        transformOrigin: 'right'
      },
      background: {
        opacity: [0, 1] as [number, number],
        scale: [0.8, 1] as [number, number]
      }
    }
  },
  SCROLL_UNFURL: {
    layers: {
      foreground: {
        opacity: [0, 1] as [number, number],
        scale: [0.9, 1] as [number, number],
        transformOrigin: 'top'
      }
    }
  },
  INK_REVEAL: {
    layers: {
      foreground: {
        opacity: [0, 1] as [number, number],
        blur: [4, 0] as [number, number]
      }
    }
  }
} as const;

export const TEXTURE_ASSETS = {
  DUST: '/assets/textures/dust.png',
  PARCHMENT: '/assets/textures/parchment-normal.png',
  INK_DRIPS: '/assets/textures/ink-drips.png'
} as const; 