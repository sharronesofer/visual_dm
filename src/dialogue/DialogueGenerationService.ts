import { GPTClient, GPTConfig, GPTResponse } from './GPTClient';

/**
 * DialogueGenerationService provides a high-level interface for generating dialogue using GPTClient.
 * Handles prompt formatting, context, error propagation, and logging.
 */
export class DialogueGenerationService {
    private gptClient: GPTClient;
    private defaultConfig: GPTConfig;

    constructor(gptClient: GPTClient, defaultConfig: GPTConfig) {
        this.gptClient = gptClient;
        this.defaultConfig = defaultConfig;
    }

    /**
     * Generates dialogue text given a prompt and context.
     * @param prompt The main prompt string.
     * @param context Array of previous conversation strings.
     * @param config Optional GPTConfig overrides.
     */
    async generateDialogue(prompt: string, context: string[] = [], config?: Partial<GPTConfig>): Promise<GPTResponse> {
        const mergedConfig: GPTConfig = { ...this.defaultConfig, ...config };
        try {
            const response = await this.gptClient.generateCompletion(prompt, context, mergedConfig);
            if (response.error) {
                this.logError('GPT API Error', response.error, { prompt, context, config: mergedConfig });
            }
            return response;
        } catch (err: any) {
            this.logError('DialogueGenerationService Exception', err.message, { prompt, context, config: mergedConfig });
            return { text: '', error: err.message, raw: err };
        }
    }

    /**
     * Logs errors for debugging and monitoring.
     */
    private logError(message: string, error: string, meta: any) {
        // Replace with a more robust logging system as needed
        // eslint-disable-next-line no-console
        console.error(`[DialogueGenerationService] ${message}:`, error, meta);
    }
} 