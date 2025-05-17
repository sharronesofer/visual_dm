import { ICommand } from './ICommand';
import { Building, BuildingState, PlaceBuildingPayload } from './types';

export class PlaceBuildingCommand implements ICommand {
    private state: BuildingState;
    private building: Building;

    constructor(state: BuildingState, payload: PlaceBuildingPayload) {
        this.state = state;
        this.building = payload.building;
    }

    execute() {
        this.state.buildings.push(this.building);
    }

    undo() {
        this.state.buildings = this.state.buildings.filter(b => b.id !== this.building.id);
    }

    redo() {
        this.execute();
    }
} 