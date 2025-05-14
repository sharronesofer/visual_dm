import React, { useRef, useEffect, useCallback } from 'react';
import styled from 'styled-components';
import { ViewportManagerProps } from '../types/props';
import { Position } from '../types/common';

const Container = styled.div`
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  touch-action: none;
`;

interface ViewportContainerProps {
  x: number;
  y: number;
  zoom: number;
}

const ViewportContainer = styled.div<ViewportContainerProps>`
  position: absolute;
  transform-origin: top left;
  transform: translate(${(props: ViewportContainerProps) => props.x}px, ${(props: ViewportContainerProps) => props.y}px) scale(${(props: ViewportContainerProps) => props.zoom});
  will-change: transform;
`;

const ViewportManager: React.FC<ViewportManagerProps> = ({
  children,
  state,
  onStateChange,
  onDrag,
  onZoom,
  className
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const isDragging = useRef(false);
  const lastPosition = useRef<Position>({ x: 0, y: 0 });
  const lastTouch = useRef<{ x: number; y: number; scale: number } | null>(null);

  const handleResize = useCallback(() => {
    if (containerRef.current) {
      const { width, height } = containerRef.current.getBoundingClientRect();
      onStateChange({
        ...state,
        dimensions: { width, height }
      });
    }
  }, [state, onStateChange]);

  useEffect(() => {
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [handleResize]);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (e.button === 0) { // Left click only
      isDragging.current = true;
      lastPosition.current = { x: e.clientX, y: e.clientY };
    }
  }, []);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!isDragging.current) return;

    const dx = e.clientX - lastPosition.current.x;
    const dy = e.clientY - lastPosition.current.y;
    lastPosition.current = { x: e.clientX, y: e.clientY };

    const newOffset = {
      x: state.offset.x + dx,
      y: state.offset.y + dy
    };

    onStateChange({
      ...state,
      offset: newOffset
    });
    onDrag?.(newOffset);
  }, [state, onStateChange, onDrag]);

  const handleMouseUp = useCallback(() => {
    isDragging.current = false;
  }, []);

  const handleWheel = useCallback((e: React.WheelEvent) => {
    e.preventDefault();
    const zoomFactor = 0.001;
    const delta = -e.deltaY;
    const newZoom = Math.max(0.1, Math.min(5, state.zoom + delta * zoomFactor));

    if (newZoom !== state.zoom) {
      onStateChange({
        ...state,
        zoom: newZoom
      });
      onZoom?.(newZoom);
    }
  }, [state, onStateChange, onZoom]);

  const handleTouchStart = useCallback((e: React.TouchEvent) => {
    if (e.touches.length === 2) {
      const touch1 = e.touches.item(0);
      const touch2 = e.touches.item(1);
      if (!touch1 || !touch2) return;

      const centerX = (touch1.clientX + touch2.clientX) / 2;
      const centerY = (touch1.clientY + touch2.clientY) / 2;
      const distance = Math.hypot(
        touch1.clientX - touch2.clientX,
        touch1.clientY - touch2.clientY
      );
      lastTouch.current = { x: centerX, y: centerY, scale: distance };
    } else if (e.touches.length === 1) {
      const touch = e.touches.item(0);
      if (!touch) return;
      
      lastPosition.current = { x: touch.clientX, y: touch.clientY };
      isDragging.current = true;
    }
  }, []);

  const handleTouchMove = useCallback((e: React.TouchEvent) => {
    e.preventDefault();
    if (e.touches.length === 2 && lastTouch.current) {
      const touch1 = e.touches.item(0);
      const touch2 = e.touches.item(1);
      if (!touch1 || !touch2) return;

      const centerX = (touch1.clientX + touch2.clientX) / 2;
      const centerY = (touch1.clientY + touch2.clientY) / 2;
      const distance = Math.hypot(
        touch1.clientX - touch2.clientX,
        touch1.clientY - touch2.clientY
      );

      const scaleDiff = distance / lastTouch.current.scale;
      const newZoom = Math.max(0.1, Math.min(5, state.zoom * scaleDiff));

      const dx = centerX - lastTouch.current.x;
      const dy = centerY - lastTouch.current.y;

      lastTouch.current = { x: centerX, y: centerY, scale: distance };

      onStateChange({
        ...state,
        zoom: newZoom,
        offset: {
          x: state.offset.x + dx,
          y: state.offset.y + dy
        }
      });
    } else if (e.touches.length === 1 && isDragging.current) {
      const touch = e.touches.item(0);
      if (!touch) return;

      const dx = touch.clientX - lastPosition.current.x;
      const dy = touch.clientY - lastPosition.current.y;
      lastPosition.current = { x: touch.clientX, y: touch.clientY };

      const newOffset = {
        x: state.offset.x + dx,
        y: state.offset.y + dy
      };

      onStateChange({
        ...state,
        offset: newOffset
      });
      onDrag?.(newOffset);
    }
  }, [state, onStateChange, onDrag]);

  const handleTouchEnd = useCallback(() => {
    isDragging.current = false;
    lastTouch.current = null;
  }, []);

  return (
    <Container
      ref={containerRef}
      className={className}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
      onWheel={handleWheel}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
    >
      <ViewportContainer
        x={state.offset.x}
        y={state.offset.y}
        zoom={state.zoom}
      >
        {children}
      </ViewportContainer>
    </Container>
  );
};

export default ViewportManager; 