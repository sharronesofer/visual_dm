export interface TurnOrderEntry {
  id: string;
  name: string;
  isActive: boolean;
}

export class TurnOrderDisplay {
  private container: HTMLElement;
  private turnOrder: TurnOrderEntry[] = [];

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
    this.container.className = 'turn-order-display';
    // Initial render
    this.render();
  }

  public updateTurnOrder(turnOrder: TurnOrderEntry[]): void {
    this.turnOrder = turnOrder;
    this.render();
  }

  private render(): void {
    this.container.innerHTML = '';
    const list = document.createElement('div');
    list.className = 'turn-order-list';
    this.turnOrder.forEach(entry => {
      const item = document.createElement('div');
      item.className = 'turn-order-item' + (entry.isActive ? ' active' : '');
      item.textContent = entry.name;
      list.appendChild(item);
    });
    this.container.appendChild(list);
    // TODO: Add styles for .turn-order-list and .turn-order-item
  }
} 