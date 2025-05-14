export interface AnimationFrame {
  image: HTMLImageElement;
  duration: number; // ms
}

export interface AnimationSet {
  name: string;
  frames: AnimationFrame[];
  loop: boolean;
}

export interface SharedSpriteFormat {
  id: string;
  anchor: { x: number; y: number };
  animationSets: AnimationSet[];
  width: number;
  height: number;
  meta?: Record<string, any>;
}

export function validateSpriteFormat(sprite: any): sprite is SharedSpriteFormat {
  return (
    typeof sprite.id === 'string' &&
    typeof sprite.anchor === 'object' &&
    Array.isArray(sprite.animationSets) &&
    typeof sprite.width === 'number' &&
    typeof sprite.height === 'number'
  );
} 