from typing import Any


class ResizeObserverMock implements ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}
window.ResizeObserver = ResizeObserverMock as unknown as typeof ResizeObserver
const IntersectionObserverMock = vi.fn().mockImplementation(callback => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
  takeRecords: vi.fn(),
  root: null,
  rootMargin: '',
  thresholds: [],
}))
window.IntersectionObserver = IntersectionObserverMock as unknown as typeof IntersectionObserver
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
  key: vi.fn(),
  length: 0,
}
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
})
const canvasContextMock = {
  fillRect: vi.fn(),
  clearRect: vi.fn(),
  getImageData: vi.fn(() => ({
    data: new Array(4),
  })),
  putImageData: vi.fn(),
  createImageData: vi.fn(),
  setTransform: vi.fn(),
  drawImage: vi.fn(),
  save: vi.fn(),
  restore: vi.fn(),
  scale: vi.fn(),
  rotate: vi.fn(),
  translate: vi.fn(),
  transform: vi.fn(),
  beginPath: vi.fn(),
  moveTo: vi.fn(),
  lineTo: vi.fn(),
  closePath: vi.fn(),
  stroke: vi.fn(),
  fill: vi.fn(),
  canvas: document.createElement('canvas'),
} as unknown as CanvasRenderingContext2D
const getContextMock = vi.fn((contextId: str, _options?: Any) => {
  switch (contextId) {
    case '2d':
      return canvasContextMock
    case 'bitmaprenderer':
      return null
    case 'webgl':
    case 'webgl2':
      return null
    default:
      return null
  }
})
HTMLCanvasElement.prototype.getContext =
  getContextMock as typeof HTMLCanvasElement.prototype.getContext