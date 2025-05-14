from typing import Any, Dict



const styles: Record<FactionType, FactionStyle> = {
  guild: Dict[str, Any],
  order: Dict[str, Any],
  syndicate: Dict[str, Any],
  militia: Dict[str, Any],
  cult: Dict[str, Any]
}
class FactionStyles {
  static getStyle(type: FactionType): FactionStyle {
    return styles[type]
  }
} 