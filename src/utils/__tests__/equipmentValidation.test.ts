import {
  validateEquipmentSelection,
  validateEquipmentItem,
  validateEquipmentCompatibility,
} from '../equipmentValidation';
import type { StarterKit, Equipment } from '../../types/character';

describe('Equipment Validation', () => {
  const mockWeapon: Equipment = {
    name: 'Longsword',
    type: 'weapon',
    quantity: 1,
    description: 'A versatile sword',
    properties: ['versatile'],
    weight: 3,
    cost: 15,
    damage: '1d8',
  };

  const mockArmor: Equipment = {
    name: 'Chain Mail',
    type: 'armor',
    quantity: 1,
    description: 'Heavy armor',
    properties: ['heavy'],
    weight: 55,
    cost: 75,
    armorClass: 16,
  };

  const mockKit: StarterKit = {
    id: 'fighter-kit-1',
    name: 'Fighter Starting Equipment',
    description: 'Standard equipment for fighters',
    items: [mockWeapon, mockArmor],
    gold: 10,
  };

  describe('validateEquipmentSelection', () => {
    it('should validate a valid equipment kit', () => {
      const result = validateEquipmentSelection(mockKit);
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
      expect(result.warnings).toHaveLength(0);
      expect(result.incompleteFields).toHaveLength(0);
    });

    it('should fail validation for null kit', () => {
      const result = validateEquipmentSelection(null);
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('No equipment kit selected');
    });

    it('should fail validation for empty kit items', () => {
      const emptyKit: StarterKit = {
        ...mockKit,
        items: [],
      };
      const result = validateEquipmentSelection(emptyKit);
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Selected kit contains no equipment');
      expect(result.incompleteFields).toContain('equipment');
    });

    it('should fail validation for negative gold', () => {
      const negativeGoldKit: StarterKit = {
        ...mockKit,
        gold: -5,
      };
      const result = validateEquipmentSelection(negativeGoldKit);
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Invalid gold amount in selected kit');
    });

    it('should validate kit with minimum requirements', () => {
      const minimalKit: StarterKit = {
        id: 'minimal-kit-1',
        name: 'Minimal Kit',
        description: 'Basic equipment',
        items: [mockWeapon],
        gold: 0,
      };
      const result = validateEquipmentSelection(minimalKit);
      expect(result.isValid).toBe(true);
      expect(result.warnings).toHaveLength(0);
    });

    it('should warn about duplicate equipment types', () => {
      const duplicateKit: StarterKit = {
        ...mockKit,
        items: [mockWeapon, mockWeapon],
      };
      const result = validateEquipmentSelection(duplicateKit);
      expect(result.isValid).toBe(true);
      expect(result.warnings).toContain(
        'Multiple weapons of the same type detected'
      );
    });
  });

  describe('validateEquipmentCompatibility', () => {
    it('should validate compatible equipment for fighter', () => {
      const result = validateEquipmentCompatibility(mockKit.items, 'Fighter');
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
      expect(result.warnings).toHaveLength(0);
    });

    it('should warn about heavy armor for rogues', () => {
      const result = validateEquipmentCompatibility(mockKit.items, 'Rogue');
      expect(result.isValid).toBe(true);
      expect(result.warnings).toContain(
        'Rogues are not proficient with heavy armor'
      );
    });

    it('should warn about missing spellbook for wizards', () => {
      const result = validateEquipmentCompatibility(mockKit.items, 'Wizard');
      expect(result.isValid).toBe(true);
      expect(result.warnings).toContain('Wizards typically need a spellbook');
    });

    it('should validate monk martial arts weapons', () => {
      const monkWeapons: Equipment[] = [
        {
          name: 'Quarterstaff',
          type: 'weapon',
          quantity: 1,
          description: 'A simple but effective weapon',
          properties: ['versatile', 'monk'],
          weight: 4,
          cost: 2,
          damage: '1d6',
        },
      ];
      const result = validateEquipmentCompatibility(monkWeapons, 'Monk');
      expect(result.isValid).toBe(true);
      expect(result.warnings).toHaveLength(0);
    });

    it('should warn about non-martial arts weapons for monks', () => {
      const result = validateEquipmentCompatibility([mockWeapon], 'Monk');
      expect(result.isValid).toBe(true);
      expect(result.warnings).toContain(
        'Some weapons are not optimal for monk martial arts'
      );
    });

    it('should validate cleric equipment with holy symbol', () => {
      const clericKit: Equipment[] = [
        mockWeapon,
        mockArmor,
        {
          name: 'Holy Symbol',
          type: 'gear',
          quantity: 1,
          description: 'A divine focus',
          properties: ['holy'],
          weight: 1,
          cost: 5,
        },
      ];
      const result = validateEquipmentCompatibility(clericKit, 'Cleric');
      expect(result.isValid).toBe(true);
      expect(result.warnings).toHaveLength(0);
    });

    it('should warn about missing holy symbol for clerics', () => {
      const result = validateEquipmentCompatibility(mockKit.items, 'Cleric');
      expect(result.isValid).toBe(true);
      expect(result.warnings).toContain('Clerics typically need a holy symbol');
    });

    it('should validate druid equipment restrictions', () => {
      const druidKit: Equipment[] = [
        {
          name: 'Wooden Shield',
          type: 'armor',
          quantity: 1,
          description: 'A shield made of wood',
          properties: ['shield'],
          weight: 6,
          cost: 10,
          armorClass: 2,
        },
      ];
      const result = validateEquipmentCompatibility(druidKit, 'Druid');
      expect(result.isValid).toBe(true);
      expect(result.warnings).toHaveLength(0);
    });

    it('should warn about metal armor for druids', () => {
      const result = validateEquipmentCompatibility([mockArmor], 'Druid');
      expect(result.isValid).toBe(true);
      expect(result.warnings).toContain(
        'Druids will not wear armor made of metal'
      );
    });

    it('should validate paladin equipment with holy symbol', () => {
      const paladinKit: Equipment[] = [
        mockWeapon,
        mockArmor,
        {
          name: 'Holy Symbol',
          type: 'gear',
          quantity: 1,
          description: 'A divine focus',
          properties: ['holy'],
          weight: 1,
          cost: 5,
        },
      ];
      const result = validateEquipmentCompatibility(paladinKit, 'Paladin');
      expect(result.isValid).toBe(true);
      expect(result.warnings).toHaveLength(0);
    });

    it('should warn about missing holy symbol for paladins', () => {
      const result = validateEquipmentCompatibility(mockKit.items, 'Paladin');
      expect(result.isValid).toBe(true);
      expect(result.warnings).toContain(
        'Paladins typically need a holy symbol'
      );
    });
  });
});

