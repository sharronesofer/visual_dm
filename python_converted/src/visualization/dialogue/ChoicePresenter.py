from typing import Any, List


ChoiceSelectCallback = (choiceId: str) => None
class ChoicePresenter {
  private container: HTMLElement
  constructor(containerId: str) {
    const element = document.getElementById(containerId)
    if (!element) {
      throw new Error(`Container element with id '${containerId}' not found`)
    }
    this.container = element
  }
  public render(choices: List[DialogueChoice], onSelect: ChoiceSelectCallback): void {
    this.container.innerHTML = ''
    choices.forEach(choice => {
      const btn = document.createElement('button')
      btn.className = 'dialogue-choice-btn'
      btn.textContent = choice.text
      btn.disabled = choice.isAvailable === false
      btn.onclick = () => onSelect(choice.id)
      this.container.appendChild(btn)
    })
  }
} 