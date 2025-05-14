from typing import Any, List



/**
 * Metadata for a single sprite asset (layer variant or animation frame).
 */
class CharacterAssetMeta:
    /** Path to the asset image (sprite or sheet) */
  path: str
    /** Number of animation frames (if sprite sheet) */
  frames: float
    /** Optional tags for filtering (e.g., color, style, gender) */
  tags?: List[str]
    /** Optional display name for UI */
  name?: str
    /** Optional z-order override */
  z?: float
/**
 * Asset index for all character sprite layers and variants.
 * Maps layer type -> feature/equipment name -> array of asset metadata.
 */
CharacterAssetIndex = List[{
  [layer in CharacterSpriteLayerType]?: {
    [variant: str]: CharacterAssetMeta]
  }
}
/**
 * Example asset index for body, hair, clothing, equipment, etc.
 * Extend as needed for all features and variants.
 */
const characterAssetIndex: CharacterAssetIndex = {
  [CharacterSpriteLayerType.Body]: {
    human_male: [
      {
        path: 'assets/body/human_male_idle.png',
        frames: 3,
        tags: ['idle', 'light'],
        name: 'Human Male Idle',
        z: 0,
      },
      {
        path: 'assets/body/human_male_walk.png',
        frames: 3,
        tags: ['walk', 'light'],
        name: 'Human Male Walk',
        z: 0,
      },
    ],
    human_female: [
      {
        path: 'assets/body/human_female_idle.png',
        frames: 3,
        tags: ['idle', 'light'],
        name: 'Human Female Idle',
        z: 0,
      },
      {
        path: 'assets/body/human_female_walk.png',
        frames: 3,
        tags: ['walk', 'light'],
        name: 'Human Female Walk',
        z: 0,
      },
    ],
  },
  [CharacterSpriteLayerType.Hair]: {
    short_blonde: [
      {
        path: 'assets/hair/short_blonde_idle.png',
        frames: 3,
        tags: ['idle', 'blonde'],
        name: 'Short Blonde Hair',
        z: 1,
      },
      {
        path: 'assets/hair/short_blonde_walk.png',
        frames: 3,
        tags: ['walk', 'blonde'],
        name: 'Short Blonde Hair Walk',
        z: 1,
      },
    ],
    long_black: [
      {
        path: 'assets/hair/long_black_idle.png',
        frames: 3,
        tags: ['idle', 'black'],
        name: 'Long Black Hair',
        z: 1,
      },
      {
        path: 'assets/hair/long_black_walk.png',
        frames: 3,
        tags: ['walk', 'black'],
        name: 'Long Black Hair Walk',
        z: 1,
      },
    ],
  },
  [CharacterSpriteLayerType.Clothing]: {
    shirt_red: [
      {
        path: 'assets/clothing/shirt_red_idle.png',
        frames: 3,
        tags: ['idle', 'red'],
        name: 'Red Shirt',
        z: 2,
      },
      {
        path: 'assets/clothing/shirt_red_walk.png',
        frames: 3,
        tags: ['walk', 'red'],
        name: 'Red Shirt Walk',
        z: 2,
      },
    ],
    armor_leather: [
      {
        path: 'assets/clothing/armor_leather_idle.png',
        frames: 3,
        tags: ['idle', 'leather'],
        name: 'Leather Armor',
        z: 2,
      },
      {
        path: 'assets/clothing/armor_leather_walk.png',
        frames: 3,
        tags: ['walk', 'leather'],
        name: 'Leather Armor Walk',
        z: 2,
      },
    ],
  },
  [CharacterSpriteLayerType.Equipment]: {
    sword: [
      {
        path: 'assets/equipment/sword_idle.png',
        frames: 3,
        tags: ['idle', 'sword'],
        name: 'Sword',
        z: 3,
      },
      {
        path: 'assets/equipment/sword_attack.png',
        frames: 3,
        tags: ['attack', 'sword'],
        name: 'Sword Attack',
        z: 3,
      },
    ],
    staff: [
      {
        path: 'assets/equipment/staff_idle.png',
        frames: 3,
        tags: ['idle', 'staff'],
        name: 'Staff',
        z: 3,
      },
      {
        path: 'assets/equipment/staff_cast.png',
        frames: 3,
        tags: ['cast', 'staff'],
        name: 'Staff Cast',
        z: 3,
      },
    ],
  },
}