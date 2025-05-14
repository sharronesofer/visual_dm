from typing import Any


class DecorationSystem {
  static generate(type: FactionType): string[] {
    const style = FactionStyles.getStyle(type)
    return style.decor
  }
} 