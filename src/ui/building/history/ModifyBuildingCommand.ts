import { ICommand } from './ICommand';
import { Building, BuildingState, ModifyBuildingPayload } from './types';

export class ModifyBuildingCommand implements ICommand {
    private state: BuildingState;
    private buildingId: string;
    private newData: Partial<Building>;
    private oldData: Partial<Building> | null = null;

    constructor(state: BuildingState, payload: ModifyBuildingPayload) {
        this.state = state;
        this.buildingId = payload.buildingId;
        this.newData = payload.newData;
        if (payload.oldData) {
            this.oldData = payload.oldData;
        }
    }

    execute() {
        const building = this.state.buildings.find(b => b.id === this.buildingId);
        if (building) {
            if (!this.oldData) {
                // Capture old data on first execute
                this.oldData = {};
                for (const key in this.newData) {
                    (this.oldData as any)[key] = (building as any)[key];
                }
            }
            Object.assign(building, this.newData);
        }
    }

    undo() {
        const building = this.state.buildings.find(b => b.id === this.buildingId);
        if (building && this.oldData) {
            Object.assign(building, this.oldData);
        }
    }

    redo() {
        this.execute();
    }
} 