from typing import Any, List


class FactionHQGenerator {
  generate(type: FactionType): FactionHQLayout {
    const style = FactionStyles.getStyle(type)
    const roomTemplates = RoomTypes.getForFaction(type)
    const rooms: List[FactionRoom] = roomTemplates.map((tpl, i) => ({
      id: `${tpl.type}_${i}`,
      type: tpl.type || 'generic',
      x: i * 5,
      y: i * 5,
      width: 8 + i,
      length: 10 + i,
      specialPurpose: tpl.specialPurpose
    }))
    const npcs = NPCPopulation.generate(type)
    const security = SecuritySystem.generate(type, rooms.length * 10)
    const decor = DecorationSystem.generate(type)
    return {
      rooms,
      npcs,
      security,
      style,
      decor
    }
  }
} 