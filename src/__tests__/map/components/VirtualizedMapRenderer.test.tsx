import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { VirtualizedMapRenderer } from '../../components/VirtualizedMapRenderer';
import { useMapStore } from '../../store/mapStore';
import { Position } from '../../types/common';

// Mock the mapStore
jest.mock('../../store/mapStore', () => ({
  useMapStore: jest.fn(),
}));

interface MockTile {
  type: 'grass' | 'water' | 'mountain' | 'forest';
}

interface MockChunk {
  tiles: Record<string, MockTile>;
}

describe('VirtualizedMapRenderer', () => {
  const mockStore = {
    playerPosition: { x: 0, y: 0 },
    visibleArea: [
      { x: 0, y: 0 },
      { x: 1, y: 0 },
      { x: 0, y: 1 },
      { x: 1, y: 1 },
    ],
    getChunk: jest.fn().mockReturnValue({
      tiles: {
        '0,0': { type: 'grass' },
        '1,0': { type: 'water' },
        '0,1': { type: 'mountain' },
        '1,1': { type: 'forest' },
      },
    } as MockChunk),
  };

  beforeEach(() => {
    (useMapStore as unknown as jest.Mock).mockReturnValue(mockStore);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders the correct number of tiles', () => {
    render(<VirtualizedMapRenderer width={200} height={200} tileSize={50} />);

    // With a 200x200 viewport and 50px tiles, we should see 4x4 tiles
    // plus overscan (default 5), so 9x9 tiles total
    const tiles = screen.getAllByTestId(/^tile-/);
    expect(tiles.length).toBe(81);
  });

  it('renders player marker on player position', () => {
    render(<VirtualizedMapRenderer width={200} height={200} tileSize={50} />);

    const playerTile = screen.getByTestId('tile-0-0');
    expect(playerTile).toBeInTheDocument();
    expect(playerTile.querySelector('.player-marker')).toBeInTheDocument();
  });

  it('calls onTileClick when a tile is clicked', () => {
    const onTileClick = jest.fn();
    render(
      <VirtualizedMapRenderer
        width={200}
        height={200}
        tileSize={50}
        onTileClick={onTileClick}
      />
    );

    const tile = screen.getByTestId('tile-1-0');
    fireEvent.click(tile);
    expect(onTileClick).toHaveBeenCalledWith({ x: 1, y: 0 });
  });

  it('renders tiles with correct visibility', () => {
    render(<VirtualizedMapRenderer width={200} height={200} tileSize={50} />);

    // Check visible tiles
    mockStore.visibleArea.forEach(({ x, y }) => {
      const tile = screen.getByTestId(`tile-${x}-${y}`);
      expect(tile).toHaveStyle({ opacity: '1' });
    });

    // Check invisible tile
    const invisibleTile = screen.getByTestId('tile-2-2');
    expect(invisibleTile).toHaveStyle({ opacity: '0.1' });
  });

  it('renders tiles with correct terrain types', () => {
    render(<VirtualizedMapRenderer width={200} height={200} tileSize={50} />);

    const terrainColors = {
      grass: 'rgb(144, 238, 144)',
      water: 'rgb(135, 206, 235)',
      mountain: 'rgb(160, 82, 45)',
      forest: 'rgb(34, 139, 34)',
    };

    const chunk = mockStore.getChunk() as MockChunk;
    Object.entries(chunk.tiles).forEach(([pos, tile]) => {
      const [x, y] = pos.split(',').map(Number);
      const element = screen.getByTestId(`tile-${x}-${y}`);
      expect(element).toHaveStyle({
        backgroundColor: terrainColors[tile.type],
      });
    });
  });
});
