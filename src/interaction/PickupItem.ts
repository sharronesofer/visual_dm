import { Interactable } from './Interactable';
import { InteractionLogger } from './InteractionLogger';
import { ItemService } from '../core/services/ItemService';
import { Item } from '../core/models/Item';

export class PickupItem implements Interactable {
    private id: string;
    private item: Item;
    private pickedUp: boolean = false;
    private itemService: ItemService;

    constructor(id: string, item: Item, itemService: ItemService) {
        this.id = id;
        this.item = item;
        this.itemService = itemService;
    }

    canInteract(actorId: string): boolean {
        return !this.pickedUp;
    }

    async onInteract(actorId: string): Promise<void> {
        try {
            if (this.pickedUp) return;

            // Actually add to inventory using ItemService
            const slotId = this.itemService.addItemToInventory(this.item);

            if (slotId) {
                this.pickedUp = true;
                InteractionLogger.info(`Actor ${actorId} picked up item: ${this.item.name} (${this.id})`);

                // Track pickup in item history
                this.item.addHistoryEvent({
                    eventType: 'PICKUP',
                    description: `Item picked up by ${actorId}`,
                    actorId
                });

                // Could trigger feedback/animation here
            } else {
                InteractionLogger.warn(`Actor ${actorId} could not pick up item: ${this.item.name} (inventory full)`);
            }
        } catch (err) {
            InteractionLogger.error(`Error during pickup interaction for item ${this.id}:`, err);
        }
    }

    getInteractionPrompt(): string {
        return this.pickedUp ? '' : `Pick up ${this.item.name}`;
    }

    getId(): string {
        return this.id;
    }

    getItem(): Item {
        return this.item;
    }

    isPickedUp(): boolean {
        return this.pickedUp;
    }
} 