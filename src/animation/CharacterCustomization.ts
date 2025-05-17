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

/**
 * Mesh slot for modular character model parts (for 3D/2D hybrid or future 3D support).
 * Each slot represents a swappable mesh (e.g., head, body, hair, beard, armor, etc.).
 */
export interface MeshSlot {
  slot: string; // e.g., 'head', 'body', 'hair', 'beard', 'armor', etc.
  meshAsset: string; // Path or key to mesh asset (FBX, glTF, or 2D sprite sheet)
  material?: string; // Material assignment key
  blendShapes?: BlendShapeConfig[]; // Optional blend shape/morph target adjustments
  scale?: { x: number; y: number; z: number }; // Optional per-slot scaling
  // Armor-specific metadata:
  armorSlot?: 'helmet' | 'chest' | 'legs' | 'boots' | 'gloves' | 'shoulders' | 'belt' | 'bracers' | string; // If this is an armor piece
  zOrder?: number; // Explicit draw order for layering
}

/**
 * Blend shape (morph target) configuration for facial/body feature adjustment.
 */
export interface BlendShapeConfig {
  name: string; // e.g., 'jawWidth', 'noseHeight', 'browDepth', etc.
  value: number; // Range: typically 0.0 - 1.0
}

/**
 * Material assignment for dynamic skin tone, armor color, etc.
 */
export interface MaterialAssignment {
  materialKey: string; // e.g., 'skin', 'armor', 'hair', etc.
  color?: string; // Hex or RGBA string
  texture?: string; // Optional texture override
  metallic?: number; // 0-1 for PBR
  roughness?: number; // 0-1 for PBR
  // Armor-specific metadata:
  preset?: 'steel' | 'leather' | 'cloth' | 'gold' | 'bronze' | string; // Material preset for armor
}

/**
 * Extended character customization configuration for modular/mesh-based system.
 * Backward compatible with existing sprite/layer system.
 */
export interface ExtendedCharacterCustomization extends CharacterCustomization {
  meshSlots?: MeshSlot[]; // Modular mesh slots for 3D/2D hybrid
  blendShapes?: BlendShapeConfig[]; // Global blend shapes (applied to base mesh)
  materials?: MaterialAssignment[]; // Dynamic material assignments
  scale?: { x: number; y: number; z: number }; // Global scaling (for race/size differences)
}

/**
 * Extended manager for modular/mesh-based character customization.
 * Wraps and extends CharacterCustomizationManager.
 */
export class ModularCharacterCustomizationManager extends CharacterCustomizationManager {
  private meshSlots: MeshSlot[] = [];
  private blendShapes: BlendShapeConfig[] = [];
  private materials: MaterialAssignment[] = [];
  private globalScale: { x: number; y: number; z: number } = { x: 1, y: 1, z: 1 };

  constructor(initialCustomization: ExtendedCharacterCustomization) {
    super(initialCustomization);
    if (initialCustomization.meshSlots) this.meshSlots = initialCustomization.meshSlots;
    if (initialCustomization.blendShapes) this.blendShapes = initialCustomization.blendShapes;
    if (initialCustomization.materials) this.materials = initialCustomization.materials;
    if (initialCustomization.scale) this.globalScale = initialCustomization.scale;
  }

  /**
   * Update mesh slots (for runtime mesh swapping).
   */
  public updateMeshSlots(slots: MeshSlot[]): void {
    this.meshSlots = slots;
  }

  /**
   * Update blend shapes (for facial/body morphs).
   */
  public updateBlendShapes(blendShapes: BlendShapeConfig[]): void {
    this.blendShapes = blendShapes;
  }

  /**
   * Update material assignments (for skin tone, armor color, etc.).
   */
  public updateMaterials(materials: MaterialAssignment[]): void {
    this.materials = materials;
  }

  /**
   * Update global scale (for race/size differences).
   */
  public updateGlobalScale(scale: { x: number; y: number; z: number }): void {
    this.globalScale = scale;
  }

  /**
   * Get current mesh slots.
   */
  public getMeshSlots(): MeshSlot[] {
    return [...this.meshSlots];
  }

  /**
   * Get current blend shapes.
   */
  public getBlendShapes(): BlendShapeConfig[] {
    return [...this.blendShapes];
  }

  /**
   * Get current material assignments.
   */
  public getMaterials(): MaterialAssignment[] {
    return [...this.materials];
  }

  /**
   * Get current global scale.
   */
  public getGlobalScale(): { x: number; y: number; z: number } {
    return { ...this.globalScale };
  }

  /**
   * Generate a full modular character configuration (for rendering/serialization).
   */
  public generateModularConfig(): ExtendedCharacterCustomization {
    return {
      ...this.getCustomization(),
      meshSlots: this.getMeshSlots(),
      blendShapes: this.getBlendShapes(),
      materials: this.getMaterials(),
      scale: this.getGlobalScale(),
    };
  }
}

/**
 * Serialization utilities for ExtendedCharacterCustomization.
 */
export const CHARACTER_CUSTOMIZATION_VERSION = 1;

export class ExtendedCharacterCustomizationSerializer {
  /**
   * Serialize an ExtendedCharacterCustomization object to JSON, including version.
   */
  static serialize(
    customization: ExtendedCharacterCustomization,
    options?: { diffFrom?: Partial<ExtendedCharacterCustomization> }
  ): string {
    const data: any = {
      ...customization,
      __version: CHARACTER_CUSTOMIZATION_VERSION,
    };
    if (options?.diffFrom) {
      // Only include fields that differ from diffFrom
      for (const key of Object.keys(data)) {
        if (JSON.stringify(data[key]) === JSON.stringify((options.diffFrom as any)[key])) {
          delete data[key];
        }
      }
      data.__diff = true;
    }
    return JSON.stringify(data);
  }

  /**
   * Deserialize from JSON, handling versioning and unknown fields.
   */
  static deserialize(json: string): ExtendedCharacterCustomization {
    const data = JSON.parse(json);
    // Handle versioning/migration here if needed
    if (!data.__version) {
      // Assume v1 if missing
      data.__version = 1;
    }
    // Remove metadata fields
    delete data.__version;
    delete data.__diff;
    // Ignore unknown fields for forward compatibility
    return data as ExtendedCharacterCustomization;
  }
}

export default CharacterCustomizationManager;
