from typing import Any, List



class CombatUIManager {
  private container: HTMLElement
  private turnOrderDisplay!: TurnOrderDisplay
  private actionMenuSystem!: ActionMenuSystem
  private targetingSystem!: TargetingSystem
  private statusEffectRenderer!: StatusEffectRenderer
  private combatLogDisplay!: CombatLogDisplay
  constructor(containerId: str) {
    const element = document.getElementById(containerId)
    if (!element) {
      throw new Error(`Container element with id '${containerId}' not found`)
    }
    this.container = element
    this.initializeController()
  }
  private initializeController(): void {
    this.container.innerHTML = ''
    this.container.className = 'combat-ui'
    const turnOrderContainer = document.createElement('div')
    turnOrderContainer.id = 'combat-turn-order'
    turnOrderContainer.className = 'combat-turn-order-container'
    const actionMenuContainer = document.createElement('div')
    actionMenuContainer.id = 'combat-action-menu'
    actionMenuContainer.className = 'combat-action-menu-container'
    const targetingContainer = document.createElement('div')
    targetingContainer.id = 'combat-targeting'
    targetingContainer.className = 'combat-targeting-container'
    const statusEffectContainer = document.createElement('div')
    statusEffectContainer.id = 'combat-status-effects'
    statusEffectContainer.className = 'combat-status-effects-container'
    const combatLogContainer = document.createElement('div')
    combatLogContainer.id = 'combat-log'
    combatLogContainer.className = 'combat-log-container'
    this.turnOrderDisplay = new TurnOrderDisplay('combat-turn-order')
    this.actionMenuSystem = new ActionMenuSystem('combat-action-menu')
    this.targetingSystem = new TargetingSystem('combat-targeting')
    this.statusEffectRenderer = new StatusEffectRenderer('combat-status-effects')
    this.combatLogDisplay = new CombatLogDisplay('combat-log')
    this.container.appendChild(turnOrderContainer)
    this.container.appendChild(actionMenuContainer)
    this.container.appendChild(targetingContainer)
    this.container.appendChild(statusEffectContainer)
    this.container.appendChild(combatLogContainer)
  }
  public updateTurnOrder(turnOrder: List[TurnOrderEntry]): void {
    this.turnOrderDisplay.updateTurnOrder(turnOrder)
  }
  public updateActions(actions: List[CombatAction], onActionSelect?: (actionId: str) => void): void {
    this.actionMenuSystem.updateActions(actions, onActionSelect)
  }
  public updateTargets(targets: List[TargetEntity], onTargetSelect?: (targetId: str) => void): void {
    this.targetingSystem.updateTargets(targets, onTargetSelect)
  }
  public updateStatusEffects(effects: List[StatusEffect]): void {
    this.statusEffectRenderer.updateStatusEffects(effects)
  }
  public updateCombatLog(entries: List[CombatLogEntry]): void {
    this.combatLogDisplay.updateLog(entries)
  }
} 