/// <reference types="vitest" />
import { vi } from "vitest";
// CharacterPresetManager.test.ts
// Tests for character preset management system

import {
  CharacterPresetManager,
  CharacterPreset,
} from '../CharacterPresetManager';
import { CharacterCustomizationFactory } from '../CharacterCustomizationFactory';
import { BodyType, SkinTone } from '../CharacterCustomization';
import { ModularCharacterCustomizationFactory } from '../CharacterCustomizationFactory';
import { ExtendedCharacterCustomizationSerializer } from '../CharacterCustomization';

describe('CharacterPresetManager', () => {
  let manager: CharacterPresetManager;
  let mockStorage: { [key: string]: string } = {};

  // Mock localStorage
  beforeEach(() => {
    mockStorage = {};
    global.localStorage = {
      getItem: vi.fn((key: string) => mockStorage[key] || null),
      setItem: vi.fn((key: string, value: string) => {
        mockStorage[key] = value;
      }),
      removeItem: vi.fn((key: string) => {
        delete mockStorage[key];
      }),
      clear: vi.fn(() => {
        mockStorage = {};
      }),
      length: 0,
      key: vi.fn((index: number) => ''),
    } as any;
    manager = new CharacterPresetManager();
  });

  describe('initialization', () => {
    it('should initialize with default presets when storage is empty', () => {
      const presets = manager.getAllPresets();
      expect(presets.length).to.equal(8); // Basic male/female + 3 classes * 2 genders
      expect(presets.some(p => p.id === 'basic_male')).to.be.true;
      expect(presets.some(p => p.id === 'basic_female')).to.be.true;
    });

    it('should load existing presets from storage', () => {
      const customPreset: CharacterPreset = {
        id: 'custom_1',
        name: 'Custom Preset',
        description: 'Test preset',
        tags: ['test'],
        customization: CharacterCustomizationFactory.createBasicHumanMale(),
        createdAt: Date.now(),
        updatedAt: Date.now(),
      };
      mockStorage['character_presets'] = JSON.stringify([customPreset]);

      manager = new CharacterPresetManager();
      const loadedPreset = manager.getPreset('custom_1');
      expect(loadedPreset).to.deep.equal(customPreset);
    });
  });

  describe('savePreset', () => {
    it('should save a new preset', () => {
      const customization =
        CharacterCustomizationFactory.createBasicHumanMale();
      const preset = manager.savePreset(
        'test_1',
        'Test Preset',
        customization,
        'Test description',
        ['test']
      );

      expect(preset.id).to.equal('test_1');
      expect(preset.name).to.equal('Test Preset');
      expect(preset.description).to.equal('Test description');
      expect(preset.tags).to.deep.equal(['test']);
      expect(preset.customization).to.deep.equal(customization);
      expect(preset.createdAt).to.exist;
      expect(preset.updatedAt).to.exist;

      // Verify storage was updated
      expect((global.localStorage.setItem as any).mock.calls.length).to.be.greaterThan(0);
    });

    it('should overwrite existing preset with same ID', () => {
      const customization1 =
        CharacterCustomizationFactory.createBasicHumanMale();
      const customization2 =
        CharacterCustomizationFactory.createBasicHumanFemale();

      manager.savePreset('test_1', 'Test 1', customization1);
      const preset2 = manager.savePreset('test_1', 'Test 2', customization2);

      expect(manager.getPreset('test_1')).to.deep.equal(preset2);
    });
  });

  describe('updatePreset', () => {
    it('should update an existing preset', () => {
      const customization =
        CharacterCustomizationFactory.createBasicHumanMale();
      const original = manager.savePreset('test_1', 'Test', customization);
      const createdAt = original.createdAt;

      const updated = manager.updatePreset('test_1', {
        name: 'Updated Test',
        description: 'Updated description',
      });

      expect(updated.name).to.equal('Updated Test');
      expect(updated.description).to.equal('Updated description');
      expect(updated.createdAt).to.equal(createdAt);
      expect(updated.updatedAt).to.be.at.least(createdAt);
    });

    it('should throw error when updating non-existent preset', () => {
      expect(() => {
        manager.updatePreset('non_existent', { name: 'Test' });
      }).to.throw('Preset with ID non_existent not found');
    });
  });

  describe('deletePreset', () => {
    it('should delete an existing preset', () => {
      const customization =
        CharacterCustomizationFactory.createBasicHumanMale();
      manager.savePreset('test_1', 'Test', customization);

      const deleted = manager.deletePreset('test_1');
      expect(deleted).to.be.true;
      expect(manager.getPreset('test_1')).to.be.undefined;
    });

    it('should return false when deleting non-existent preset', () => {
      const deleted = manager.deletePreset('non_existent');
      expect(deleted).to.be.false;
    });
  });

  describe('searchPresets', () => {
    beforeEach(() => {
      manager.savePreset(
        'test_1',
        'Warrior Test',
        CharacterCustomizationFactory.createWarrior(),
        'A test warrior preset',
        ['warrior', 'test']
      );
      manager.savePreset(
        'test_2',
        'Mage Test',
        CharacterCustomizationFactory.createMage(),
        'A test mage preset',
        ['mage', 'test']
      );
    });

    it('should find presets by name', () => {
      const results = manager.searchPresets('warrior');
      expect(results.length).to.be.greaterThan(0);
      expect(results.every(p => p.name.toLowerCase().includes('warrior'))).to.be.true;
    });

    it('should find presets by description', () => {
      const results = manager.searchPresets('test warrior');
      expect(results.length).to.be.greaterThan(0);
      expect(
        results.some(p => p.description?.toLowerCase().includes('test warrior'))
      ).to.be.true;
    });

    it('should find presets by tags', () => {
      const results = manager.searchPresets('test');
      expect(results.length).to.equal(2);
      expect(results.every(p => p.tags?.includes('test'))).to.be.true;
    });
  });

  describe('filterByTags', () => {
    beforeEach(() => {
      manager.savePreset(
        'test_1',
        'Warrior Test',
        CharacterCustomizationFactory.createWarrior(),
        'A test warrior preset',
        ['warrior', 'combat', 'test']
      );
      manager.savePreset(
        'test_2',
        'Mage Test',
        CharacterCustomizationFactory.createMage(),
        'A test mage preset',
        ['mage', 'magic', 'test']
      );
    });

    it('should filter presets by single tag', () => {
      const results = manager.filterByTags(['warrior']);
      expect(results.length).to.be.greaterThan(0);
      expect(results.every(p => p.tags?.includes('warrior'))).to.be.true;
    });

    it('should filter presets by multiple tags', () => {
      const results = manager.filterByTags(['test', 'combat']);
      expect(results.length).to.equal(4);
      expect(results.some(p => p.tags && p.tags.includes('test') && p.tags.includes('combat'))).to.be.true;
      expect(results.every(p => p.tags && (p.tags.includes('test') || p.tags.includes('combat')))).to.be.true;
    });

    it('should handle case-insensitive tag matching', () => {
      const results = manager.filterByTags(['WARRIOR', 'Combat']);
      expect(results.length).to.be.greaterThan(0);
      expect(
        results.every(p =>
          p.tags?.some(
            tag =>
              tag.toLowerCase() === 'warrior' || tag.toLowerCase() === 'combat'
          )
        )
      ).to.be.true;
    });
  });
});

