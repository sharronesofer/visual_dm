import { FactionType, FactionStyle } from './types';

const styles: Record<FactionType, FactionStyle> = {
  guild: {
    id: 'guild_style',
    name: 'Guild Hall',
    description: 'Traditional, wood-paneled, banners and trophies.',
    colorScheme: ['brown', 'gold', 'red'],
    architecturalFeatures: ['vaulted ceilings', 'meeting hall', 'library'],
    decor: ['banners', 'trophies', 'wooden furniture']
  },
  order: {
    id: 'order_style',
    name: 'Order Sanctuary',
    description: 'Stone, stained glass, symmetrical layout.',
    colorScheme: ['gray', 'blue', 'white'],
    architecturalFeatures: ['cloister', 'chapel', 'archive'],
    decor: ['statues', 'candles', 'altars']
  },
  syndicate: {
    id: 'syndicate_style',
    name: 'Syndicate Lair',
    description: 'Hidden, labyrinthine, secret passages.',
    colorScheme: ['black', 'purple', 'silver'],
    architecturalFeatures: ['hidden rooms', 'escape tunnels', 'vault'],
    decor: ['graffiti', 'contraband', 'luxury items']
  },
  militia: {
    id: 'militia_style',
    name: 'Militia Barracks',
    description: 'Fortified, utilitarian, training grounds.',
    colorScheme: ['green', 'gray', 'brown'],
    architecturalFeatures: ['armory', 'barracks', 'parade ground'],
    decor: ['weapons racks', 'flags', 'training dummies']
  },
  cult: {
    id: 'cult_style',
    name: 'Cult Temple',
    description: 'Dark, ritualistic, mysterious symbols.',
    colorScheme: ['black', 'red', 'gold'],
    architecturalFeatures: ['ritual chamber', 'catacombs', 'altar'],
    decor: ['skulls', 'candles', 'strange runes']
  }
};

export class FactionStyles {
  static getStyle(type: FactionType): FactionStyle {
    return styles[type];
  }
} 