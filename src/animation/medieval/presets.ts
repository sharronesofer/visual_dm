import { AnimationPreset } from './types';
import { ANIMATION_TIMING, ANIMATION_PRESETS } from './constants';

export const presets: Record<string, AnimationPreset> = {
  classicPageTurn: {
    name: 'Classic Page Turn',
    config: {
      type: 'page-turn',
      timing: {
        duration: ANIMATION_TIMING.DURATION.PAGE_TURN,
        easing: ANIMATION_TIMING.EASING.PAGE_TURN,
        delay: ANIMATION_TIMING.DELAY.NONE
      },
      layers: ANIMATION_PRESETS.PAGE_TURN.layers
    },
    description: 'A classic medieval book page turning animation',
    tags: ['page', 'book', 'turn', 'classic']
  },

  scrollUnfurl: {
    name: 'Scroll Unfurl',
    config: {
      type: 'scroll',
      timing: {
        duration: ANIMATION_TIMING.DURATION.SCROLL_UNFURL,
        easing: ANIMATION_TIMING.EASING.SCROLL,
        delay: ANIMATION_TIMING.DELAY.SHORT
      },
      layers: ANIMATION_PRESETS.SCROLL_UNFURL.layers
    },
    description: 'Unfurls content like an ancient scroll',
    tags: ['scroll', 'unfurl', 'reveal']
  },

  inkReveal: {
    name: 'Ink Reveal',
    config: {
      type: 'ink',
      timing: {
        duration: ANIMATION_TIMING.DURATION.INK_REVEAL,
        easing: ANIMATION_TIMING.EASING.INK,
        delay: ANIMATION_TIMING.DELAY.NONE
      },
      layers: ANIMATION_PRESETS.INK_REVEAL.layers
    },
    description: 'Reveals content with an ink-spreading effect',
    tags: ['ink', 'reveal', 'fade']
  },

  ambientParchment: {
    name: 'Ambient Parchment',
    config: {
      type: 'ambient',
      timing: {
        duration: ANIMATION_TIMING.DURATION.AMBIENT,
        easing: ANIMATION_TIMING.EASING.DEFAULT,
        delay: ANIMATION_TIMING.DELAY.MEDIUM
      },
      layers: {
        foreground: {
          opacity: [0.8, 1],
          scale: [0.98, 1.02],
          transformOrigin: 'center'
        }
      }
    },
    description: 'Subtle ambient movement for parchment backgrounds',
    tags: ['ambient', 'background', 'subtle']
  },

  quickFade: {
    name: 'Quick Fade',
    config: {
      type: 'fade',
      timing: {
        duration: ANIMATION_TIMING.DURATION.FAST,
        easing: ANIMATION_TIMING.EASING.DEFAULT,
        delay: ANIMATION_TIMING.DELAY.NONE
      },
      layers: {
        foreground: {
          opacity: [0, 1]
        }
      }
    },
    description: 'Fast fade transition for quick content updates',
    tags: ['fade', 'quick', 'simple']
  }
};

export const getPreset = (name: keyof typeof presets): AnimationPreset => {
  if (!presets[name]) {
    throw new Error(`Animation preset "${name}" not found`);
  }
  return presets[name];
};

export const getPresetsByTag = (tag: string): AnimationPreset[] => {
  return Object.values(presets).filter(preset => preset.tags.includes(tag));
};

export const getAllPresets = (): AnimationPreset[] => {
  return Object.values(presets);
}; 