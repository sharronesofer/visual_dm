import React from 'react';
import { render, screen } from '@testing-library/react';
import RegionLayer from '../../components/RegionLayer';
import { Region } from '../../types/map';
import { Viewport } from '../../types/common';

describe('RegionLayer', () => {
  it('renders with the correct number of regions', () => {
    const regions: Region[] = [
      {
        id: '1',
        position: { x: 0, y: 0 },
        type: 'test',
        terrainType: 'plains',
        borders: [],
        pois: [],
        discovered: true,
        visible: true,
      },
      {
        id: '2',
        position: { x: 1, y: 1 },
        type: 'test',
        terrainType: 'forest',
        borders: [],
        pois: [],
        discovered: false,
        visible: false,
      },
    ];
    const viewport: Viewport = {
      offset: { x: 0, y: 0 },
      dimensions: { width: 10, height: 10 },
      zoom: 1,
    };
    render(<RegionLayer regions={regions} viewport={viewport} />);
    expect(screen.getByTestId('region-layer')).toHaveTextContent('regions: 2');
  });
});
