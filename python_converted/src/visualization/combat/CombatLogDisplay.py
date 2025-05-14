from typing import Any, List


class CombatLogEntry:
    id: str
    message: str
    timestamp?: str
class CombatLogDisplay {
  private container: HTMLElement
  private logEntries: List[CombatLogEntry] = []
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
    this.container.className = 'combat-log-display'
    this.render()
  }
  public updateLog(entries: List[CombatLogEntry]): void {
    this.logEntries = entries
    this.render()
  }
  private render(): void {
    this.container.innerHTML = ''
    const list = document.createElement('div')
    list.className = 'combat-log-list'
    this.logEntries.forEach(entry => {
      const item = document.createElement('div')
      item.className = 'combat-log-entry'
      item.textContent = entry.timestamp ? `[${entry.timestamp}] ${entry.message}` : entry.message
      list.appendChild(item)
    })
    this.container.appendChild(list)
  }
} 