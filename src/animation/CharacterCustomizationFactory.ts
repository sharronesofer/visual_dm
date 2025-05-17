// CharacterCustomizationFactory.ts
// Factory for creating character customizations with preset configurations

import {
  CharacterCustomization,
  BodyType,
  SkinTone,
  HairStyle,
  HairColor,
  EyeType,
  EyeColor,
  MouthType,
  ClothingType,
  EquipmentType,
  ExtendedCharacterCustomization,
  MeshSlot,
  BlendShapeConfig,
  MaterialAssignment,
} from './CharacterCustomization';

/**
 * Factory class for creating character customizations with preset configurations.
 */
export class CharacterCustomizationFactory {
  /**
   * Create a basic human male character customization.
   */
  public static createBasicHumanMale(skinTone: SkinTone = SkinTone.Medium): CharacterCustomization {
    return {
      bodyType: BodyType.HumanMaleMedium,
      skinTone,
      hair: {
        style: HairStyle.Short,
        color: HairColor.Brown,
      },
      eyes: {
        type: EyeType.Round,
        color: EyeColor.Brown,
      },
      mouth: {
        type: MouthType.Neutral,
      },
      clothing: {
        type: ClothingType.Shirt,
        color: '#2244AA', // Navy blue
      },
    };
  }

  /**
   * Create a basic human female character customization.
   */
  public static createBasicHumanFemale(
    skinTone: SkinTone = SkinTone.Medium
  ): CharacterCustomization {
    return {
      bodyType: BodyType.HumanFemaleMedium,
      skinTone,
      hair: {
        style: HairStyle.Medium,
        color: HairColor.Brown,
      },
      eyes: {
        type: EyeType.Almond,
        color: EyeColor.Brown,
      },
      mouth: {
        type: MouthType.Neutral,
      },
      clothing: {
        type: ClothingType.Shirt,
        color: '#AA2244', // Burgundy
      },
    };
  }

  /**
   * Create a warrior character customization.
   */
  public static createWarrior(
    bodyType: BodyType = BodyType.HumanMaleMedium,
    skinTone: SkinTone = SkinTone.Medium
  ): CharacterCustomization {
    return {
      bodyType,
      skinTone,
      hair: {
        style: HairStyle.Short,
        color: HairColor.Black,
      },
      eyes: {
        type: EyeType.Round,
        color: EyeColor.Brown,
      },
      mouth: {
        type: MouthType.Neutral,
      },
      clothing: {
        type: ClothingType.Armor,
        color: '#888888', // Steel gray
      },
      equipment: [
        {
          type: EquipmentType.Sword,
          variant: 'steel',
        },
        {
          type: EquipmentType.Shield,
          variant: 'round',
        },
      ],
    };
  }

  /**
   * Create a mage character customization.
   */
  public static createMage(
    bodyType: BodyType = BodyType.HumanMaleMedium,
    skinTone: SkinTone = SkinTone.Medium
  ): CharacterCustomization {
    return {
      bodyType,
      skinTone,
      hair: {
        style: HairStyle.Long,
        color: HairColor.Gray,
      },
      eyes: {
        type: EyeType.Almond,
        color: EyeColor.Blue,
      },
      mouth: {
        type: MouthType.Neutral,
      },
      clothing: {
        type: ClothingType.Robe,
        color: '#4422AA', // Deep purple
      },
      equipment: [
        {
          type: EquipmentType.Staff,
          variant: 'wooden',
        },
      ],
    };
  }

  /**
   * Create an archer character customization.
   */
  public static createArcher(
    bodyType: BodyType = BodyType.HumanFemaleMedium,
    skinTone: SkinTone = SkinTone.Medium
  ): CharacterCustomization {
    return {
      bodyType,
      skinTone,
      hair: {
        style: HairStyle.Long,
        color: HairColor.Brown,
      },
      eyes: {
        type: EyeType.Almond,
        color: EyeColor.Green,
      },
      mouth: {
        type: MouthType.Neutral,
      },
      clothing: {
        type: ClothingType.Tunic,
        color: '#225522', // Forest green
      },
      equipment: [
        {
          type: EquipmentType.Bow,
          variant: 'longbow',
        },
      ],
    };
  }

  /**
   * Create a random character customization.
   */
  public static createRandom(): CharacterCustomization {
    const bodyTypes = Object.values(BodyType);
    const skinTones = Object.values(SkinTone);
    const hairStyles = Object.values(HairStyle);
    const hairColors = Object.values(HairColor);
    const eyeTypes = Object.values(EyeType);
    const eyeColors = Object.values(EyeColor);
    const mouthTypes = Object.values(MouthType);
    const clothingTypes = Object.values(ClothingType);
    const equipmentTypes = Object.values(EquipmentType);

    const randomElement = <T>(array: T[]): T => array[Math.floor(Math.random() * array.length)];
    const randomColor = (): string =>
      `#${Math.floor(Math.random() * 16777215)
        .toString(16)
        .padStart(6, '0')}`;

    return {
      bodyType: randomElement(bodyTypes),
      skinTone: randomElement(skinTones),
      hair: {
        style: randomElement(hairStyles),
        color: randomElement(hairColors),
      },
      eyes: {
        type: randomElement(eyeTypes),
        color: randomElement(eyeColors),
      },
      mouth: {
        type: randomElement(mouthTypes),
      },
      clothing: {
        type: randomElement(clothingTypes),
        color: randomColor(),
      },
      equipment:
        Math.random() > 0.5
          ? [
            {
              type: randomElement(equipmentTypes),
              variant: 'basic',
            },
          ]
          : undefined,
    };
  }
}

