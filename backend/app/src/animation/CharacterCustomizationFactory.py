from typing import Any, Dict, List


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
} from './CharacterCustomization'
/**
 * Factory class for creating character customizations with preset configurations.
 */
class CharacterCustomizationFactory {
  /**
   * Create a basic human male character customization.
   */
  public static createBasicHumanMale(skinTone: SkinTone = SkinTone.Medium): CharacterCustomization {
    return {
      bodyType: BodyType.HumanMaleMedium,
      skinTone,
      hair: Dict[str, Any],
      eyes: Dict[str, Any],
      mouth: Dict[str, Any],
      clothing: Dict[str, Any],
    }
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
      hair: Dict[str, Any],
      eyes: Dict[str, Any],
      mouth: Dict[str, Any],
      clothing: Dict[str, Any],
    }
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
      hair: Dict[str, Any],
      eyes: Dict[str, Any],
      mouth: Dict[str, Any],
      clothing: Dict[str, Any],
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
    }
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
      hair: Dict[str, Any],
      eyes: Dict[str, Any],
      mouth: Dict[str, Any],
      clothing: Dict[str, Any],
      equipment: [
        {
          type: EquipmentType.Staff,
          variant: 'wooden',
        },
      ],
    }
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
      hair: Dict[str, Any],
      eyes: Dict[str, Any],
      mouth: Dict[str, Any],
      clothing: Dict[str, Any],
      equipment: [
        {
          type: EquipmentType.Bow,
          variant: 'longbow',
        },
      ],
    }
  }
  /**
   * Create a random character customization.
   */
  public static createRandom(): CharacterCustomization {
    const bodyTypes = Object.values(BodyType)
    const skinTones = Object.values(SkinTone)
    const hairStyles = Object.values(HairStyle)
    const hairColors = Object.values(HairColor)
    const eyeTypes = Object.values(EyeType)
    const eyeColors = Object.values(EyeColor)
    const mouthTypes = Object.values(MouthType)
    const clothingTypes = Object.values(ClothingType)
    const equipmentTypes = Object.values(EquipmentType)
    const randomElement = <T>(array: List[T]): T => array[Math.floor(Math.random() * array.length)]
    const randomColor = (): str =>
      `#${Math.floor(Math.random() * 16777215)
        .toString(16)
        .padStart(6, '0')}`
    return {
      bodyType: randomElement(bodyTypes),
      skinTone: randomElement(skinTones),
      hair: Dict[str, Any],
      eyes: Dict[str, Any],
      mouth: Dict[str, Any],
      clothing: Dict[str, Any],
      equipment:
        Math.random() > 0.5
          ? [
              {
                type: randomElement(equipmentTypes),
                variant: 'basic',
              },
            ]
          : undefined,
    }
  }
}
default CharacterCustomizationFactory