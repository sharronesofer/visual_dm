from typing import Any


const templates: Record<BuildingType, Partial<Room>[]> = {
  residential: [
    { type: 'bedroom' },
    { type: 'kitchen' },
    { type: 'bathroom' },
    { type: 'living_room' }
  ],
  commercial: [
    { type: 'office' },
    { type: 'meeting_room' },
    { type: 'reception' },
    { type: 'restroom' }
  ],
  industrial: [
    { type: 'workshop' },
    { type: 'storage' },
    { type: 'office' },
    { type: 'break_room' }
  ]
}
class BuildingTemplates {
  static getTemplates(type: BuildingType): Partial<Room>[] {
    return templates[type] || []
  }
} 