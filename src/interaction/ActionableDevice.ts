import { Interactable } from './Interactable';
import { InteractionLogger } from './InteractionLogger';

export class ActionableDevice implements Interactable {
    private id: string;
    private deviceName: string;
    private activated: boolean = false;
    private action: () => void | Promise<void>;

    constructor(id: string, deviceName: string, action: () => void | Promise<void>) {
        this.id = id;
        this.deviceName = deviceName;
        this.action = action;
    }

    canInteract(actorId: string): boolean {
        return !this.activated;
    }

    async onInteract(actorId: string): Promise<void> {
        try {
            if (this.activated) return;
            await this.action();
            this.activated = true;
            InteractionLogger.info(`Actor ${actorId} activated device: ${this.deviceName} (${this.id})`);
            // Optionally trigger feedback/animation here
        } catch (err) {
            InteractionLogger.error(`Error during activation for device ${this.id}:`, err);
        }
    }

    getInteractionPrompt(): string {
        return this.activated ? '' : `Activate ${this.deviceName}`;
    }

    getId(): string {
        return this.id;
    }
} 