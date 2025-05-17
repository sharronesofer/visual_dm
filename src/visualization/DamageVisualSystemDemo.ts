// DamageVisualSystemDemo.ts
// Standalone demo for testing DamageVisualSystem with mock data

import { DamageVisualSystem, DamageState } from './DamageVisualSystem';
import { OverlayManager } from './OverlayManager';
import { SpriteRegistry } from './SpriteRegistry';
import { BuildingModuleSystem } from '../systems/building_modules/BuildingModuleSystem';
import { BuildingModule, ModuleState } from '../systems/building_modules/BuildingModule';
import { BuildingStructure } from '../core/interfaces/types/building';

// --- Setup canvas ---
const canvas = document.createElement('canvas');
canvas.width = 600;
canvas.height = 400;
document.body.appendChild(canvas);
const ctx = canvas.getContext('2d')!;

// --- Mock overlay and sprite managers ---
const overlayManager = new OverlayManager();
const spriteRegistry = SpriteRegistry.getInstance();

// --- Mock module system and modules ---
const moduleSystem = BuildingModuleSystem.getInstance();

function createMockModule(moduleId: string, type: string, x: number, y: number, state: ModuleState): BuildingModule {
    // @ts-ignore: Use a generic BuildingModule for demo purposes only
    const mod = new BuildingModule(moduleId, type, { x, y }, 100, 'wood', 0.01, 0.01);
    mod.currentState = state;
    return mod;
}

// Register mock modules
const states: ModuleState[] = [
    ModuleState.INTACT,
    ModuleState.DAMAGED,
    ModuleState.SEVERELY_DAMAGED,
    ModuleState.DESTROYED
];
states.forEach((state, i) => {
    const mod = createMockModule(`b1_${state.toLowerCase()}`, 'wall', 100 + i * 120, 200, state);
    moduleSystem['modules'].set(mod.moduleId, mod);
});

// --- Mock building structure ---
const structure: BuildingStructure = {
    id: 'b1',
    elements: new Map(),
    integrity: 1,
    supportPoints: [],
    battleDamage: 0,
    deterioration: 0,
};

// --- Instantiate visual system ---
const visualSystem = new DamageVisualSystem({
    overlayManager,
    spriteRegistry,
    damageStateMap: {
        intact: [],
        dirty: ['dirty'],
        dingy: ['dingy'],
        chipped: ['chipped'],
        cracked: ['cracked'],
        destroyed: ['cracked'],
    },
    fadeDuration: 300,
});

// --- Render loop ---
function render() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    visualSystem.renderBuildingModules(ctx, structure, moduleSystem, { debug: true });
}

render();

// --- UI for toggling states (optional) ---
// In a real demo, add buttons or keyboard controls to change module states and re-render 