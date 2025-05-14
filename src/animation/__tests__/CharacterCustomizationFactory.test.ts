// CharacterCustomizationFactory.test.ts
// Tests for character customization factory

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
} from '../CharacterCustomization';
import { CharacterCustomizationFactory } from '../CharacterCustomizationFactory';

describe('CharacterCustomizationFactory', () => {
  describe('createBasicHumanMale', () => {
    it('should create basic male customization with default skin tone', () => {
      const customization =
        CharacterCustomizationFactory.createBasicHumanMale();
      expect(customization).toEqual({
        bodyType: BodyType.HumanMaleMedium,
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
          type: ClothingType.Shirt,
          color: '#2244AA',
        },
      });
    });

    it('should create basic male customization with specified skin tone', () => {
      const customization = CharacterCustomizationFactory.createBasicHumanMale(
        SkinTone.Dark
      );
      expect(customization.skinTone).toBe(SkinTone.Dark);
    });
  });

  describe('createBasicHumanFemale', () => {
    it('should create basic female customization with default skin tone', () => {
      const customization =
        CharacterCustomizationFactory.createBasicHumanFemale();
      expect(customization).toEqual({
        bodyType: BodyType.HumanFemaleMedium,
        skinTone: SkinTone.Medium,
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
          color: '#AA2244',
        },
      });
    });

    it('should create basic female customization with specified skin tone', () => {
      const customization =
        CharacterCustomizationFactory.createBasicHumanFemale(SkinTone.Light);
      expect(customization.skinTone).toBe(SkinTone.Light);
    });
  });

  describe('createWarrior', () => {
    it('should create warrior customization with default parameters', () => {
      const customization = CharacterCustomizationFactory.createWarrior();
      expect(customization).toEqual({
        bodyType: BodyType.HumanMaleMedium,
        skinTone: SkinTone.Medium,
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
          color: '#888888',
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
      });
    });

    it('should create warrior customization with specified parameters', () => {
      const customization = CharacterCustomizationFactory.createWarrior(
        BodyType.HumanFemaleMedium,
        SkinTone.Dark
      );
      expect(customization.bodyType).toBe(BodyType.HumanFemaleMedium);
      expect(customization.skinTone).toBe(SkinTone.Dark);
    });
  });

  describe('createMage', () => {
    it('should create mage customization with default parameters', () => {
      const customization = CharacterCustomizationFactory.createMage();
      expect(customization).toEqual({
        bodyType: BodyType.HumanMaleMedium,
        skinTone: SkinTone.Medium,
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
          color: '#4422AA',
        },
        equipment: [
          {
            type: EquipmentType.Staff,
            variant: 'wooden',
          },
        ],
      });
    });

    it('should create mage customization with specified parameters', () => {
      const customization = CharacterCustomizationFactory.createMage(
        BodyType.HumanFemaleMedium,
        SkinTone.Light
      );
      expect(customization.bodyType).toBe(BodyType.HumanFemaleMedium);
      expect(customization.skinTone).toBe(SkinTone.Light);
    });
  });

  describe('createArcher', () => {
    it('should create archer customization with default parameters', () => {
      const customization = CharacterCustomizationFactory.createArcher();
      expect(customization).toEqual({
        bodyType: BodyType.HumanFemaleMedium,
        skinTone: SkinTone.Medium,
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
          color: '#225522',
        },
        equipment: [
          {
            type: EquipmentType.Bow,
            variant: 'longbow',
          },
        ],
      });
    });

    it('should create archer customization with specified parameters', () => {
      const customization = CharacterCustomizationFactory.createArcher(
        BodyType.HumanMaleMedium,
        SkinTone.Dark
      );
      expect(customization.bodyType).toBe(BodyType.HumanMaleMedium);
      expect(customization.skinTone).toBe(SkinTone.Dark);
    });
  });

  describe('createRandom', () => {
    it('should create valid random customization', () => {
      const customization = CharacterCustomizationFactory.createRandom();

      // Check required fields
      expect(Object.values(BodyType)).toContain(customization.bodyType);
      expect(Object.values(SkinTone)).toContain(customization.skinTone);

      // Check hair
      expect(Object.values(HairStyle)).toContain(customization.hair?.style);
      expect(Object.values(HairColor)).toContain(customization.hair?.color);

      // Check eyes
      expect(Object.values(EyeType)).toContain(customization.eyes?.type);
      expect(Object.values(EyeColor)).toContain(customization.eyes?.color);

      // Check mouth
      expect(Object.values(MouthType)).toContain(customization.mouth?.type);

      // Check clothing
      expect(Object.values(ClothingType)).toContain(
        customization.clothing?.type
      );
      expect(customization.clothing?.color).toMatch(/^#[0-9A-F]{6}$/i);

      // Check equipment if present
      if (customization.equipment) {
        expect(customization.equipment.length).toBe(1);
        expect(Object.values(EquipmentType)).toContain(
          customization.equipment[0].type
        );
        expect(customization.equipment[0].variant).toBe('basic');
      }
    });

    it('should create different customizations on multiple calls', () => {
      const customizations = new Set();
      for (let i = 0; i < 10; i++) {
        const customization = CharacterCustomizationFactory.createRandom();
        customizations.add(JSON.stringify(customization));
      }
      expect(customizations.size).toBeGreaterThan(1);
    });
  });
});
