import React from 'react';
import { render, screen } from '@testing-library/react';
import { RegionProvider, useRegions } from '../../components/RegionContext';
import type { Region } from '../../types/map';

const TestComponent: React.FC = () => {
  const { regions, setRegions } = useRegions();
  React.useEffect(() => {
    setRegions([
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
    ]);
  }, [setRegions]);
  return <div data-testid="region-count">{regions.length}</div>;
};

describe('RegionContext', () => {
  it('provides and updates region state', () => {
    render(
      <RegionProvider>
        <TestComponent />
      </RegionProvider>
    );
    expect(screen.getByTestId('region-count')).toHaveTextContent('1');
  });
});
