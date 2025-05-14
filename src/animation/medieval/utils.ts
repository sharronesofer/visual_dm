import { AnimationState } from './types';

// Asset paths for medieval textures
export const medievalTextures = {
  dust: '/assets/textures/dust.png',
  parchment: '/assets/textures/parchment-normal.png',
  inkDrips: '/assets/textures/ink-drips.png',
  candleLight: '/assets/textures/candle-light.png',
  paperEdge: '/assets/textures/paper-edge.png'
} as const;

// Performance metrics interface
export interface PerformanceMetrics {
  fps: number;
  duration: number;
  droppedFrames: number;
  averageFps: number;
  fpsHistory: number[];
  lastFrameTime: number;
}

// Default performance thresholds
export const performanceThresholds = {
  minFps: 30,
  targetFps: 60,
  maxDroppedFrames: 5,
  historySize: 60, // 1 second at 60fps
  warningThreshold: 45
};

/**
 * Preload medieval textures to prevent visual glitches
 * @returns Promise that resolves when all textures are loaded
 */
export const preloadMedievalTextures = async (): Promise<void> => {
  const loadTexture = (url: string): Promise<void> => {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => resolve();
      img.onerror = () => {
        console.warn(`Failed to load texture: ${url}`);
        resolve(); // Resolve anyway to prevent blocking
      };
      img.src = url;
    });
  };

  try {
    await Promise.all(Object.values(medievalTextures).map(loadTexture));
    console.debug('Medieval textures preloaded successfully');
  } catch (error) {
    console.error('Error preloading textures:', error);
  }
};

/**
 * Initialize performance monitoring for medieval animations
 */
export const createPerformanceMonitor = () => {
  const metrics: PerformanceMetrics = {
    fps: 0,
    duration: 0,
    droppedFrames: 0,
    averageFps: 0,
    fpsHistory: [],
    lastFrameTime: 0
  };

  const updateMetrics = (currentTime: number) => {
    if (metrics.lastFrameTime === 0) {
      metrics.lastFrameTime = currentTime;
      return metrics;
    }

    // Calculate FPS
    const timeDelta = currentTime - metrics.lastFrameTime;
    const currentFps = 1000 / timeDelta;

    // Update FPS history
    metrics.fpsHistory.push(currentFps);
    if (metrics.fpsHistory.length > performanceThresholds.historySize) {
      metrics.fpsHistory.shift();
    }

    // Calculate average FPS
    metrics.averageFps = metrics.fpsHistory.reduce((a, b) => a + b, 0) / metrics.fpsHistory.length;

    // Count dropped frames
    if (currentFps < performanceThresholds.minFps) {
      metrics.droppedFrames++;
    }

    // Update metrics
    metrics.fps = currentFps;
    metrics.lastFrameTime = currentTime;
    metrics.duration += timeDelta;

    return metrics;
  };

  const logPerformanceWarning = (metrics: PerformanceMetrics) => {
    if (metrics.averageFps < performanceThresholds.warningThreshold) {
      console.warn('Medieval Animation Performance Warning:', {
        averageFps: metrics.averageFps.toFixed(2),
        droppedFrames: metrics.droppedFrames,
        duration: metrics.duration.toFixed(2) + 'ms'
      });
    }
  };

  return {
    updateMetrics,
    logPerformanceWarning,
    getMetrics: () => ({ ...metrics }),
    reset: () => {
      metrics.fps = 0;
      metrics.duration = 0;
      metrics.droppedFrames = 0;
      metrics.averageFps = 0;
      metrics.fpsHistory = [];
      metrics.lastFrameTime = 0;
    }
  };
};

/**
 * Check if the device should use reduced animations
 */
export const shouldUseReducedAnimations = (): boolean => {
  // Check for reduced motion preference
  if (typeof window !== 'undefined' && window.matchMedia) {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      return true;
    }
  }

  // Check for mobile devices
  const isMobile = typeof window !== 'undefined' && 
    /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);

  // Check for low-end devices (rough estimation)
  const isLowEnd = typeof navigator !== 'undefined' && 
    navigator.hardwareConcurrency !== undefined && 
    navigator.hardwareConcurrency <= 4;

  return isMobile || isLowEnd;
};

/**
 * Get optimized animation config based on device capabilities
 */
export const getOptimizedAnimationConfig = (state: AnimationState) => {
  if (shouldUseReducedAnimations()) {
    return {
      ...state,
      layers: {
        foreground: {
          ...state.layers.foreground,
          blur: undefined, // Disable blur effects
          scale: Math.min(state.layers.foreground.scale || 1, 1.1) // Limit scale
        },
        background: {
          ...state.layers.background,
          blur: undefined, // Disable blur effects
          scale: Math.min(state.layers.background.scale || 1, 1.1) // Limit scale
        }
      }
    };
  }
  return state;
}; 