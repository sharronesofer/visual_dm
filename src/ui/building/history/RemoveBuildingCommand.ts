import { ICommand } from './ICommand';
import { Building, BuildingState, RemoveBuildingPayload } from './types';

export class RemoveBuildingCommand implements ICommand {
    private state: BuildingState;
    private buildingId: string;
    private removedBuilding: Building | null = null;

    constructor(state: BuildingState, payload: RemoveBuildingPayload) {
        this.state = state;
        this.buildingId = payload.buildingId;
    }

    execute() {
        const idx = this.state.buildings.findIndex(b => b.id === this.buildingId);
        if (idx !== -1) {
            this.removedBuilding = this.state.buildings[idx];
            this.state.buildings.splice(idx, 1);
        }
    }

    undo() {
        if (this.removedBuilding) {
            this.state.buildings.push(this.removedBuilding);
        }
    }

    redo() {
        this.execute();
    }
} 