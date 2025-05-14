import { DialogueChoice } from './types';

type ChoiceSelectCallback = (choiceId: string) => void;

export class ChoicePresenter {
  private container: HTMLElement;

  constructor(containerId: string) {
    const element = document.getElementById(containerId);
    if (!element) {
      throw new Error(`Container element with id '${containerId}' not found`);
    }
    this.container = element;
  }

  public render(choices: DialogueChoice[], onSelect: ChoiceSelectCallback): void {
    this.container.innerHTML = '';
    choices.forEach(choice => {
      const btn = document.createElement('button');
      btn.className = 'dialogue-choice-btn';
      btn.textContent = choice.text;
      btn.disabled = choice.isAvailable === false;
      btn.onclick = () => onSelect(choice.id);
      this.container.appendChild(btn);
    });
    // TODO: Add styling for .dialogue-choice-btn and handle disabled state
  }
} 