/**
 * Factory method for creating a modular/mesh-based character (e.g., Dwarf Warrior).
 * Demonstrates use of meshSlots, blendShapes, materials, and scale.
 */
export class ModularCharacterCustomizationFactory extends CharacterCustomizationFactory {
  /**
   * Create a modular dwarf warrior character with unique scaling and mesh slots.
   */
  public static createDwarfWarrior(): ExtendedCharacterCustomization {
    const meshSlots: MeshSlot[] = [
      {
        slot: 'body',
        meshAsset: 'assets/meshes/dwarf_body.glb',
        material: 'skin',
        scale: { x: 0.85, y: 0.85, z: 0.85 },
      },
      {
        slot: 'head',
        meshAsset: 'assets/meshes/dwarf_head.glb',
        material: 'skin',
      },
      {
        slot: 'beard',
        meshAsset: 'assets/meshes/dwarf_beard_long.glb',
        material: 'hair',
      },
      {
        slot: 'hair',
        meshAsset: 'assets/meshes/dwarf_hair_short.glb',
        material: 'hair',
      },
      {
        slot: 'armor',
        meshAsset: 'assets/meshes/dwarf_armor_heavy.glb',
        material: 'armor',
      },
      {
        slot: 'weapon',
        meshAsset: 'assets/meshes/dwarf_axe.glb',
        material: 'metal',
      },
    ];
    const blendShapes: BlendShapeConfig[] = [
      { name: 'jawWidth', value: 0.7 },
      { name: 'browDepth', value: 0.5 },
      { name: 'noseSize', value: 0.6 },
    ];
    const materials: MaterialAssignment[] = [
      { materialKey: 'skin', color: '#b08d57' },
      { materialKey: 'hair', color: '#6b3e26' },
      { materialKey: 'armor', color: '#888888', metallic: 0.8, roughness: 0.3 },
      { materialKey: 'metal', color: '#cccccc', metallic: 1.0, roughness: 0.2 },
    ];
    const scale = { x: 0.85, y: 0.85, z: 0.85 };
    return {
      bodyType: BodyType.HumanMaleLarge, // Closest base type for compatibility
      skinTone: SkinTone.Medium,
      hair: {
        style: HairStyle.Short,
        color: HairColor.Brown,
      },
      eyes: {
        type: EyeType.Round,
        color: EyeColor.Brown,
      },
      mouth: {
        type: MouthType.Neutral,
      },
      clothing: {
        type: ClothingType.Armor,
        color: '#888888',
      },
      equipment: [
        {
          type: EquipmentType.Sword,
          variant: 'axe',
        },
      ],
      meshSlots,
      blendShapes,
      materials,
      scale,
    };
  }

  /**
   * Create a modular character with a full layered armor set, demonstrating armor layering, z-order, and material variety.
   */
  public static createLayeredArmorSet(): ExtendedCharacterCustomization {
    const meshSlots: MeshSlot[] = [
      {
        slot: 'helmet',
        meshAsset: 'assets/meshes/armor_helmet.glb',
        material: 'armor_helmet',
        armorSlot: 'helmet',
        zOrder: 10,
      },
      {
        slot: 'chest',
        meshAsset: 'assets/meshes/armor_chest.glb',
        material: 'armor_chest',
        armorSlot: 'chest',
        zOrder: 20,
      },
      {
        slot: 'shoulders',
        meshAsset: 'assets/meshes/armor_shoulders.glb',
        material: 'armor_shoulders',
        armorSlot: 'shoulders',
        zOrder: 30,
      },
      {
        slot: 'legs',
        meshAsset: 'assets/meshes/armor_legs.glb',
        material: 'armor_legs',
        armorSlot: 'legs',
        zOrder: 40,
      },
      {
        slot: 'boots',
        meshAsset: 'assets/meshes/armor_boots.glb',
        material: 'armor_boots',
        armorSlot: 'boots',
        zOrder: 50,
      },
      {
        slot: 'gloves',
        meshAsset: 'assets/meshes/armor_gloves.glb',
        material: 'armor_gloves',
        armorSlot: 'gloves',
        zOrder: 60,
      },
    ];
    const materials: MaterialAssignment[] = [
      { materialKey: 'armor_helmet', color: '#cccccc', metallic: 1.0, roughness: 0.2, preset: 'steel' },
      { materialKey: 'armor_chest', color: '#888888', metallic: 0.9, roughness: 0.3, preset: 'steel' },
      { materialKey: 'armor_shoulders', color: '#b08d57', metallic: 0.7, roughness: 0.4, preset: 'bronze' },
      { materialKey: 'armor_legs', color: '#a0522d', metallic: 0.3, roughness: 0.6, preset: 'leather' },
      { materialKey: 'armor_boots', color: '#654321', metallic: 0.2, roughness: 0.7, preset: 'leather' },
      { materialKey: 'armor_gloves', color: '#654321', metallic: 0.2, roughness: 0.7, preset: 'leather' },
    ];
    return {
      bodyType: BodyType.HumanMaleMedium,
      skinTone: SkinTone.Light,
      meshSlots,
      materials,
      scale: { x: 1, y: 1, z: 1 },
    };
  }
}

export default CharacterCustomizationFactory;
