import React, { useMemo } from 'react';
import styled from 'styled-components';
import { TileLayerProps, TileProps } from '../types/props';
import { Position, TerrainType } from '../types/common';
import { TileState } from '../types/state';

const TILE_SIZE = 64; // pixels

interface TileContainerProps {
  x: number;
  y: number;
}

const TileContainer = styled.div<TileContainerProps>`
  position: absolute;
  width: ${TILE_SIZE}px;
  height: ${TILE_SIZE}px;
  transform: translate(${(props: TileContainerProps) => props.x * TILE_SIZE}px, ${(props: TileContainerProps) => props.y * TILE_SIZE}px);
  transition: background-color 0.2s ease;
  border: 1px solid rgba(0, 0, 0, 0.1);
  box-sizing: border-box;
`;

const terrainColors: Record<TerrainType, string> = {
  plains: '#90a955',
  forest: '#386641',
  mountain: '#6d6875',
  water: '#48cae4',
  desert: '#e9c46a',
  swamp: '#4a4e69'
};

const Tile: React.FC<TileProps> = ({
  state,
  selected,
  hovered,
  onClick,
  onHover,
  className
}) => {
  const StyledTile = styled(TileContainer)`
    background-color: ${props => terrainColors[state.terrainType]};
    opacity: ${state.visible ? 1 : state.discovered ? 0.7 : 0.4};
    cursor: pointer;
    
    &:hover {
      filter: brightness(1.1);
    }
    
    ${selected && `
      box-shadow: inset 0 0 0 2px #ffd700;
      z-index: 1;
    `}
    
    ${hovered && `
      filter: brightness(1.2);
      z-index: 2;
    `}
    
    ${state.poi && `
      &::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 12px;
        height: 12px;
        background: #fff;
        border-radius: 50%;
        transform: translate(-50%, -50%);
        box-shadow: 0 0 4px rgba(0, 0, 0, 0.3);
      }
    `}
  `;

  return (
    <StyledTile
      x={state.position.x}
      y={state.position.y}
      className={className}
      onClick={onClick}
      onMouseEnter={onHover}
    />
  );
};

interface VisibleTile {
  key: string;
  tile: TileState;
}

const TileLayer: React.FC<TileLayerProps> = ({
  tiles,
  viewport,
  onTileClick,
  onTileHover,
  selectedTile,
  hoveredTile,
  className
}) => {
  const visibleTiles = useMemo(() => {
    const tileKeys = Object.keys(tiles);
    return tileKeys.reduce<VisibleTile[]>((acc, key) => {
      const tile = tiles[key];
      if (!tile) return acc;

      const tileLeft = tile.position.x * TILE_SIZE;
      const tileTop = tile.position.y * TILE_SIZE;
      const tileRight = tileLeft + TILE_SIZE;
      const tileBottom = tileTop + TILE_SIZE;

      const viewLeft = -viewport.offset.x / viewport.zoom;
      const viewTop = -viewport.offset.y / viewport.zoom;
      const viewRight = viewLeft + viewport.dimensions.width / viewport.zoom;
      const viewBottom = viewTop + viewport.dimensions.height / viewport.zoom;

      if (
        tileRight >= viewLeft &&
        tileLeft <= viewRight &&
        tileBottom >= viewTop &&
        tileTop <= viewBottom
      ) {
        acc.push({ key, tile });
      }

      return acc;
    }, []);
  }, [tiles, viewport]);

  return (
    <>
      {visibleTiles.map(({ key, tile }) => {
        const isSelected = selectedTile && 
          selectedTile.x === tile.position.x && 
          selectedTile.y === tile.position.y;
        const isHovered = hoveredTile && 
          hoveredTile.x === tile.position.x && 
          hoveredTile.y === tile.position.y;

        return (
          <Tile
            key={key}
            state={tile}
            selected={isSelected}
            hovered={isHovered}
            onClick={() => onTileClick?.(tile.position)}
            onHover={() => onTileHover?.(tile.position)}
            className={className}
          />
        );
      })}
    </>
  );
};

export default TileLayer; 