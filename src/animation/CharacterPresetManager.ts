// CharacterPresetManager.ts
// Manages saving and loading of character customization presets

import { CharacterCustomization, BodyType } from './CharacterCustomization';
import { CharacterCustomizationManager } from './CharacterCustomization';
import { CharacterCustomizationFactory } from './CharacterCustomizationFactory';

/**
 * Interface for a saved character preset.
 */
export interface CharacterPreset {
  id: string;
  name: string;
  description?: string;
  tags?: string[];
  customization: CharacterCustomization;
  createdAt: number;
  updatedAt: number;
}

/**
 * Manages character customization presets with persistence.
 */
export class CharacterPresetManager {
  private static readonly STORAGE_KEY = 'character_presets';
  private presets: Map<string, CharacterPreset>;

  constructor() {
    this.presets = new Map();
    this.loadPresets();
  }

  /**
   * Save a new character preset.
   */
  public savePreset(
    id: string,
    name: string,
    customization: CharacterCustomization,
    description?: string,
    tags?: string[]
  ): CharacterPreset {
    const now = Date.now();
    const preset: CharacterPreset = {
      id,
      name,
      description,
      tags,
      customization,
      createdAt: now,
      updatedAt: now,
    };

    this.presets.set(id, preset);
    this.persistPresets();
    return preset;
  }

  /**
   * Update an existing character preset.
   */
  public updatePreset(
    id: string,
    updates: Partial<Omit<CharacterPreset, 'id' | 'createdAt'>>
  ): CharacterPreset {
    const preset = this.presets.get(id);
    if (!preset) {
      throw new Error(`Preset with ID ${id} not found`);
    }

    const updatedPreset: CharacterPreset = {
      ...preset,
      ...updates,
      updatedAt: Date.now(),
    };

    this.presets.set(id, updatedPreset);
    this.persistPresets();
    return updatedPreset;
  }

  /**
   * Get a preset by ID.
   */
  public getPreset(id: string): CharacterPreset | undefined {
    return this.presets.get(id);
  }

  /**
   * Delete a preset by ID.
   */
  public deletePreset(id: string): boolean {
    const deleted = this.presets.delete(id);
    if (deleted) {
      this.persistPresets();
    }
    return deleted;
  }

  /**
   * Get all presets.
   */
  public getAllPresets(): CharacterPreset[] {
    return Array.from(this.presets.values());
  }

  /**
   * Search presets by name, description, or tags.
   */
  public searchPresets(query: string): CharacterPreset[] {
    const normalizedQuery = query.toLowerCase();
    return Array.from(this.presets.values()).filter(preset => {
      const nameMatch = preset.name.toLowerCase().includes(normalizedQuery);
      const descMatch = preset.description?.toLowerCase().includes(normalizedQuery);
      const tagMatch = preset.tags?.some(tag => tag.toLowerCase().includes(normalizedQuery));
      return nameMatch || descMatch || tagMatch;
    });
  }

  /**
   * Filter presets by tags.
   */
  public filterByTags(tags: string[]): CharacterPreset[] {
    const normalizedTags = tags.map(tag => tag.toLowerCase());
    return Array.from(this.presets.values()).filter(preset =>
      preset.tags?.some(tag => normalizedTags.includes(tag.toLowerCase()))
    );
  }

  /**
   * Load presets from storage.
   */
  private loadPresets(): void {
    try {
      const storedData = localStorage.getItem(CharacterPresetManager.STORAGE_KEY);
      if (storedData) {
        const presets = JSON.parse(storedData) as CharacterPreset[];
        this.presets = new Map(presets.map(preset => [preset.id, preset]));
      } else {
        // Initialize with default presets if storage is empty
        this.initializeDefaultPresets();
      }
    } catch (error) {
      console.error('Failed to load character presets:', error);
      // Initialize with defaults on error
      this.initializeDefaultPresets();
    }
  }

  /**
   * Save presets to storage.
   */
  private persistPresets(): void {
    try {
      const presetsArray = Array.from(this.presets.values());
      localStorage.setItem(CharacterPresetManager.STORAGE_KEY, JSON.stringify(presetsArray));
    } catch (error) {
      console.error('Failed to save character presets:', error);
    }
  }

  /**
   * Initialize default character presets.
   */
  private initializeDefaultPresets(): void {
    // Basic presets
    this.savePreset(
      'basic_male',
      'Basic Male',
      CharacterCustomizationFactory.createBasicHumanMale(),
      'Default male character preset',
      ['basic', 'male']
    );

    this.savePreset(
      'basic_female',
      'Basic Female',
      CharacterCustomizationFactory.createBasicHumanFemale(),
      'Default female character preset',
      ['basic', 'female']
    );

    // Class-based presets
    this.savePreset(
      'warrior_male',
      'Male Warrior',
      CharacterCustomizationFactory.createWarrior(),
      'Male warrior with sword and shield',
      ['warrior', 'male', 'combat']
    );

    this.savePreset(
      'warrior_female',
      'Female Warrior',
      CharacterCustomizationFactory.createWarrior(BodyType.HumanFemaleMedium),
      'Female warrior with sword and shield',
      ['warrior', 'female', 'combat']
    );

    this.savePreset(
      'mage_male',
      'Male Mage',
      CharacterCustomizationFactory.createMage(),
      'Male mage with staff and robes',
      ['mage', 'male', 'magic']
    );

    this.savePreset(
      'mage_female',
      'Female Mage',
      CharacterCustomizationFactory.createMage(BodyType.HumanFemaleMedium),
      'Female mage with staff and robes',
      ['mage', 'female', 'magic']
    );

    this.savePreset(
      'archer_male',
      'Male Archer',
      CharacterCustomizationFactory.createArcher(BodyType.HumanMaleMedium),
      'Male archer with bow',
      ['archer', 'male', 'ranged']
    );

    this.savePreset(
      'archer_female',
      'Female Archer',
      CharacterCustomizationFactory.createArcher(),
      'Female archer with bow',
      ['archer', 'female', 'ranged']
    );
  }
}

export default CharacterPresetManager;
