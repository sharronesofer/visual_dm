import {
  latLngToPixel,
  isBoundingBoxInViewport,
  getPixelSizeAtZoom,
  Viewport,
} from '../coordinateTransform';

describe('coordinateTransform', () => {
  const viewport: Viewport = {
    center: [0, 0],
    zoom: 1,
    rotation: 0,
    width: 800,
    height: 600,
  };

  it('latLngToPixel returns center for (0,0)', () => {
    const result = latLngToPixel(0, 0, viewport);
    expect(result.x).toBeCloseTo(400);
    expect(result.y).toBeCloseTo(300);
  });

  it('latLngToPixel returns correct direction for north/east', () => {
    const north = latLngToPixel(10, 0, viewport);
    const east = latLngToPixel(0, 10, viewport);
    expect(north.y).toBeLessThan(300); // North is up
    expect(east.x).toBeGreaterThan(400); // East is right
  });

  it('latLngToPixel handles rotation', () => {
    const rotatedViewport = { ...viewport, rotation: 90 };
    const point = latLngToPixel(0, 10, rotatedViewport);
    expect(point.y).toBeGreaterThan(300); // After 90° rotation, east becomes south
  });

  it('isBoundingBoxInViewport returns true for box at center', () => {
    expect(isBoundingBoxInViewport(-1, -1, 1, 1, viewport)).toBe(true);
  });

  it('isBoundingBoxInViewport returns false for far away box', () => {
    expect(isBoundingBoxInViewport(80, 170, 85, 175, viewport)).toBe(false);
  });

  it('getPixelSizeAtZoom returns expected value', () => {
    expect(getPixelSizeAtZoom(viewport)).toBeCloseTo(
      (800 / 360) * Math.pow(2, 1)
    );
  });
});
