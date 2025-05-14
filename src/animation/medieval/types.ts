export type AnimationLayer = 'foreground' | 'background';

export type PageTransitionType = 
  | 'fade' 
  | 'slide' 
  | 'page-turn'
  | 'scroll'
  | 'ink'
  | 'ambient'
  | 'dissolve';

export type AnimationValue = number | [number, number];

export type AnimationTiming = {
  duration: number;
  delay?: number;
  easing: string;
};

export type AmbientEffect = 
  | 'dust'          // Floating dust particles
  | 'candleLight'   // Flickering candle effect
  | 'parchmentWave' // Subtle parchment movement
  | 'inkDrip'       // Occasional ink drips
  | 'none';

export interface LayerConfig {
  opacity: AnimationValue;
  scale?: AnimationValue;
  rotation?: AnimationValue;
  blur?: AnimationValue;
  transformOrigin?: string;
}

export interface AnimationConfig {
  type: PageTransitionType;
  timing: AnimationTiming;
  layers: {
    foreground: LayerConfig;
    background?: LayerConfig;
  };
  ambientEffects?: {
    particles?: boolean;
    lighting?: boolean;
    sound?: boolean;
  };
}

export interface AnimationState {
  isAnimating: boolean;
  progress: number;
  currentType: PageTransitionType;
  direction: 'forward' | 'backward';
  layers: {
    foreground: LayerConfig;
    background?: LayerConfig;
  };
  config?: AnimationConfig;
}

export interface AnimationEventHandlers {
  onStart?: () => void;
  onUpdate?: (progress: number) => void;
  onComplete?: () => void;
  onCancel?: () => void;
}

export interface AnimationController {
  play: (config: AnimationConfig) => Promise<void>;
  pause: () => void;
  resume: () => void;
  cancel: () => void;
  reverse: () => void;
  getState: () => AnimationState;
}

export type AnimationPreset = {
  name: string;
  config: AnimationConfig;
  description: string;
  tags: string[];
}; 