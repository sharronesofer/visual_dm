import { Emotion } from './types';

export class EmotionSystem {
  private container: HTMLElement;

  constructor(containerId: string) {
    const element = document.getElementById(containerId);
    if (!element) {
      throw new Error(`Container element with id '${containerId}' not found`);
    }
    this.container = element;
  }

  public render(emotion: Emotion): void {
    this.container.innerHTML = '';
    // TODO: Map emotion to icon or emoji
    const label = document.createElement('span');
    label.className = 'dialogue-emotion';
    label.textContent = emotion;
    this.container.appendChild(label);
    // TODO: Add styling for .dialogue-emotion
  }
} 