import React from 'react';
import { render, fireEvent, act } from '@testing-library/react';
import { PlayerMovement } from '../components/PlayerMovement';
import { Position } from '../types/common';
import { MovementService } from '../services/MovementService';

describe('PlayerMovement Component', () => {
  const mockInitialPosition: Position = { x: 5, y: 5 };
  const mockMapBounds = { width: 10, height: 10 };
  const mockObstacles: Position[] = [
    { x: 6, y: 5 }, // Right of initial position
    { x: 5, y: 6 }, // Below initial position
  ];
  const mockOnMove = jest.fn();

  beforeEach(() => {
    // Reset movement service before each test
    const movementService = MovementService.getInstance();
    movementService.setMapBounds(mockMapBounds);
    movementService.setObstacles(mockObstacles);
    mockOnMove.mockClear();
  });

  test('renders player at initial position', () => {
    const { container } = render(
      <PlayerMovement
        initialPosition={mockInitialPosition}
        mapWidth={mockMapBounds.width}
        mapHeight={mockMapBounds.height}
        obstacles={mockObstacles}
        onMove={mockOnMove}
      />
    );

    const playerElement = container.querySelector('.player');
    expect(playerElement).toBeInTheDocument();
    expect(playerElement).toHaveStyle({
      transform: `translate(${mockInitialPosition.x * 32}px, ${mockInitialPosition.y * 32}px)`,
    });
  });

  test('highlights available moves on hover', async () => {
    const { container } = render(
      <PlayerMovement
        initialPosition={mockInitialPosition}
        mapWidth={mockMapBounds.width}
        mapHeight={mockMapBounds.height}
        obstacles={mockObstacles}
        onMove={mockOnMove}
      />
    );

    const validMovePosition: Position = { x: 4, y: 5 }; // Left of initial position
    const tile = container.querySelector(
      `[data-position="${validMovePosition.x},${validMovePosition.y}"]`
    );

    await act(async () => {
      fireEvent.mouseEnter(tile!);
    });

    expect(tile).toHaveClass('highlight-valid');
  });

  test('shows blocked state for invalid moves', async () => {
    const { container } = render(
      <PlayerMovement
        initialPosition={mockInitialPosition}
        mapWidth={mockMapBounds.width}
        mapHeight={mockMapBounds.height}
        obstacles={mockObstacles}
        onMove={mockOnMove}
      />
    );

    const blockedPosition: Position = { x: 6, y: 5 }; // Position with obstacle
    const tile = container.querySelector(
      `[data-position="${blockedPosition.x},${blockedPosition.y}"]`
    );

    await act(async () => {
      fireEvent.mouseEnter(tile!);
    });

    expect(tile).toHaveClass('highlight-invalid');
  });

  test('executes movement animation on valid move', async () => {
    const { container } = render(
      <PlayerMovement
        initialPosition={mockInitialPosition}
        mapWidth={mockMapBounds.width}
        mapHeight={mockMapBounds.height}
        obstacles={mockObstacles}
        onMove={mockOnMove}
      />
    );

    const validMovePosition: Position = { x: 4, y: 5 }; // Left of initial position
    const tile = container.querySelector(
      `[data-position="${validMovePosition.x},${validMovePosition.y}"]`
    );

    await act(async () => {
      fireEvent.click(tile!);
    });

    const playerElement = container.querySelector('.player');
    expect(playerElement).toHaveClass('moving');
    expect(playerElement).toHaveStyle({
      transition: 'transform 0.3s ease-in-out',
    });

    // Wait for animation to complete
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 300));
    });

    expect(mockOnMove).toHaveBeenCalledWith(validMovePosition);
    expect(playerElement).not.toHaveClass('moving');
  });

  test('updates movement points after successful move', async () => {
    const { container } = render(
      <PlayerMovement
        initialPosition={mockInitialPosition}
        mapWidth={mockMapBounds.width}
        mapHeight={mockMapBounds.height}
        obstacles={mockObstacles}
        onMove={mockOnMove}
      />
    );

    const validMovePosition: Position = { x: 4, y: 5 }; // Left of initial position
    const tile = container.querySelector(
      `[data-position="${validMovePosition.x},${validMovePosition.y}"]`
    );

    const initialPoints =
      container.querySelector('.movement-points')?.textContent;

    await act(async () => {
      fireEvent.click(tile!);
    });

    // Wait for animation to complete
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 300));
    });

    const updatedPoints =
      container.querySelector('.movement-points')?.textContent;
    expect(Number(updatedPoints)).toBeLessThan(Number(initialPoints));
  });

  test('shows path preview on hover', async () => {
    const { container } = render(
      <PlayerMovement
        initialPosition={mockInitialPosition}
        mapWidth={mockMapBounds.width}
        mapHeight={mockMapBounds.height}
        obstacles={mockObstacles}
        onMove={mockOnMove}
      />
    );

    const targetPosition: Position = { x: 4, y: 4 }; // Diagonal move
    const tile = container.querySelector(
      `[data-position="${targetPosition.x},${targetPosition.y}"]`
    );

    await act(async () => {
      fireEvent.mouseEnter(tile!);
    });

    const pathTiles = container.querySelectorAll('.path-preview');
    expect(pathTiles.length).toBeGreaterThan(0);
    pathTiles.forEach(tile => {
      expect(tile).toHaveClass('path-preview');
    });
  });

  test('clears path preview on mouse leave', async () => {
    const { container } = render(
      <PlayerMovement
        initialPosition={mockInitialPosition}
        mapWidth={mockMapBounds.width}
        mapHeight={mockMapBounds.height}
        obstacles={mockObstacles}
        onMove={mockOnMove}
      />
    );

    const targetPosition: Position = { x: 4, y: 4 }; // Diagonal move
    const tile = container.querySelector(
      `[data-position="${targetPosition.x},${targetPosition.y}"]`
    );

    await act(async () => {
      fireEvent.mouseEnter(tile!);
      fireEvent.mouseLeave(tile!);
    });

    const pathTiles = container.querySelectorAll('.path-preview');
    expect(pathTiles.length).toBe(0);
  });
});
