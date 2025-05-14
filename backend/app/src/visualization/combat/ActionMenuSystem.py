from typing import Any, List


class CombatAction:
    id: str
    label: str
    disabled?: bool
ActionSelectCallback = (actionId: str) => None
class ActionMenuSystem {
  private container: HTMLElement
  private actions: List[CombatAction] = []
  private onActionSelect: ActionSelectCallback | null = null
  constructor(containerId: str) {
    const element = document.getElementById(containerId)
    if (!element) {
      throw new Error(`Container element with id '${containerId}' not found`)
    }
    this.container = element
    this.initializeDisplay()
  }
  private initializeDisplay(): void {
    this.container.innerHTML = ''
    this.container.className = 'action-menu-system'
    this.render()
  }
  public updateActions(actions: List[CombatAction], onActionSelect?: ActionSelectCallback): void {
    this.actions = actions
    if (onActionSelect) this.onActionSelect = onActionSelect
    this.render()
  }
  private render(): void {
    this.container.innerHTML = ''
    const buttonGroup = document.createElement('div')
    buttonGroup.className = 'action-menu-buttons'
    this.actions.forEach(action => {
      const btn = document.createElement('button')
      btn.className = 'combat-action-btn'
      btn.textContent = action.label
      btn.disabled = !!action.disabled
      btn.onclick = () => {
        if (!action.disabled && this.onActionSelect) {
          this.onActionSelect(action.id)
        }
      }
      buttonGroup.appendChild(btn)
    })
    this.container.appendChild(buttonGroup)
  }
} 