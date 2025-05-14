import { FactionType } from './types';
import { FactionStyles } from './FactionStyles';

export class DecorationSystem {
  static generate(type: FactionType): string[] {
    const style = FactionStyles.getStyle(type);
    // For demo, just return all decor items
    return style.decor;
  }
} 