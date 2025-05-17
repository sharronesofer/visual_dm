import { TurnOrderDisplay, TurnOrderEntry } from './TurnOrderDisplay';
import { ActionMenuSystem, CombatAction } from './ActionMenuSystem';
import { TargetingSystem, TargetEntity } from './TargetingSystem';
import { StatusEffectRenderer, StatusEffect } from './StatusEffectRenderer';
import { CombatLogDisplay, CombatLogEntry } from './CombatLogDisplay';
import { CombatInventoryUI } from './CombatInventoryUI';
import { QuickSlotManager } from './QuickSlotManager';

export class CombatUIManager {
  private container: HTMLElement;
  private turnOrderDisplay!: TurnOrderDisplay;
  private actionMenuSystem!: ActionMenuSystem;
  private targetingSystem!: TargetingSystem;
  private statusEffectRenderer!: StatusEffectRenderer;
  private combatLogDisplay!: CombatLogDisplay;
  private combatInventoryUI!: CombatInventoryUI;
  private quickSlotManager!: QuickSlotManager;

  constructor(containerId: string) {
    const element = document.getElementById(containerId);
    if (!element) {
      throw new Error(`Container element with id '${containerId}' not found`);
    }
    this.container = element;
    this.initializeController();
  }

  private initializeController(): void {
    this.container.innerHTML = '';
    this.container.className = 'combat-ui';

    // Create component containers
    const turnOrderContainer = document.createElement('div');
    turnOrderContainer.id = 'combat-turn-order';
    turnOrderContainer.className = 'combat-turn-order-container';

    const actionMenuContainer = document.createElement('div');
    actionMenuContainer.id = 'combat-action-menu';
    actionMenuContainer.className = 'combat-action-menu-container';

    const targetingContainer = document.createElement('div');
    targetingContainer.id = 'combat-targeting';
    targetingContainer.className = 'combat-targeting-container';

    const statusEffectContainer = document.createElement('div');
    statusEffectContainer.id = 'combat-status-effects';
    statusEffectContainer.className = 'combat-status-effects-container';

    const combatLogContainer = document.createElement('div');
    combatLogContainer.id = 'combat-log';
    combatLogContainer.className = 'combat-log-container';

    const inventoryContainer = document.createElement('div');
    inventoryContainer.id = 'combat-inventory';
    inventoryContainer.className = 'combat-inventory-container';

    const quickSlotContainer = document.createElement('div');
    quickSlotContainer.id = 'combat-quick-slots';
    quickSlotContainer.className = 'combat-quick-slots-container';

    // Initialize subcomponents (stubs for now)
    this.turnOrderDisplay = new TurnOrderDisplay('combat-turn-order');
    this.actionMenuSystem = new ActionMenuSystem('combat-action-menu');
    this.targetingSystem = new TargetingSystem('combat-targeting');
    this.statusEffectRenderer = new StatusEffectRenderer('combat-status-effects');
    this.combatLogDisplay = new CombatLogDisplay('combat-log');
    this.combatInventoryUI = new CombatInventoryUI('combat-inventory');
    this.quickSlotManager = new QuickSlotManager('combat-quick-slots');

    // Add components to container
    this.container.appendChild(turnOrderContainer);
    this.container.appendChild(actionMenuContainer);
    this.container.appendChild(targetingContainer);
    this.container.appendChild(statusEffectContainer);
    this.container.appendChild(combatLogContainer);
    this.container.appendChild(inventoryContainer);
    this.container.appendChild(quickSlotContainer);

    // TODO: Add CSS styles for layout and appearance
  }

  // Update the turn order display
  public updateTurnOrder(turnOrder: TurnOrderEntry[]): void {
    this.turnOrderDisplay.updateTurnOrder(turnOrder);
  }

  // Update the action menu
  public updateActions(actions: CombatAction[], onActionSelect?: (actionId: string) => void): void {
    this.actionMenuSystem.updateActions(actions, onActionSelect);
  }

  // Update the targeting system
  public updateTargets(targets: TargetEntity[], onTargetSelect?: (targetId: string) => void): void {
    this.targetingSystem.updateTargets(targets, onTargetSelect);
  }

  // Update the status effects
  public updateStatusEffects(effects: StatusEffect[]): void {
    this.statusEffectRenderer.updateStatusEffects(effects);
  }

  // Update the combat log
  public updateCombatLog(entries: CombatLogEntry[]): void {
    this.combatLogDisplay.updateLog(entries);
  }

  // TODO: Wire up to combat state and add similar update methods for other subcomponents
} 