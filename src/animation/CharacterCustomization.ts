// CharacterCustomization.ts
// Manages character customization options and layer combinations

import { CharacterSpriteLayerType } from './CharacterSprite';

/**
 * Available body types for character customization.
 */
export enum BodyType {
  HumanMaleSlim = 'human_male_slim',
  HumanMaleMedium = 'human_male_medium',
  HumanMaleLarge = 'human_male_large',
  HumanFemaleSlim = 'human_female_slim',
  HumanFemaleMedium = 'human_female_medium',
  HumanFemaleLarge = 'human_female_large',
  // Add more body types as needed
}

/**
 * Available skin tones for character customization.
 */
export enum SkinTone {
  Light = 'light',
  Medium = 'medium',
  Dark = 'dark',
  // Add more skin tones as needed
}

/**
 * Available hair styles for character customization.
 */
export enum HairStyle {
  Short = 'short',
  Medium = 'medium',
  Long = 'long',
  Bald = 'bald',
  // Add more hair styles as needed
}

/**
 * Available hair colors for character customization.
 */
export enum HairColor {
  Black = 'black',
  Brown = 'brown',
  Blonde = 'blonde',
  Red = 'red',
  Gray = 'gray',
  White = 'white',
  // Add more hair colors as needed
}

/**
 * Available eye types for character customization.
 */
export enum EyeType {
  Round = 'round',
  Almond = 'almond',
  Narrow = 'narrow',
  // Add more eye types as needed
}

/**
 * Available eye colors for character customization.
 */
export enum EyeColor {
  Brown = 'brown',
  Blue = 'blue',
  Green = 'green',
  Hazel = 'hazel',
  Gray = 'gray',
  // Add more eye colors as needed
}

/**
 * Available mouth types for character customization.
 */
export enum MouthType {
  Neutral = 'neutral',
  Smile = 'smile',
  Frown = 'frown',
  // Add more mouth types as needed
}

/**
 * Available clothing types for character customization.
 */
export enum ClothingType {
  Shirt = 'shirt',
  Tunic = 'tunic',
  Robe = 'robe',
  Armor = 'armor',
  // Add more clothing types as needed
}

/**
 * Available equipment types for character customization.
 */
export enum EquipmentType {
  Sword = 'sword',
  Staff = 'staff',
  Bow = 'bow',
  Shield = 'shield',
  // Add more equipment types as needed
}

/**
 * Character customization options for a specific layer.
 */
export interface LayerCustomization {
  type: CharacterSpriteLayerType;
  variant: string;
  color?: string;
  style?: string;
}

/**
 * Complete character customization configuration.
 */
export interface CharacterCustomization {
  bodyType: BodyType;
  skinTone: SkinTone;
  hair?: {
    style: HairStyle;
    color: HairColor;
  };
  eyes?: {
    type: EyeType;
    color: EyeColor;
  };
  mouth?: {
    type: MouthType;
  };
  clothing?: {
    type: ClothingType;
    color: string;
  };
  equipment?: {
    type: EquipmentType;
    variant?: string;
  }[];
}

/**
 * Manages character customization and generates appropriate layer configurations.
 */
export class CharacterCustomizationManager {
  private customization: CharacterCustomization;

  constructor(initialCustomization: CharacterCustomization) {
    this.customization = initialCustomization;
  }

  /**
   * Update character customization options.
   */
  public updateCustomization(newCustomization: Partial<CharacterCustomization>): void {
    this.customization = {
      ...this.customization,
      ...newCustomization,
    };
  }

  /**
   * Get the current customization configuration.
   */
  public getCustomization(): CharacterCustomization {
    return { ...this.customization };
  }

  /**
   * Generate layer configurations based on current customization.
   */
  public generateLayers(): LayerCustomization[] {
    const layers: LayerCustomization[] = [];

    // Add body layer
    layers.push({
      type: CharacterSpriteLayerType.Body,
      variant: `${this.customization.bodyType}_${this.customization.skinTone}`,
    });

    // Add hair layer if configured
    if (this.customization.hair) {
      layers.push({
        type: CharacterSpriteLayerType.Hair,
        variant: this.customization.hair.style,
        color: this.customization.hair.color,
      });
    }

    // Add eyes layer if configured
    if (this.customization.eyes) {
      layers.push({
        type: CharacterSpriteLayerType.Eyes,
        variant: this.customization.eyes.type,
        color: this.customization.eyes.color,
      });
    }

    // Add mouth layer if configured
    if (this.customization.mouth) {
      layers.push({
        type: CharacterSpriteLayerType.Mouth,
        variant: this.customization.mouth.type,
      });
    }

    // Add clothing layer if configured
    if (this.customization.clothing) {
      layers.push({
        type: CharacterSpriteLayerType.Clothing,
        variant: this.customization.clothing.type,
        color: this.customization.clothing.color,
      });
    }

    // Add equipment layers if configured
    if (this.customization.equipment) {
      for (const equipment of this.customization.equipment) {
        layers.push({
          type: CharacterSpriteLayerType.Equipment,
          variant: equipment.type,
          style: equipment.variant,
        });
      }
    }

    return layers;
  }

  /**
   * Validate if the current customization is complete and valid.
   */
  public validateCustomization(): boolean {
    // Required fields
    if (!this.customization.bodyType || !this.customization.skinTone) {
      return false;
    }

    // Optional fields validation
    if (this.customization.hair) {
      if (!this.customization.hair.style || !this.customization.hair.color) {
        return false;
      }
    }

    if (this.customization.eyes) {
      if (!this.customization.eyes.type || !this.customization.eyes.color) {
        return false;
      }
    }

    if (this.customization.mouth && !this.customization.mouth.type) {
      return false;
    }

    if (this.customization.clothing) {
      if (!this.customization.clothing.type || !this.customization.clothing.color) {
        return false;
      }
    }

    if (this.customization.equipment) {
      for (const equipment of this.customization.equipment) {
        if (!equipment.type) {
          return false;
        }
      }
    }

    return true;
  }
}

export default CharacterCustomizationManager;
