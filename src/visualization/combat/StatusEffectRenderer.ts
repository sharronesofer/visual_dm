export interface StatusEffect {
  id: string;
  label: string;
  icon?: string;
  isActive: boolean;
}

export class StatusEffectRenderer {
  private container: HTMLElement;
  private statusEffects: StatusEffect[] = [];

  constructor(containerId: string) {
    const element = document.getElementById(containerId);
    if (!element) {
      throw new Error(`Container element with id '${containerId}' not found`);
    }
    this.container = element;
    this.initializeDisplay();
  }

  private initializeDisplay(): void {
    this.container.innerHTML = '';
    this.container.className = 'status-effect-renderer';
    this.render();
  }

  public updateStatusEffects(effects: StatusEffect[]): void {
    this.statusEffects = effects;
    this.render();
  }

  private render(): void {
    this.container.innerHTML = '';
    const list = document.createElement('div');
    list.className = 'status-effect-list';
    this.statusEffects.forEach(effect => {
      const item = document.createElement('div');
      item.className = 'status-effect-item' + (effect.isActive ? ' active' : '');
      if (effect.icon) {
        const icon = document.createElement('img');
        icon.src = effect.icon;
        icon.alt = effect.label;
        icon.className = 'status-effect-icon';
        item.appendChild(icon);
      } else {
        item.textContent = effect.label;
      }
      list.appendChild(item);
    });
    this.container.appendChild(list);
    // TODO: Add styles for .status-effect-list, .status-effect-item, .active, .status-effect-icon
  }
} 