import React from 'react';
import { render, screen } from '@testing-library/react';
import ViewportManager from '../../components/ViewportManager';
import { Viewport } from '../../types/common';

describe('ViewportManager', () => {
  it('renders with the correct zoom value and children', () => {
    const viewport: Viewport = {
      offset: { x: 0, y: 0 },
      dimensions: { width: 10, height: 10 },
      zoom: 2,
    };
    render(
      <ViewportManager viewport={viewport}>
        <div data-testid="child">Child Content</div>
      </ViewportManager>
    );
    expect(screen.getByTestId('viewport-manager')).toHaveTextContent('zoom: 2');
    expect(screen.getByTestId('child')).toHaveTextContent('Child Content');
  });
});
