import { DialogueEvent } from './types';

export class InterruptionHandler {
  private container: HTMLElement;

  constructor(containerId: string) {
    const element = document.getElementById(containerId);
    if (!element) {
      throw new Error(`Container element with id '${containerId}' not found`);
    }
    this.container = element;
  }

  public handleInterruption(event: DialogueEvent): void {
    this.container.innerHTML = '';
    const overlay = document.createElement('div');
    overlay.className = 'dialogue-interruption-overlay';
    overlay.textContent = `Interruption: ${event.text}`;
    this.container.appendChild(overlay);
    // TODO: Add priority management and styling for .dialogue-interruption-overlay
  }
} 