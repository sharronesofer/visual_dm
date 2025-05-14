import { POIType, POIContent } from './types';
import { POITemplates } from './POITemplates';
import { selectModifiers } from './ContentDistribution';

export class POIGenerator {
  generate(type: POIType): POIContent {
    const template = POITemplates.getTemplate(type);
    const modifiers = selectModifiers(2); // Pick 2 random modifiers for demo
    let loot = [...template.baseLoot];
    let npcs = [...template.baseNPCs];
    let tags: string[] = [];
    modifiers.forEach(mod => {
      if (mod.lootModifier) loot = mod.lootModifier(loot);
      if (mod.npcModifier) npcs = mod.npcModifier(npcs);
      if (mod.questHook) tags.push(mod.questHook);
    });
    return {
      template,
      modifiers,
      loot,
      npcs,
      tags
    };
  }
} 