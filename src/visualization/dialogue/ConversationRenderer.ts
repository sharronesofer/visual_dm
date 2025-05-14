import { DialogueEvent } from './types';

export class ConversationRenderer {
  private container: HTMLElement;

  constructor(containerId: string) {
    const element = document.getElementById(containerId);
    if (!element) {
      throw new Error(`Container element with id '${containerId}' not found`);
    }
    this.container = element;
  }

  public render(event: DialogueEvent): void {
    this.container.innerHTML = '';
    // Speaker portrait
    if (event.speaker.portraitUrl) {
      const img = document.createElement('img');
      img.src = event.speaker.portraitUrl;
      img.alt = event.speaker.name;
      img.className = 'dialogue-portrait';
      this.container.appendChild(img);
    }
    // Speaker name
    const name = document.createElement('div');
    name.className = 'dialogue-speaker';
    name.textContent = event.speaker.name;
    this.container.appendChild(name);
    // Dialogue text
    const text = document.createElement('div');
    text.className = 'dialogue-text';
    text.textContent = event.text; // TODO: Add typing animation
    this.container.appendChild(text);
    // TODO: Display emotion indicator
  }
} 