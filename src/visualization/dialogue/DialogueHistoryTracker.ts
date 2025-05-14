import { DialogueEvent } from './types';

export class DialogueHistoryTracker {
  private container: HTMLElement;

  constructor(containerId: string) {
    const element = document.getElementById(containerId);
    if (!element) {
      throw new Error(`Container element with id '${containerId}' not found`);
    }
    this.container = element;
  }

  public render(history: DialogueEvent[]): void {
    this.container.innerHTML = '';
    const log = document.createElement('div');
    log.className = 'dialogue-history-log';
    history.forEach(event => {
      const entry = document.createElement('div');
      entry.className = 'dialogue-history-entry';
      entry.textContent = `${event.speaker.name}: ${event.text}`;
      log.appendChild(entry);
    });
    this.container.appendChild(log);
    // TODO: Add virtualization for long histories and styling for .dialogue-history-log, .dialogue-history-entry
  }
} 