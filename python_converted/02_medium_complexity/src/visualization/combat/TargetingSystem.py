from typing import Any, List



class TargetEntity:
    id: str
    name: str
    isSelected: bool
    isInRange: bool
TargetSelectCallback = (targetId: str) => None
class TargetingSystem {
  private container: HTMLElement
  private targets: List[TargetEntity] = []
  private onTargetSelect: TargetSelectCallback | null = null
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
    this.container.className = 'targeting-system'
    this.render()
  }
  public updateTargets(targets: List[TargetEntity], onTargetSelect?: TargetSelectCallback): void {
    this.targets = targets
    if (onTargetSelect) this.onTargetSelect = onTargetSelect
    this.render()
  }
  private render(): void {
    this.container.innerHTML = ''
    const list = document.createElement('div')
    list.className = 'target-list'
    this.targets.forEach(target => {
      const item = document.createElement('div')
      item.className = 'target-item' + (target.isSelected ? ' selected' : '') + (target.isInRange ? ' in-range' : ' out-of-range')
      item.textContent = target.name
      item.onclick = () => {
        if (target.isInRange && this.onTargetSelect) {
          this.onTargetSelect(target.id)
        }
      }
      list.appendChild(item)
    })
    this.container.appendChild(list)
  }
} 