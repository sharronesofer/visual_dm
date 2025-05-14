import React, { useEffect, useRef, useState } from 'react';
import { layerManager, cameraSystem, regionLayer, poiLayer } from '../AnimationLayerSystem';

const LAYERS = [regionLayer, poiLayer];

export default function LayerSystemTestHarness() {
  const [regionVisible, setRegionVisible] = useState(true);
  const [poiVisible, setPoiVisible] = useState(true);
  const [debug, setDebug] = useState(true);
  const [zOrder, setZOrder] = useState(['region', 'poi']);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    regionLayer.setVisibility(regionVisible);
    poiLayer.setVisibility(poiVisible);
    layerManager.setZOrder(zOrder);
  }, [regionVisible, poiVisible, zOrder]);

  // Camera controls
  const pan = (dx: number, dy: number) => cameraSystem.pan(dx, dy);
  const zoom = (z: number) => cameraSystem.zoomTo(z);

  // Z-order controls
  const swapZOrder = () => setZOrder(zOrder.slice().reverse());

  // Debug overlay toggle
  useEffect(() => {
    // This will toggle debug overlay in the main system
    (window as any).debugEnabled = debug;
  }, [debug]);

  return (
    <div>
      <h2>Animation Layer System Test Harness</h2>
      <div style={{ marginBottom: 8 }}>
        <button onClick={() => setRegionVisible(v => !v)}>
          Toggle Region Layer ({regionVisible ? 'On' : 'Off'})
        </button>
        <button onClick={() => setPoiVisible(v => !v)}>
          Toggle POI Layer ({poiVisible ? 'On' : 'Off'})
        </button>
        <button onClick={swapZOrder}>Swap Z-Order</button>
        <button onClick={() => setDebug(d => !d)}>
          Debug Overlay ({debug ? 'On' : 'Off'})
        </button>
      </div>
      <div style={{ marginBottom: 8 }}>
        <button onClick={() => pan(-20, 0)}>Pan Left</button>
        <button onClick={() => pan(20, 0)}>Pan Right</button>
        <button onClick={() => pan(0, -20)}>Pan Up</button>
        <button onClick={() => pan(0, 20)}>Pan Down</button>
        <button onClick={() => zoom(cameraSystem.getState().zoom * 1.1)}>Zoom In</button>
        <button onClick={() => zoom(cameraSystem.getState().zoom / 1.1)}>Zoom Out</button>
      </div>
      <canvas
        id="animation-canvas"
        ref={canvasRef}
        width={800}
        height={600}
        style={{ border: '1px solid #888', background: '#222' }}
      />
    </div>
  );
} 