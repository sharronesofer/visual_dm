from typing import Any, Dict


const templates: Record<POIType, POITemplate> = {
  shop: Dict[str, Any],
  temple: Dict[str, Any],
  ruin: Dict[str, Any],
  camp: Dict[str, Any],
  outpost: Dict[str, Any]
}
class POITemplates {
  static getTemplate(type: POIType): POITemplate {
    return templates[type]
  }
} 