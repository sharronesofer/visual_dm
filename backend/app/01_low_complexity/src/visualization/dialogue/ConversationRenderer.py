from typing import Any



class ConversationRenderer {
  private container: HTMLElement
  constructor(containerId: str) {
    const element = document.getElementById(containerId)
    if (!element) {
      throw new Error(`Container element with id '${containerId}' not found`)
    }
    this.container = element
  }
  public render(event: DialogueEvent): void {
    this.container.innerHTML = ''
    if (event.speaker.portraitUrl) {
      const img = document.createElement('img')
      img.src = event.speaker.portraitUrl
      img.alt = event.speaker.name
      img.className = 'dialogue-portrait'
      this.container.appendChild(img)
    }
    const name = document.createElement('div')
    name.className = 'dialogue-speaker'
    name.textContent = event.speaker.name
    this.container.appendChild(name)
    const text = document.createElement('div')
    text.className = 'dialogue-text'
    text.textContent = event.text 
    this.container.appendChild(text)
  }
} 