describe('validateEquipmentItem', () => {
  const validWeapon: Equipment = {
    name: 'Longsword',
    type: 'weapon',
    quantity: 1,
    description: 'A versatile sword',
    properties: ['versatile'],
    weight: 3,
    cost: 15,
    damage: '1d8',
  };

  it('validates a valid equipment item', () => {
    const result = validateEquipmentItem(validWeapon);
    expect(result.isValid).toBe(true);
    expect(result.errors).toHaveLength(0);
  });

  it('requires a name', () => {
    const noNameWeapon = { ...validWeapon, name: '' };
    const result = validateEquipmentItem(noNameWeapon);
    expect(result.isValid).toBe(false);
    expect(result.errors).toContain('Equipment item must have a name');
  });

  it('requires a type', () => {
    const noTypeWeapon = { ...validWeapon, type: '' as any };
    const result = validateEquipmentItem(noTypeWeapon);
    expect(result.isValid).toBe(false);
    expect(result.errors).toContain('Equipment item must have a type');
  });

  it('adds warning for missing description', () => {
    const noDescWeapon = { ...validWeapon, description: '' };
    const result = validateEquipmentItem(noDescWeapon);
    expect(result.warnings).toContain(
      'Equipment item should have a description'
    );
  });

  it('adds warning for weapon without damage', () => {
    const noDamageWeapon = { ...validWeapon, damage: undefined };
    const result = validateEquipmentItem(noDamageWeapon);
    expect(result.warnings).toContain('Weapon should specify damage');
  });

  it('adds warning for armor without armor class', () => {
    const noACarmor: Equipment = {
      name: 'Chain Mail',
      type: 'armor',
      quantity: 1,
      description: 'Heavy armor',
      properties: ['heavy'],
      weight: 55,
      cost: 75,
    };
    const result = validateEquipmentItem(noACarmor);
    expect(result.warnings).toContain('Armor should specify armor class');
  });

  it('adds warning for negative value', () => {
    const negativeValueWeapon = { ...validWeapon, cost: -5 };
    const result = validateEquipmentItem(negativeValueWeapon);
    expect(result.warnings).toContain(
      'Equipment item should have a valid non-negative value'
    );
  });
});
