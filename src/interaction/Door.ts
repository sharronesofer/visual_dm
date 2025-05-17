import { Interactable } from './Interactable';
import { InteractionLogger } from './InteractionLogger';

export class Door implements Interactable {
    private id: string;
    private isOpen: boolean = false;
    private requiredKey?: string;
    private hasKey: (actorId: string, key: string) => boolean;

    constructor(id: string, requiredKey?: string, hasKey?: (actorId: string, key: string) => boolean) {
        this.id = id;
        this.requiredKey = requiredKey;
        this.hasKey = hasKey || (() => true); // Default: always has key if not provided
    }

    canInteract(actorId: string): boolean {
        if (this.isOpen) return false;
        if (this.requiredKey) {
            return this.hasKey(actorId, this.requiredKey);
        }
        return true;
    }

    async onInteract(actorId: string): Promise<void> {
        try {
            if (this.isOpen) return;
            if (this.requiredKey && !this.hasKey(actorId, this.requiredKey)) {
                InteractionLogger.warn(`Actor ${actorId} tried to open door ${this.id} without required key: ${this.requiredKey}`);
                return;
            }
            this.isOpen = true;
            InteractionLogger.info(`Actor ${actorId} opened door: ${this.id}`);
            // Optionally trigger open animation here
        } catch (err) {
            InteractionLogger.error(`Error during door interaction for ${this.id}:`, err);
        }
    }

    getInteractionPrompt(): string {
        if (this.isOpen) return '';
        if (this.requiredKey) {
            return `Open Door (requires ${this.requiredKey})`;
        }
        return 'Open Door';
    }

    getId(): string {
        return this.id;
    }
} 