from typing import Any


class EmotionSystem {
  private container: HTMLElement
  constructor(containerId: str) {
    const element = document.getElementById(containerId)
    if (!element) {
      throw new Error(`Container element with id '${containerId}' not found`)
    }
    this.container = element
  }
  public render(emotion: Emotion): void {
    this.container.innerHTML = ''
    const label = document.createElement('span')
    label.className = 'dialogue-emotion'
    label.textContent = emotion
    this.container.appendChild(label)
  }
} 