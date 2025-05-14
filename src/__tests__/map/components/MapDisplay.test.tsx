import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { MapDisplay } from '../../components/MapDisplay';
import { useMapStore } from '../../store/mapStore';
import { MapService } from '../../services/MapService';

// Mock dependencies
jest.mock('../../store/mapStore', () => ({
  useMapStore: jest.fn(),
}));

jest.mock('../../services/MapService', () => ({
  MapService: {
    getInstance: jest.fn(),
  },
}));

jest.mock('../../components/VirtualizedMapRenderer', () => ({
  VirtualizedMapRenderer: ({ width, height, tileSize, onTileClick }: any) => (
    <div
      data-testid="virtualized-map-renderer"
      data-props={JSON.stringify({ width, height, tileSize })}
    >
      <div
        data-testid="mock-tile"
        onClick={() => onTileClick?.({ x: 1, y: 1 })}
      />
    </div>
  ),
}));

describe('MapDisplay', () => {
  const mockGetMapData = jest.fn();
  const mockStore = {
    playerPosition: { x: 0, y: 0 },
    error: null,
    setError: jest.fn(),
  };

  beforeEach(() => {
    (useMapStore as unknown as jest.Mock).mockReturnValue(mockStore);
    (MapService.getInstance as jest.Mock).mockReturnValue({
      getMapData: mockGetMapData,
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders VirtualizedMapRenderer with correct props', () => {
    render(<MapDisplay width={800} height={600} tileSize={32} />);

    const renderer = screen.getByTestId('virtualized-map-renderer');
    const props = JSON.parse(renderer.getAttribute('data-props') || '{}');

    expect(props).toEqual({
      width: 800,
      height: 600,
      tileSize: 32,
    });
  });

  it('updates map data when player position changes', () => {
    render(<MapDisplay width={800} height={600} tileSize={32} />);

    expect(mockGetMapData).toHaveBeenCalledWith(mockStore.playerPosition);
  });

  it('displays error message when there is an error', () => {
    const errorMessage = 'Failed to load map data';
    (useMapStore as unknown as jest.Mock).mockReturnValue({
      ...mockStore,
      error: errorMessage,
    });

    render(<MapDisplay width={800} height={600} tileSize={32} />);

    expect(
      screen.getByText(`Error loading map: ${errorMessage}`)
    ).toBeInTheDocument();
  });

  it('calls onTileClick when a tile is clicked', () => {
    const onTileClick = jest.fn();
    render(
      <MapDisplay
        width={800}
        height={600}
        tileSize={32}
        onTileClick={onTileClick}
      />
    );

    const tile = screen.getByTestId('mock-tile');
    fireEvent.click(tile);

    expect(onTileClick).toHaveBeenCalledWith({ x: 1, y: 1 });
  });

  it('handles map update errors', async () => {
    const error = new Error('Network error');
    mockGetMapData.mockRejectedValueOnce(error);

    render(<MapDisplay width={800} height={600} tileSize={32} />);

    expect(mockStore.setError).toHaveBeenCalledWith(error.message);
  });
});
