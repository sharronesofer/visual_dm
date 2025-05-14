import { InteriorParams, Room } from './types';

let roomIdCounter = 0;

function generateRoomId() {
  return `room_${roomIdCounter++}`;
}

export class BSPLayout {
  constructor(private params: InteriorParams) {}

  generateRooms(): Room[] {
    const minRoomSize = 3;
    const rooms: Room[] = [];

    function split(x: number, y: number, width: number, length: number) {
      // Stop splitting if room is too small
      if (width <= minRoomSize * 2 && length <= minRoomSize * 2) {
        rooms.push({
          id: generateRoomId(),
          type: 'generic',
          x,
          y,
          width,
          length
        });
        return;
      }
      // Decide split direction
      const splitVertically = width > length;
      if (splitVertically && width > minRoomSize * 2) {
        // Vertical split
        const splitAt = Math.floor(width / 2);
        split(x, y, splitAt, length);
        split(x + splitAt, y, width - splitAt, length);
      } else if (length > minRoomSize * 2) {
        // Horizontal split
        const splitAt = Math.floor(length / 2);
        split(x, y, width, splitAt);
        split(x, y + splitAt, width, length - splitAt);
      } else {
        // No more splits
        rooms.push({
          id: generateRoomId(),
          type: 'generic',
          x,
          y,
          width,
          length
        });
      }
    }

    split(0, 0, this.params.width, this.params.length);
    return rooms;
  }
} 