from typing import Any, List



let roomIdCounter = 0
function generateRoomId() {
  return `room_${roomIdCounter++}`
}
class BSPLayout {
  constructor(private params: InteriorParams) {}
  generateRooms(): Room[] {
    const minRoomSize = 3
    const rooms: List[Room] = []
    function split(x: float, y: float, width: float, length: float) {
      if (width <= minRoomSize * 2 && length <= minRoomSize * 2) {
        rooms.push({
          id: generateRoomId(),
          type: 'generic',
          x,
          y,
          width,
          length
        })
        return
      }
      const splitVertically = width > length
      if (splitVertically && width > minRoomSize * 2) {
        const splitAt = Math.floor(width / 2)
        split(x, y, splitAt, length)
        split(x + splitAt, y, width - splitAt, length)
      } else if (length > minRoomSize * 2) {
        const splitAt = Math.floor(length / 2)
        split(x, y, width, splitAt)
        split(x, y + splitAt, width, length - splitAt)
      } else {
        rooms.push({
          id: generateRoomId(),
          type: 'generic',
          x,
          y,
          width,
          length
        })
      }
    }
    split(0, 0, this.params.width, this.params.length)
    return rooms
  }
} 