from typing import Any



const roomTypes: Record<FactionType, Partial<FactionRoom>[]> = {
  guild: [
    { type: 'meeting_hall', specialPurpose: 'leadership' },
    { type: 'workshop', specialPurpose: 'crafting' },
    { type: 'library', specialPurpose: 'research' }
  ],
  order: [
    { type: 'chapel', specialPurpose: 'worship' },
    { type: 'archive', specialPurpose: 'records' },
    { type: 'cloister', specialPurpose: 'meditation' }
  ],
  syndicate: [
    { type: 'vault', specialPurpose: 'treasure' },
    { type: 'secret_room', specialPurpose: 'planning' },
    { type: 'escape_tunnel', specialPurpose: 'escape' }
  ],
  militia: [
    { type: 'armory', specialPurpose: 'weapons' },
    { type: 'barracks', specialPurpose: 'rest' },
    { type: 'training_ground', specialPurpose: 'training' }
  ],
  cult: [
    { type: 'ritual_chamber', specialPurpose: 'ritual' },
    { type: 'catacombs', specialPurpose: 'burial' },
    { type: 'altar', specialPurpose: 'sacrifice' }
  ]
}
class RoomTypes {
  static getForFaction(type: FactionType): Partial<FactionRoom>[] {
    return roomTypes[type] || []
  }
} 