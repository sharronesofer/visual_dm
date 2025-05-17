// types.ts
export interface Building {
    id: string;
    type: string;
    position: { x: number; y: number; z: number };
    rotation: { x: number; y: number; z: number; w: number };
    [key: string]: any;
}

export interface BuildingState {
    buildings: Building[];
}

export interface PlaceBuildingPayload {
    building: Building;
}

export interface RemoveBuildingPayload {
    buildingId: string;
}

export interface ModifyBuildingPayload {
    buildingId: string;
    newData: Partial<Building>;
    oldData?: Partial<Building>;
} 