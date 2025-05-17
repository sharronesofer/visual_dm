/**
 * Interactable objects should implement robust error handling in their methods.
 * Use try/catch and InteractionLogger for logging errors and important events.
 */
export interface Interactable {
    /**
     * Determines if the object can currently be interacted with by the player.
     * @param actorId - The ID of the actor attempting interaction (e.g., player or NPC)
     * @returns boolean indicating if interaction is possible
     */
    canInteract(actorId: string): boolean;

    /**
     * Executes the interaction logic when triggered by the player.
     * @param actorId - The ID of the actor performing the interaction
     * @returns void or a Promise for async interactions
     */
    onInteract(actorId: string): void | Promise<void>;

    /**
     * Returns the prompt or description to display to the player for this interaction.
     * @returns string prompt for UI display
     */
    getInteractionPrompt(): string;

    /**
     * Optional: Returns a unique identifier for this interactable (for tracking/registration)
     */
    getId?(): string;
} 