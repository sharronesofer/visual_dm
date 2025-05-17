import { Interactable } from './Interactable';
import { InteractionLogger } from './InteractionLogger';

interface Position {
    x: number;
    y: number;
    z: number;
}

export interface Actor {
    id: string;
    position: Position;
}

export class InteractionManager {
    private interactables: Map<string, Interactable> = new Map();

    /**
     * Registers an interactable object with the manager.
     */
    registerInteractable(interactable: Interactable): void {
        try {
            const id = interactable.getId ? interactable.getId() : undefined;
            if (!id) {
                InteractionLogger.warn('Attempted to register interactable without ID.');
                return;
            }
            if (this.interactables.has(id)) {
                InteractionLogger.warn(`Interactable with ID ${id} is already registered.`);
                return;
            }
            this.interactables.set(id, interactable);
            InteractionLogger.info(`Registered interactable: ${id}`);
        } catch (err) {
            InteractionLogger.error('Error registering interactable:', err);
        }
    }

    /**
     * Deregisters an interactable object from the manager.
     */
    deregisterInteractable(interactable: Interactable): void {
        try {
            const id = interactable.getId ? interactable.getId() : undefined;
            if (!id || !this.interactables.has(id)) {
                InteractionLogger.warn('Attempted to deregister unknown interactable.');
                return;
            }
            this.interactables.delete(id);
            InteractionLogger.info(`Deregistered interactable: ${id}`);
        } catch (err) {
            InteractionLogger.error('Error deregistering interactable:', err);
        }
    }

    /**
     * Returns a list of interactables within range of the actor.
     * Placeholder: Replace with actual raycasting/collision logic.
     */
    getInteractablesInRange(actor: Actor, range: number = 2): Interactable[] {
        try {
            // Placeholder: In a real system, use spatial queries/raycasting
            // For now, return all interactables
            InteractionLogger.debug(`Querying interactables in range for actor ${actor.id}`);
            return Array.from(this.interactables.values());
        } catch (err) {
            InteractionLogger.error('Error getting interactables in range:', err);
            return [];
        }
    }

    /**
     * Handles player input for interaction (stub for integration with input system).
     */
    handleInteractionInput(actor: Actor): void {
        try {
            // Placeholder for input handling logic
            InteractionLogger.debug(`Handling interaction input for actor ${actor.id}`);
        } catch (err) {
            InteractionLogger.error('Error handling interaction input:', err);
        }
    }

    /**
     * Returns prompts for all available interactions for the actor.
     */
    getAvailableInteractionPrompts(actor: Actor): string[] {
        try {
            return this.getInteractablesInRange(actor)
                .filter(i => i.canInteract(actor.id))
                .map(i => i.getInteractionPrompt());
        } catch (err) {
            InteractionLogger.error('Error getting available interaction prompts:', err);
            return [];
        }
    }

    /**
     * Should be called each frame or on relevant events to update detection logic.
     * (Stub for integration with game loop)
     */
    update(actor: Actor): void {
        try {
            // Placeholder for update logic
            InteractionLogger.debug(`Updating interaction state for actor ${actor.id}`);
        } catch (err) {
            InteractionLogger.error('Error updating interaction state:', err);
        }
    }
} 