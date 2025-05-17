import { Interactable } from './Interactable';
import { InteractionLogger } from './InteractionLogger';

export class Switch implements Interactable {
    private id: string;
    private label: string;
    private isOn: boolean = false;
    private onToggle: (actorId: string, isOn: boolean) => void | Promise<void>;

    constructor(id: string, label: string, onToggle: (actorId: string, isOn: boolean) => void | Promise<void>) {
        this.id = id;
        this.label = label;
        this.onToggle = onToggle;
    }

    canInteract(actorId: string): boolean {
        return true;
    }

    async onInteract(actorId: string): Promise<void> {
        try {
            this.isOn = !this.isOn;
            await this.onToggle(actorId, this.isOn);
            InteractionLogger.info(`Actor ${actorId} toggled switch: ${this.label} (${this.id}) to ${this.isOn ? 'ON' : 'OFF'}`);
            // Optionally trigger feedback/animation here
        } catch (err) {
            InteractionLogger.error(`Error during switch interaction for ${this.id}:`, err);
        }
    }

    getInteractionPrompt(): string {
        return this.isOn ? `Turn off ${this.label}` : `Turn on ${this.label}`;
    }

    getId(): string {
        return this.id;
    }
} 