import React from 'react';
import { render, screen } from '@testing-library/react';
import {
  ViewportProvider,
  useViewport,
} from '../../components/ViewportContext';

const TestComponent: React.FC = () => {
  const { viewport, setViewport } = useViewport();
  React.useEffect(() => {
    setViewport({
      offset: { x: 5, y: 5 },
      dimensions: { width: 20, height: 20 },
      zoom: 2,
    });
  }, [setViewport]);
  return <div data-testid="viewport-zoom">{viewport.zoom}</div>;
};

describe('ViewportContext', () => {
  it('provides and updates viewport state', () => {
    render(
      <ViewportProvider>
        <TestComponent />
      </ViewportProvider>
    );
    expect(screen.getByTestId('viewport-zoom')).toHaveTextContent('2');
  });
});
