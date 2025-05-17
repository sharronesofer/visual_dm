import { Interactable } from './Interactable';
import { InteractionLogger } from './InteractionLogger';

export class NPC implements Interactable {
    private id: string;
    private name: string;
    private dialogue: string;
    private interacted: boolean = false;
    private onDialogue: (actorId: string) => void | Promise<void>;

    constructor(id: string, name: string, dialogue: string, onDialogue: (actorId: string) => void | Promise<void>) {
        this.id = id;
        this.name = name;
        this.dialogue = dialogue;
        this.onDialogue = onDialogue;
    }

    canInteract(actorId: string): boolean {
        return !this.interacted;
    }

    async onInteract(actorId: string): Promise<void> {
        try {
            if (this.interacted) return;
            await this.onDialogue(actorId);
            this.interacted = true;
            InteractionLogger.info(`Actor ${actorId} interacted with NPC: ${this.name} (${this.id})`);
            // Optionally trigger feedback/animation here
        } catch (err) {
            InteractionLogger.error(`Error during NPC interaction for ${this.id}:`, err);
        }
    }

    getInteractionPrompt(): string {
        return this.interacted ? '' : `Talk to ${this.name}`;
    }

    getId(): string {
        return this.id;
    }
} 