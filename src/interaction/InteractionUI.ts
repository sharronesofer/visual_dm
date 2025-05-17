import { InteractionManager } from './InteractionManager';
import { Actor } from './InteractionManager';
import { InteractionLogger } from './InteractionLogger';

export type InteractionUIOptions = {
    onSuccess?: (prompt: string) => void;
    onFail?: (prompt: string) => void;
    onUnavailable?: (prompt: string) => void;
    highlightColor?: string;
    icon?: string;
};

export class InteractionUI {
    private manager: InteractionManager;
    private options: InteractionUIOptions;

    constructor(manager: InteractionManager, options: InteractionUIOptions = {}) {
        this.manager = manager;
        this.options = options;
    }

    /**
     * Render interaction prompts for the given actor.
     * Returns an array of prompt objects for UI rendering.
     */
    getPrompts(actor: Actor): { prompt: string; interactableId: string }[] {
        try {
            const interactables = this.manager.getInteractablesInRange(actor);
            const prompts = interactables
                .filter(i => i.canInteract(actor.id))
                .map(i => ({ prompt: i.getInteractionPrompt(), interactableId: i.getId ? i.getId() : '' }));
            InteractionLogger.debug(`Rendering prompts for actor ${actor.id}: ${JSON.stringify(prompts)}`);
            return prompts;
        } catch (err) {
            InteractionLogger.error('Error rendering interaction prompts:', err);
            return [];
        }
    }

    /**
     * Visual indicator logic (e.g., highlight interactables in range)
     */
    getHighlightData(actor: Actor): { interactableId: string; color: string; icon?: string }[] {
        try {
            const color = this.options.highlightColor || '#FFD700';
            const icon = this.options.icon;
            const highlights = this.manager.getInteractablesInRange(actor).map(i => ({
                interactableId: i.getId ? i.getId() : '',
                color,
                icon,
            }));
            InteractionLogger.debug(`Highlight data for actor ${actor.id}: ${JSON.stringify(highlights)}`);
            return highlights;
        } catch (err) {
            InteractionLogger.error('Error getting highlight data:', err);
            return [];
        }
    }

    /**
     * Call this when an interaction is successful
     */
    handleSuccess(prompt: string) {
        try {
            if (this.options.onSuccess) this.options.onSuccess(prompt);
            InteractionLogger.info(`Interaction success: ${prompt}`);
            // Optionally trigger sound/animation here
        } catch (err) {
            InteractionLogger.error('Error handling interaction success:', err);
        }
    }

    /**
     * Call this when an interaction fails
     */
    handleFail(prompt: string) {
        try {
            if (this.options.onFail) this.options.onFail(prompt);
            InteractionLogger.warn(`Interaction failed: ${prompt}`);
            // Optionally trigger sound/animation here
        } catch (err) {
            InteractionLogger.error('Error handling interaction fail:', err);
        }
    }

    /**
     * Call this when an interaction is unavailable
     */
    handleUnavailable(prompt: string) {
        try {
            if (this.options.onUnavailable) this.options.onUnavailable(prompt);
            InteractionLogger.warn(`Interaction unavailable: ${prompt}`);
            // Optionally trigger sound/animation here
        } catch (err) {
            InteractionLogger.error('Error handling interaction unavailable:', err);
        }
    }
} 