import { BuildingModule, ModuleState } from './BuildingModule';
import { FacadeModule } from './FacadeModule';
import { RoofModule } from './RoofModule';
import { WallModule } from './WallModule';
import { FoundationModule } from './FoundationModule';
import { InteriorModule } from './InteriorModule';
import { Position } from '../../core/interfaces/types/common';
import { MaterialType } from '../../core/interfaces/types/building';
import { FloorModule } from './FloorModule';
import { ColumnModule } from './ColumnModule';
import { BeamModule } from './BeamModule';
import { StairModule } from './StairModule';
import { FurnitureModule } from './FurnitureModule';
import { PartitionModule } from './PartitionModule';

export type ModuleConfig = {
    moduleId: string;
    type: string;
    position: Position;
    maxHealth: number;
    material: MaterialType;
    deteriorationRate: number;
    repairRate: number;
    // Optional type-specific properties
    [key: string]: any;
};

export class ModuleFactory {
    static createModule(config: ModuleConfig): BuildingModule {
        switch (config.type) {
            case 'facade':
                return new FacadeModule(
                    config.moduleId,
                    config.position,
                    config.maxHealth,
                    config.material,
                    config.deteriorationRate,
                    config.repairRate,
                    config.style || 'default'
                );
            case 'roof':
                return new RoofModule(
                    config.moduleId,
                    config.position,
                    config.maxHealth,
                    config.material,
                    config.deteriorationRate,
                    config.repairRate,
                    config.slope || 30
                );
            case 'wall':
                return new WallModule(
                    config.moduleId,
                    config.position,
                    config.maxHealth,
                    config.material,
                    config.deteriorationRate,
                    config.repairRate,
                    config.thickness || 1,
                    config.height || 3,
                    config.isLoadBearing || false
                );
            case 'foundation':
                return new FoundationModule(
                    config.moduleId,
                    config.position,
                    config.maxHealth,
                    config.material,
                    config.deteriorationRate,
                    config.repairRate,
                    config.depth || 1,
                    config.materialStrength || 1
                );
            case 'interior':
                return new InteriorModule(
                    config.moduleId,
                    config.position,
                    config.maxHealth,
                    config.material,
                    config.deteriorationRate,
                    config.repairRate,
                    config.roomType || 'generic'
                );
            case 'floor':
                return new FloorModule(
                    config.moduleId,
                    config.position,
                    config.maxHealth,
                    config.material,
                    config.deteriorationRate,
                    config.repairRate,
                    config.thickness,
                    config.area,
                    config.supportColumns
                );
            case 'column':
                return new ColumnModule(
                    config.moduleId,
                    config.position,
                    config.maxHealth,
                    config.material,
                    config.deteriorationRate,
                    config.repairRate,
                    config.height,
                    config.radius,
                    config.loadCapacity
                );
            case 'beam':
                return new BeamModule(
                    config.moduleId,
                    config.position,
                    config.maxHealth,
                    config.material,
                    config.deteriorationRate,
                    config.repairRate,
                    config.length,
                    config.crossSection,
                    config.loadCapacity
                );
            case 'stair':
                return new StairModule(
                    config.moduleId,
                    config.position,
                    config.maxHealth,
                    config.material,
                    config.deteriorationRate,
                    config.repairRate,
                    config.width,
                    config.height,
                    config.steps,
                    config.connects
                );
            case 'furniture':
                return new FurnitureModule(
                    config.moduleId,
                    config.position,
                    config.maxHealth,
                    config.material,
                    config.deteriorationRate,
                    config.repairRate,
                    config.furnitureType,
                    config.dimensions,
                    config.isMovable
                );
            case 'partition':
                return new PartitionModule(
                    config.moduleId,
                    config.position,
                    config.maxHealth,
                    config.material,
                    config.deteriorationRate,
                    config.repairRate,
                    config.thickness,
                    config.height,
                    config.isMovable,
                    config.hasDoorway,
                    config.hasWindow
                );
            default:
                throw new Error(`Unknown module type: ${config.type}`);
        }
    }

    static serializeModule(module: BuildingModule): any {
        return module.serialize();
    }

    static deserializeModule(data: any): BuildingModule {
        // Use the type field to instantiate the correct module class
        return this.createModule({ ...data });
    }

    static deserialize(data: any): BuildingModule {
        switch (data.type) {
            case 'roof':
                return new RoofModule(
                    data.moduleId,
                    data.position,
                    data.maxHealth,
                    data.material,
                    data.deteriorationRate,
                    data.repairRate,
                    data.slope
                );
            case 'floor':
                return new FloorModule(
                    data.moduleId,
                    data.position,
                    data.maxHealth,
                    data.material,
                    data.deteriorationRate,
                    data.repairRate,
                    data.thickness,
                    data.area,
                    data.supportColumns
                );
            case 'column':
                return new ColumnModule(
                    data.moduleId,
                    data.position,
                    data.maxHealth,
                    data.material,
                    data.deteriorationRate,
                    data.repairRate,
                    data.height,
                    data.radius,
                    data.loadCapacity
                );
            case 'beam':
                return new BeamModule(
                    data.moduleId,
                    data.position,
                    data.maxHealth,
                    data.material,
                    data.deteriorationRate,
                    data.repairRate,
                    data.length,
                    data.crossSection,
                    data.loadCapacity
                );
            case 'stair':
                return new StairModule(
                    data.moduleId,
                    data.position,
                    data.maxHealth,
                    data.material,
                    data.deteriorationRate,
                    data.repairRate,
                    data.width,
                    data.height,
                    data.steps,
                    data.connects
                );
            case 'furniture':
                return new FurnitureModule(
                    data.moduleId,
                    data.position,
                    data.maxHealth,
                    data.material,
                    data.deteriorationRate,
                    data.repairRate,
                    data.furnitureType,
                    data.dimensions,
                    data.isMovable
                );
            case 'partition':
                return new PartitionModule(
                    data.moduleId,
                    data.position,
                    data.maxHealth,
                    data.material,
                    data.deteriorationRate,
                    data.repairRate,
                    data.thickness,
                    data.height,
                    data.isMovable,
                    data.hasDoorway,
                    data.hasWindow
                );
            default:
                throw new Error(`Unknown module type: ${data.type}`);
        }
    }
} 