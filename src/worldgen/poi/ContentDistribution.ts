import { POIModifier } from './types';
import { POIModifiers } from './POIModifiers';

export function selectModifiers(count: number = 1): POIModifier[] {
  const all = POIModifiers.getAll();
  const selected: POIModifier[] = [];
  for (let i = 0; i < count; i++) {
    const idx = Math.floor(Math.random() * all.length);
    selected.push(all[idx]);
  }
  return selected;
} 