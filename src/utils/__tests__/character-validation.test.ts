import { describe, it, expect } from 'vitest';
import {
  validateCharacter,
  validateAttributes,
  validateSkills,
  validateEquipment,
  ValidationError,
} from '../validation';
import { CharacterData, Attributes, Race, Class, Background } from '../../types/character';

describe('Character Validation', () => {
  describe('validateAttributes', () => {
    it('should validate valid attributes', () => {
      const validAttributes: Attributes = {
        strength: 10,
        dexterity: 12,
        constitution: 14,
        intelligence: 13,
        wisdom: 11,
        charisma: 15,
      };

      const errors = validateAttributes(validAttributes);
      expect(errors).toHaveLength(0);
    });

    it('should return errors for invalid attributes', () => {
      const invalidAttributes: Attributes = {
        strength: 2, // Too low
        dexterity: 21, // Too high
        constitution: 14,
        intelligence: 13,
        wisdom: 11,
        charisma: 15,
      };

      const errors = validateAttributes(invalidAttributes);
      expect(errors).toHaveLength(2);
      expect(errors[0]).toEqual({
        field: 'strength',
        message: 'Strength must be between 3 and 20',
        severity: 'error',
      });
      expect(errors[1]).toEqual({
        field: 'dexterity',
        message: 'Dexterity must be between 3 and 20',
        severity: 'error',
      });
    });
  });

  describe('validateSkills', () => {
    it('should validate valid skills', () => {
      const validSkills = [
        { name: 'Athletics', isProficient: true },
        { name: 'Stealth', isProficient: false },
      ];

      const errors = validateSkills(validSkills);
      expect(errors).toHaveLength(0);
    });

    it('should return errors for empty skills', () => {
      const errors = validateSkills([]);
      expect(errors).toHaveLength(1);
      expect(errors[0]).toEqual({
        field: 'skills',
        message: 'Must select at least one skill',
        severity: 'error',
      });
    });

    it('should return errors when no proficient skills', () => {
      const noProficentSkills = [
        { name: 'Athletics', isProficient: false },
        { name: 'Stealth', isProficient: false },
      ];

      const errors = validateSkills(noProficentSkills);
      expect(errors).toHaveLength(1);
      expect(errors[0]).toEqual({
        field: 'skills',
        message: 'Must have at least one proficient skill',
        severity: 'error',
      });
    });
  });

  describe('validateEquipment', () => {
    it('should validate valid equipment', () => {
      const validEquipment = [
        { name: 'Longsword', type: 'weapon', quantity: 1, description: 'A versatile sword' },
        { name: 'Chain Mail', type: 'armor', quantity: 1, description: 'Heavy armor' },
      ];

      const errors = validateEquipment(validEquipment);
      expect(errors).toHaveLength(0);
    });

    it('should return errors for invalid equipment', () => {
      const invalidEquipment = [
        { name: '', type: '', quantity: 0, description: '' },
      ];

      const errors = validateEquipment(invalidEquipment);
      expect(errors).toHaveLength(3);
      expect(errors).toContainEqual({
        field: 'equipment[0].name',
        message: 'Item name is required',
        severity: 'error',
      });
      expect(errors).toContainEqual({
        field: 'equipment[0].type',
        message: 'Item type is required',
        severity: 'error',
      });
      expect(errors).toContainEqual({
        field: 'equipment[0].quantity',
        message: 'Quantity must be at least 1',
        severity: 'error',
      });
    });
  });

  describe('validateCharacter', () => {
    const mockRace: Race = {
      name: 'Human',
      description: 'Versatile and adaptable',
      abilityScoreIncrease: { strength: 1, dexterity: 1 },
      speed: 30,
      size: 'Medium',
      languages: ['Common'],
      traits: [{ name: 'Versatile', description: 'Gain proficiency in one skill' }],
    };

    const mockClass: Class = {
      name: 'Fighter',
      description: 'Master of martial combat',
      hitDie: 10,
      primaryAbility: 'strength',
      savingThrows: ['strength', 'constitution'],
      proficiencies: {
        armor: ['light', 'medium', 'heavy'],
        weapons: ['martial', 'simple'],
        tools: [],
        skills: ['Athletics', 'Intimidation'],
      },
      features: [{ name: 'Fighting Style', level: 1, description: 'Choose a fighting style' }],
    };

    const mockBackground: Background = {
      name: 'Soldier',
      description: 'Military background',
      skillProficiencies: ['Athletics', 'Intimidation'],
      toolProficiencies: ['Gaming Set', 'Vehicles (Land)'],
      languages: [],
      equipment: [{ name: 'Common Clothes', type: 'gear', quantity: 1, description: 'A set of common clothes' }],
      feature: { name: 'Military Rank', description: 'You have a military rank' },
      suggestedCharacteristics: {
        personalityTraits: ['I face problems head-on'],
        ideals: ['Responsibility'],
        bonds: ['I fight for those who cannot fight for themselves'],
        flaws: ['I have a weakness for vices'],
      },
    };

    it('should validate a valid character', () => {
      const validCharacter: CharacterData = {
        id: '123',
        name: 'Test Character',
        race: mockRace,
        class: mockClass,
        background: mockBackground,
        level: 1,
        experience: 0,
        attributes: {
          strength: 15,
          dexterity: 14,
          constitution: 13,
          intelligence: 12,
          wisdom: 10,
          charisma: 8,
        },
        skills: [{ name: 'Athletics', ability: 'strength', proficient: true, expertise: false, value: 4 }],
        features: [],
        equipment: [
          { name: 'Longsword', type: 'weapon', quantity: 1, description: 'A versatile sword' },
          { name: 'Chain Mail', type: 'armor', quantity: 1, description: 'Heavy armor' },
        ],
        proficiencies: ['simple weapons', 'martial weapons'],
        languages: ['Common'],
        description: 'A brave warrior',
        personality: {
          traits: ['Brave'],
          ideals: ['Honor'],
          bonds: ['Protect the weak'],
          flaws: ['Stubborn'],
        },
        alignment: 'Lawful Good',
        feats: [],
        derivedStats: {
          hitPoints: 12,
          armorClass: 16,
          initiative: 2,
          speed: 30,
          proficiencyBonus: 2,
          savingThrows: {
            strength: 4,
            dexterity: 2,
            constitution: 1,
            intelligence: 1,
            wisdom: 0,
            charisma: -1,
          },
        },
        appearance: {
          height: '6\'0"',
          weight: '180 lbs',
          age: 25,
          eyes: 'Brown',
          skin: 'Fair',
          hair: 'Black',
        },
        backstory: 'Grew up in a military family',
        skillPoints: 0,
      };

      const result = validateCharacter(validCharacter);
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should return errors for an invalid character', () => {
      const invalidCharacter: Partial<CharacterData> = {
        id: '123',
        name: '',  // Invalid: empty name
        background: mockBackground,
        level: 1,
        experience: 0,
        attributes: {
          strength: 2,  // Invalid: too low
          dexterity: 21,  // Invalid: too high
          constitution: 13,
          intelligence: 12,
          wisdom: 10,
          charisma: 8,
        },
        skills: [],  // Invalid: no skills
        features: [],
        equipment: [],  // Warning: no armor/weapon
        proficiencies: [],
        languages: [],
        description: '',
        personality: {
          traits: [],
          ideals: [],
          bonds: [],
          flaws: [],
        },
        alignment: 'Lawful Good',
        feats: [],
        derivedStats: {
          hitPoints: 12,
          armorClass: 16,
          initiative: 2,
          speed: 30,
          proficiencyBonus: 2,
          savingThrows: {
            strength: 4,
            dexterity: 2,
            constitution: 1,
            intelligence: 1,
            wisdom: 0,
            charisma: -1,
          },
        },
        appearance: {
          height: '6\'0"',
          weight: '180 lbs',
          age: 25,
          eyes: 'Brown',
          skin: 'Fair',
          hair: 'Black',
        },
        backstory: '',
        skillPoints: 0,
      };

      const result = validateCharacter(invalidCharacter as CharacterData);
      expect(result.isValid).toBe(false);
      
      // Check for specific errors
      const errorMessages = result.errors.map(e => e.message);
      expect(errorMessages).toContain('Name is required');
      expect(errorMessages).toContain('Race is required');
      expect(errorMessages).toContain('Class is required');
      expect(errorMessages).toContain('Strength must be between 3 and 20');
      expect(errorMessages).toContain('Dexterity must be between 3 and 20');
      expect(errorMessages).toContain('Must select at least one skill');
      expect(errorMessages).toContain('No armor selected');
      expect(errorMessages).toContain('No weapon selected');
    });
  });
}); 