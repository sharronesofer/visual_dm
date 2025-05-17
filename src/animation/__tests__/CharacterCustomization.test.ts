/// <reference types="vitest" />
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
  ModularCharacterCustomizationManager,
  ExtendedCharacterCustomization,
} from '../CharacterCustomization';
import { CharacterSpriteLayerType } from '../CharacterSprite';
import { ModularCharacterCustomizationFactory } from '../CharacterCustomizationFactory';
import { ExtendedCharacterCustomizationSerializer } from '../CharacterCustomization';
import { RandomCharacterGenerator, RandomizationProfile } from '../RandomCharacterGenerator';

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
      expect(manager.getCustomization()).to.deep.equal(baseCustomization);
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
      expect(manager.getCustomization()).to.deep.equal({
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
      expect(manager.getCustomization()).to.deep.equal({
        ...baseCustomization,
        ...firstUpdate,
        ...secondUpdate,
      });
    });
  });

  describe('generateLayers', () => {
    it('should generate base layers with body only', () => {
      const layers = manager.generateLayers();
      expect(layers).to.deep.equal([
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

      expect(layers).to.deep.equal([
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
      expect(manager.validateCustomization()).to.be.true;

      const invalidManager = new CharacterCustomizationManager({
        bodyType: BodyType.HumanMaleMedium,
        skinTone: undefined as unknown as SkinTone,
      });
      expect(invalidManager.validateCustomization()).to.be.false;
    });

    it('should validate optional fields when present', () => {
      manager.updateCustomization({
        hair: {
          style: undefined as unknown as HairStyle,
          color: HairColor.Brown,
        },
      });
      expect(manager.validateCustomization()).to.be.false;

      manager.updateCustomization({
        hair: {
          style: HairStyle.Short,
          color: HairColor.Brown,
        },
      });
      expect(manager.validateCustomization()).to.be.true;
    });

    it('should validate equipment array', () => {
      manager.updateCustomization({
        equipment: [
          {
            type: undefined as unknown as EquipmentType,
          },
        ],
      });
      expect(manager.validateCustomization()).to.be.false;

      manager.updateCustomization({
        equipment: [
          {
            type: EquipmentType.Sword,
            variant: 'steel',
          },
        ],
      });
      expect(manager.validateCustomization()).to.be.true;
    });
  });
});

describe('ModularCharacterCustomizationManager', () => {
  const baseModular: ExtendedCharacterCustomization = {
    bodyType: BodyType.HumanMaleLarge,
    skinTone: SkinTone.Medium,
    meshSlots: [
      { slot: 'body', meshAsset: 'assets/meshes/test_body.glb', material: 'skin' },
    ],
    blendShapes: [
      { name: 'jawWidth', value: 0.5 },
    ],
    materials: [
      { materialKey: 'skin', color: '#b08d57' },
    ],
    scale: { x: 1, y: 1, z: 1 },
  };
  let modularManager: ModularCharacterCustomizationManager;

  beforeEach(() => {
    modularManager = new ModularCharacterCustomizationManager(baseModular);
  });

  it('should initialize with mesh slots, blend shapes, materials, and scale', () => {
    expect(modularManager.getMeshSlots()).to.deep.equal(baseModular.meshSlots);
    expect(modularManager.getBlendShapes()).to.deep.equal(baseModular.blendShapes);
    expect(modularManager.getMaterials()).to.deep.equal(baseModular.materials);
    expect(modularManager.getGlobalScale()).to.deep.equal(baseModular.scale);
  });

  it('should update mesh slots', () => {
    const newSlots = [
      { slot: 'head', meshAsset: 'assets/meshes/test_head.glb', material: 'skin' },
    ];
    modularManager.updateMeshSlots(newSlots);
    expect(modularManager.getMeshSlots()).to.deep.equal(newSlots);
  });

  it('should update blend shapes', () => {
    const newBlendShapes = [
      { name: 'browDepth', value: 0.8 },
    ];
    modularManager.updateBlendShapes(newBlendShapes);
    expect(modularManager.getBlendShapes()).to.deep.equal(newBlendShapes);
  });

  it('should update materials', () => {
    const newMaterials = [
      { materialKey: 'armor', color: '#888888', metallic: 0.8 },
    ];
    modularManager.updateMaterials(newMaterials);
    expect(modularManager.getMaterials()).to.deep.equal(newMaterials);
  });

  it('should update global scale', () => {
    const newScale = { x: 0.9, y: 0.9, z: 0.9 };
    modularManager.updateGlobalScale(newScale);
    expect(modularManager.getGlobalScale()).to.deep.equal(newScale);
  });

  it('should generate a full modular config', () => {
    const config = modularManager.generateModularConfig();
    expect(config.meshSlots).to.deep.equal(baseModular.meshSlots);
    expect(config.blendShapes).to.deep.equal(baseModular.blendShapes);
    expect(config.materials).to.deep.equal(baseModular.materials);
    expect(config.scale).to.deep.equal(baseModular.scale);
    expect(config.bodyType).to.equal(baseModular.bodyType);
    expect(config.skinTone).to.equal(baseModular.skinTone);
  });
});

describe('ModularCharacterCustomizationFactory', () => {
  it('should create a modular dwarf warrior with all modular fields', () => {
    const dwarf = ModularCharacterCustomizationFactory.createDwarfWarrior();
    expect(dwarf.meshSlots).to.exist;
    expect(dwarf.meshSlots).to.be.an('array');
    expect(dwarf.meshSlots!.some((slot: any) => slot.slot === 'beard')).to.be.true;
    expect(dwarf.blendShapes).to.exist;
    expect(dwarf.blendShapes).to.be.an('array');
    expect(dwarf.materials).to.exist;
    expect(dwarf.materials).to.be.an('array');
    expect(dwarf.scale).to.exist;
    expect(dwarf.scale!.x).to.be.a('number');
    expect(dwarf.bodyType).to.equal(BodyType.HumanMaleLarge);
    expect(dwarf.clothing?.type).to.equal(ClothingType.Armor);
  });

  it('should create a layered armor set with correct slots, zOrder, and material presets', () => {
    const armorSet = ModularCharacterCustomizationFactory.createLayeredArmorSet();
    const expectedSlots = ['helmet', 'chest', 'shoulders', 'legs', 'boots', 'gloves'];
    expect(armorSet.meshSlots).to.exist;
    expect(armorSet.meshSlots).to.be.an('array');
    for (const slot of expectedSlots) {
      expect(armorSet.meshSlots!.some((s: any) => s.slot === slot)).to.be.true;
    }
    // Check zOrder is increasing
    const zOrders = armorSet.meshSlots!.map((s: any) => s.zOrder);
    expect(zOrders).to.deep.equal([10, 20, 30, 40, 50, 60]);
    // Check material presets
    expect(armorSet.materials).to.exist;
    expect(armorSet.materials).to.be.an('array');
    const presets = armorSet.materials!.map((m: any) => m.preset);
    expect(presets).to.include('steel');
    expect(presets).to.include('bronze');
    expect(presets).to.include('leather');
  });
});

describe('ExtendedCharacterCustomizationSerializer', () => {
  const base: import('../CharacterCustomization').ExtendedCharacterCustomization = {
    bodyType: BodyType.HumanMaleLarge,
    skinTone: SkinTone.Medium,
    meshSlots: [
      { slot: 'body', meshAsset: 'assets/meshes/test_body.glb', material: 'skin' },
    ],
    blendShapes: [
      { name: 'jawWidth', value: 0.5 },
    ],
    materials: [
      { materialKey: 'skin', color: '#b08d57' },
    ],
    scale: { x: 1, y: 1, z: 1 },
  };

  it('should serialize and deserialize a full modular customization', () => {
    const json = ExtendedCharacterCustomizationSerializer.serialize(base);
    const parsed = ExtendedCharacterCustomizationSerializer.deserialize(json);
    expect(parsed).to.deep.equal(base);
  });

  it('should serialize only diffs when diffFrom is provided', () => {
    const mod = { ...base, scale: { x: 1.2, y: 1, z: 1 } };
    const json = ExtendedCharacterCustomizationSerializer.serialize(mod, { diffFrom: base });
    const parsed = JSON.parse(json);
    expect(parsed).to.not.have.property('meshSlots');
    expect(parsed).to.have.property('scale');
    expect(parsed).to.have.property('__diff', true);
  });

  it('should ignore unknown fields on deserialize (forward compatibility)', () => {
    const json = ExtendedCharacterCustomizationSerializer.serialize(base);
    const withUnknown = json.replace('}', ',"futureField":123}');
    const parsed = ExtendedCharacterCustomizationSerializer.deserialize(withUnknown);
    expect(parsed).to.have.property('bodyType');
    expect(parsed).to.have.property('meshSlots');
    expect(parsed).to.not.have.property('futureField');
  });

  it('should set version to 1 if missing', () => {
    const json = ExtendedCharacterCustomizationSerializer.serialize(base);
    const obj = JSON.parse(json);
    delete obj.__version;
    const noVersion = JSON.stringify(obj);
    const parsed = ExtendedCharacterCustomizationSerializer.deserialize(noVersion);
    expect(parsed).to.have.property('bodyType');
  });
});

describe('RandomCharacterGenerator', () => {
  const simpleProfile: RandomizationProfile = {
    name: 'default',
    featureWeights: {
      bodyType: {
        human_male_slim: 0.01,
        human_male_medium: 1,
        human_male_large: 0.01,
        human_female_slim: 0.01,
        human_female_medium: 1,
        human_female_large: 0.01,
      },
      skinTone: { light: 1, medium: 2, dark: 1 },
      hairStyle: { short: 2, medium: 0.01, long: 1, bald: 0.01 },
      hairColor: { black: 1, brown: 1, blonde: 1, red: 0.01, gray: 0.01, white: 0.01 },
      eyeType: { round: 1, almond: 1, narrow: 0.01 },
      eyeColor: { brown: 2, blue: 1, green: 0.01, hazel: 0.01, gray: 0.01 },
      mouthType: { neutral: 1, smile: 1, frown: 0.01 },
      clothingType: { shirt: 1, tunic: 1, robe: 0.01, armor: 0.01 },
      equipmentType: { sword: 1, staff: 1, bow: 0.01, shield: 0.01 },
    },
    constraints: {},
  };
  const generator = new RandomCharacterGenerator([simpleProfile]);

  it('should generate a valid random customization', () => {
    const customization = generator.generateRandomCustomization('default');
    expect(customization.bodyType).to.exist;
    expect(customization.skinTone).to.exist;
    expect(customization.hair).to.exist;
    expect(customization.eyes).to.exist;
    expect(customization.mouth).to.exist;
    expect(customization.clothing).to.exist;
    expect(customization.equipment).to.exist;
  });

  it('should respect feature locks', () => {
    const locked = { bodyType: BodyType.HumanFemaleMedium, skinTone: SkinTone.Dark };
    const customization = generator.generateRandomCustomization('default', locked);
    expect(customization.bodyType).to.equal(BodyType.HumanFemaleMedium);
    expect(customization.skinTone).to.equal(SkinTone.Dark);
  });

  it('should use weighted probabilities', () => {
    // Generate a batch and check distribution
    let countMedium = 0;
    let countLight = 0;
    for (let i = 0; i < 100; ++i) {
      const c = generator.generateRandomCustomization('default');
      if (c.skinTone === 'medium') countMedium++;
      if (c.skinTone === 'light') countLight++;
    }
    expect(countMedium).to.be.greaterThan(countLight);
  });
});