describe('CharacterPresetManager (modular)', () => {
  let manager: CharacterPresetManager;
  let mockStorage: Record<string, string> = {};
  beforeEach(() => {
    mockStorage = {};
    global.localStorage = {
      getItem: vi.fn((key: string) => mockStorage[key] || null),
      setItem: vi.fn((key: string, value: string) => {
        mockStorage[key] = value;
      }),
      removeItem: vi.fn((key: string) => {
        delete mockStorage[key];
      }),
      clear: vi.fn(() => {
        mockStorage = {};
      }),
      length: 0,
      key: vi.fn((index: number) => ''),
    } as any;
    manager = new CharacterPresetManager();
  });

  it('should save and load a modular preset with version', () => {
    const modular = ModularCharacterCustomizationFactory.createDwarfWarrior();
    const preset = manager.savePreset('mod1', 'Modular Dwarf', modular, 'A modular dwarf', ['modular']);
    expect(preset.version).to.equal(1);
    const loaded = manager.getPreset('mod1');
    expect(loaded).to.exist;
    expect(loaded!.customization).to.deep.equal(modular);
    expect(loaded!.version).to.equal(1);
  });

  it('should migrate legacy modular presets to include version', () => {
    const modular = ModularCharacterCustomizationFactory.createDwarfWarrior();
    // Simulate legacy preset (no version field)
    mockStorage['character_presets'] = JSON.stringify([
      {
        id: 'legacy1',
        name: 'Legacy Modular',
        customization: modular,
        createdAt: Date.now(),
        updatedAt: Date.now(),
      },
    ]);
    manager = new CharacterPresetManager();
    const loaded = manager.getPreset('legacy1');
    expect(loaded).to.exist;
    expect(loaded!.version).to.equal(1);
  });
});
