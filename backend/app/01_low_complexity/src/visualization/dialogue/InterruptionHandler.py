from typing import Any



class InterruptionHandler {
  private container: HTMLElement
  constructor(containerId: str) {
    const element = document.getElementById(containerId)
    if (!element) {
      throw new Error(`Container element with id '${containerId}' not found`)
    }
    this.container = element
  }
  public handleInterruption(event: DialogueEvent): void {
    this.container.innerHTML = ''
    const overlay = document.createElement('div')
    overlay.className = 'dialogue-interruption-overlay'
    overlay.textContent = `Interruption: ${event.text}`
    this.container.appendChild(overlay)
  }
} 