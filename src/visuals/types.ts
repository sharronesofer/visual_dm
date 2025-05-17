// types.ts
// Shared types for visual systems (OverlayManager, DamageVisualSystem, SpriteRegistry)

export interface Point {
    x: number;
    y: number;
}

export interface Size {
    width: number;
    height: number;
}

export interface BuildingVisualInfo {
    id: string;
    position: Point;
    size: Size;
    // Optionally add more fields as needed (e.g., orientation, module info)
} 