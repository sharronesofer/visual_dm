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

export default CharacterCustomizationFactory;
