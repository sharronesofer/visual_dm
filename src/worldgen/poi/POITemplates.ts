import { POIType, POITemplate } from './types';

const templates: Record<POIType, POITemplate> = {
  shop: {
    id: 'shop_base',
    type: 'shop',
    baseDescription: 'A small trading post with various goods.',
    baseLoot: ['coins', 'food', 'tools'],
    baseNPCs: ['merchant']
  },
  temple: {
    id: 'temple_base',
    type: 'temple',
    baseDescription: 'A place of worship and ancient rituals.',
    baseLoot: ['relic', 'scroll', 'herbs'],
    baseNPCs: ['priest']
  },
  ruin: {
    id: 'ruin_base',
    type: 'ruin',
    baseDescription: 'Crumbling remains of a forgotten structure.',
    baseLoot: ['artifact', 'bones', 'scrap'],
    baseNPCs: ['scavenger']
  },
  camp: {
    id: 'camp_base',
    type: 'camp',
    baseDescription: 'A temporary encampment with tents and a fire.',
    baseLoot: ['food', 'blanket', 'knife'],
    baseNPCs: ['traveler']
  },
  outpost: {
    id: 'outpost_base',
    type: 'outpost',
    baseDescription: 'A fortified outpost for defense and supply.',
    baseLoot: ['ammo', 'supplies', 'map'],
    baseNPCs: ['guard']
  }
};

export class POITemplates {
  static getTemplate(type: POIType): POITemplate {
    return templates[type];
  }
} 