// CharacterCustomization.test.ts
// Tests for character customization system

import {
  CharacterCustomizationManager,
  BodyType,
  SkinTone,
  HairStyle,
  HairColor,
  EyeType,
  EyeColor,
  MouthType,
  ClothingType,
  EquipmentType,
  CharacterCustomization,
} from '../CharacterCustomization';
import { CharacterSpriteLayerType } from '../CharacterSprite';

describe('CharacterCustomizationManager', () => {
  let manager: CharacterCustomizationManager;
  let baseCustomization: CharacterCustomization;

  beforeEach(() => {
    baseCustomization = {
      bodyType: BodyType.HumanMaleMedium,
      skinTone: SkinTone.Medium,
    };
    manager = new CharacterCustomizationManager(baseCustomization);
  });

  describe('constructor', () => {
    it('should initialize with base customization', () => {
      expect(manager.getCustomization()).toEqual(baseCustomization);
    });
  });

  describe('updateCustomization', () => {
    it('should update partial customization', () => {
      const update = {
        hair: {
          style: HairStyle.Short,
          color: HairColor.Brown,
        },
      };
      manager.updateCustomization(update);
      expect(manager.getCustomization()).toEqual({
        ...baseCustomization,
        ...update,
      });
    });

    it('should preserve existing customization when updating', () => {
      const firstUpdate = {
        hair: {
          style: HairStyle.Short,
          color: HairColor.Brown,
        },
      };
      const secondUpdate = {
        eyes: {
          type: EyeType.Round,
          color: EyeColor.Blue,
        },
      };
      manager.updateCustomization(firstUpdate);
      manager.updateCustomization(secondUpdate);
      expect(manager.getCustomization()).toEqual({
        ...baseCustomization,
        ...firstUpdate,
        ...secondUpdate,
      });
    });
  });

  describe('generateLayers', () => {
    it('should generate base layers with body only', () => {
      const layers = manager.generateLayers();
      expect(layers).toEqual([
        {
          type: CharacterSpriteLayerType.Body,
          variant: `${BodyType.HumanMaleMedium}_${SkinTone.Medium}`,
        },
      ]);
    });

    it('should generate all layers with full customization', () => {
      const fullCustomization: CharacterCustomization = {
        ...baseCustomization,
        hair: {
          style: HairStyle.Short,
          color: HairColor.Brown,
        },
        eyes: {
          type: EyeType.Round,
          color: EyeColor.Blue,
        },
        mouth: {
          type: MouthType.Smile,
        },
        clothing: {
          type: ClothingType.Armor,
          color: '#FF0000',
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
      manager.updateCustomization(fullCustomization);
      const layers = manager.generateLayers();

      expect(layers).toEqual([
        {
          type: CharacterSpriteLayerType.Body,
          variant: `${BodyType.HumanMaleMedium}_${SkinTone.Medium}`,
        },
        {
          type: CharacterSpriteLayerType.Hair,
          variant: HairStyle.Short,
          color: HairColor.Brown,
        },
        {
          type: CharacterSpriteLayerType.Eyes,
          variant: EyeType.Round,
          color: EyeColor.Blue,
        },
        {
          type: CharacterSpriteLayerType.Mouth,
          variant: MouthType.Smile,
        },
        {
          type: CharacterSpriteLayerType.Clothing,
          variant: ClothingType.Armor,
          color: '#FF0000',
        },
        {
          type: CharacterSpriteLayerType.Equipment,
          variant: EquipmentType.Sword,
          style: 'steel',
        },
        {
          type: CharacterSpriteLayerType.Equipment,
          variant: EquipmentType.Shield,
          style: 'round',
        },
      ]);
    });
  });

  describe('validateCustomization', () => {
    it('should validate required fields', () => {
      expect(manager.validateCustomization()).toBe(true);

      const invalidManager = new CharacterCustomizationManager({
        bodyType: BodyType.HumanMaleMedium,
        skinTone: undefined as unknown as SkinTone,
      });
      expect(invalidManager.validateCustomization()).toBe(false);
    });

    it('should validate optional fields when present', () => {
      manager.updateCustomization({
        hair: {
          style: undefined as unknown as HairStyle,
          color: HairColor.Brown,
        },
      });
      expect(manager.validateCustomization()).toBe(false);

      manager.updateCustomization({
        hair: {
          style: HairStyle.Short,
          color: HairColor.Brown,
        },
      });
      expect(manager.validateCustomization()).toBe(true);
    });

    it('should validate equipment array', () => {
      manager.updateCustomization({
        equipment: [
          {
            type: undefined as unknown as EquipmentType,
          },
        ],
      });
      expect(manager.validateCustomization()).toBe(false);

      manager.updateCustomization({
        equipment: [
          {
            type: EquipmentType.Sword,
            variant: 'steel',
          },
        ],
      });
      expect(manager.validateCustomization()).toBe(true);
    });
  });
});
