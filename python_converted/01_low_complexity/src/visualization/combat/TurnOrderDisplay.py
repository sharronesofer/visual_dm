from typing import Any, List



class TurnOrderEntry:
    id: str
    name: str
    isActive: bool
class TurnOrderDisplay {
  private container: HTMLElement
  private turnOrder: List[TurnOrderEntry] = []
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
    this.container.className = 'turn-order-display'
    this.render()
  }
  public updateTurnOrder(turnOrder: List[TurnOrderEntry]): void {
    this.turnOrder = turnOrder
    this.render()
  }
  private render(): void {
    this.container.innerHTML = ''
    const list = document.createElement('div')
    list.className = 'turn-order-list'
    this.turnOrder.forEach(entry => {
      const item = document.createElement('div')
      item.className = 'turn-order-item' + (entry.isActive ? ' active' : '')
      item.textContent = entry.name
      list.appendChild(item)
    })
    this.container.appendChild(list)
  }
} 