import { GPTService } from './GPTService';
import { LLMErrorHandler, LLMErrorType, LLMErrorContext } from './LLMErrorHandler';
import { ApiResponse } from '../interfaces/types/api';

export interface GPTServiceOptions {
  maxRetries?: number;
  timeoutMs?: number;
}

export class GPTServiceWrapper {
  private static instance: GPTServiceWrapper;
  private gptService: GPTService;
  private errorHandler: LLMErrorHandler;
  private defaultOptions: GPTServiceOptions = {
    maxRetries: 3,
    timeoutMs: 10000
  };

  private constructor() {
    this.gptService = GPTService.getInstance();
    this.errorHandler = LLMErrorHandler.getInstance();
  }

  public static getInstance(): GPTServiceWrapper {
    if (!GPTServiceWrapper.instance) {
      GPTServiceWrapper.instance = new GPTServiceWrapper();
    }
    return GPTServiceWrapper.instance;
  }

  /**
   * Generate names with error handling and retries
   */
  public async generateNames(params: {
    race?: string;
    class?: string;
    alignment?: string;
    count?: number;
  }, options?: GPTServiceOptions): Promise<any> {
    const mergedOptions = { ...this.defaultOptions, ...options };
    let retryCount = 0;
    let lastError: Error | null = null;

    // Construct the error context
    const errorContext: LLMErrorContext = {
      timestamp: Date.now(),
      prompt: `Generate ${params.count || 5} fantasy character names for ${params.race} ${params.class} with ${params.alignment} alignment`,
      gameState: { interactionType: 'character_creation' }
    };

    while (retryCount <= mergedOptions.maxRetries!) {
      try {
        // Add timeout handling
        const timeoutPromise = new Promise<never>((_, reject) => {
          setTimeout(() => reject(new Error('GPT request timed out')), mergedOptions.timeoutMs);
        });

        // Actual request
        const result = await Promise.race([
          this.gptService.generateNames(params),
          timeoutPromise
        ]);

        return result;
      } catch (error) {
        lastError = error as Error;
        
        // Identify error type and log it
        const errorType = this.errorHandler.identifyErrorType(lastError);
        this.errorHandler.logError(errorType, errorContext);
        
        // Get retry delay with exponential backoff
        const delayMs = this.errorHandler.getRetryDelay(retryCount);
        
        // If we haven't exceeded max retries, wait and try again
        if (retryCount < mergedOptions.maxRetries!) {
          await new Promise(resolve => setTimeout(resolve, delayMs));
          retryCount++;
          
          // For certain error types, modify params to improve chances of success
          if (errorType === LLMErrorType.CONTENT_POLICY) {
            // Make generation more neutral for content policy violations
            params.alignment = 'neutral';
          }
        } else {
          // We've exhausted retries, use fallback
          return this.handleNameGenerationFallback(params, errorContext, errorType);
        }
      }
    }

    throw lastError; // Should never reach here due to the fallback, but added for type safety
  }

  /**
   * Generate background with error handling and retries
   */
  public async generateBackground(params: {
    name: string;
    race: string;
    class: string;
    alignment: string;
  }, options?: GPTServiceOptions): Promise<string> {
    const mergedOptions = { ...this.defaultOptions, ...options };
    let retryCount = 0;
    let lastError: Error | null = null;

    // Construct the prompt and error context
    const prompt = `Create a background story for a ${params.alignment} ${params.race} ${params.class} named ${params.name}`;
    const errorContext: LLMErrorContext = {
      timestamp: Date.now(),
      prompt,
      gameState: { interactionType: 'character_creation' }
    };

    while (retryCount <= mergedOptions.maxRetries!) {
      try {
        // Add timeout handling
        const timeoutPromise = new Promise<never>((_, reject) => {
          setTimeout(() => reject(new Error('GPT request timed out')), mergedOptions.timeoutMs);
        });

        // Actual request
        const result = await Promise.race([
          this.gptService.generateBackground(params),
          timeoutPromise
        ]);

        return result;
      } catch (error) {
        lastError = error as Error;
        
        // Identify error type and log it
        const errorType = this.errorHandler.identifyErrorType(lastError);
        this.errorHandler.logError(errorType, errorContext);
        
        // Get retry delay with exponential backoff
        const delayMs = this.errorHandler.getRetryDelay(retryCount);
        
        // If we haven't exceeded max retries, wait and try again
        if (retryCount < mergedOptions.maxRetries!) {
          await new Promise(resolve => setTimeout(resolve, delayMs));
          retryCount++;
          
          // For certain error types, modify params to improve chances of success
          if (errorType === LLMErrorType.CONTENT_POLICY) {
            // Make background more neutral for content policy violations
            params.alignment = 'neutral';
          }
        } else {
          // We've exhausted retries, use fallback
          return this.handleBackgroundGenerationFallback(params, errorContext, errorType);
        }
      }
    }

    throw lastError; // Should never reach here due to the fallback, but added for type safety
  }

  /**
   * Direct access to GPT API with error handling and retries
   * This can be used for any custom prompts, including dialogue
   */
  public async generateText(prompt: string, 
                          options: { 
                            maxTokens?: number; 
                            temperature?: number;
                            contextType?: string;
                            characterId?: string;
                            gameState?: any;
                          } & GPTServiceOptions = {}): Promise<string> {
    const { maxTokens = 100, temperature = 0.7, contextType = 'default', characterId, gameState, ...retryOptions } = options;
    const mergedOptions = { ...this.defaultOptions, ...retryOptions };
    
    let retryCount = 0;
    let lastError: Error | null = null;
    let currentPrompt = prompt;

    // Construct error context
    const errorContext: LLMErrorContext = {
      timestamp: Date.now(),
      prompt,
      characterId,
      gameState: { 
        ...gameState,
        interactionType: contextType 
      }
    };

    while (retryCount <= mergedOptions.maxRetries!) {
      try {
        // Add timeout handling
        const timeoutPromise = new Promise<never>((_, reject) => {
          setTimeout(() => reject(new Error('GPT request timed out')), mergedOptions.timeoutMs);
        });

        // Actual request - use the ApiService directly since there's no GPTService method
        const response = await Promise.race([
          this.makeGptRequest(currentPrompt, maxTokens, temperature),
          timeoutPromise
        ]);

        if (response.error) {
          throw new Error(response.error.message);
        }

        return response.data.choices[0].text.trim();
      } catch (error) {
        lastError = error as Error;
        
        // Identify error type and log it
        const errorType = this.errorHandler.identifyErrorType(lastError);
        this.errorHandler.logError(errorType, errorContext);
        
        // Get retry delay with exponential backoff
        const delayMs = this.errorHandler.getRetryDelay(retryCount);
        
        // If we haven't exceeded max retries, wait and try again
        if (retryCount < mergedOptions.maxRetries!) {
          await new Promise(resolve => setTimeout(resolve, delayMs));
          
          // Get alternative prompt for next retry
          currentPrompt = this.errorHandler.getAlternativePrompt(prompt, errorType, retryCount + 1);
          
          retryCount++;
        } else {
          // We've exhausted retries, use fallback
          return this.errorHandler.getFallbackResponse(errorType, errorContext);
        }
      }
    }

    throw lastError; // Should never reach here due to the fallback, but added for type safety
  }

  /**
   * Private method to make GPT API requests
   */
  private async makeGptRequest(prompt: string, maxTokens: number, temperature: number): Promise<ApiResponse> {
    return this.gptService['apiService'].post('/api/gpt/generate', {
      prompt,
      max_tokens: maxTokens,
      temperature
    });
  }

  /**
   * Handle fallback for name generation
   */
  private handleNameGenerationFallback(
    params: { race?: string; class?: string; alignment?: string; count?: number },
    errorContext: LLMErrorContext,
    errorType: LLMErrorType
  ): { name: string; description: string }[] {
    const count = params.count || 5;
    const fallbackNames = [
      { name: "Alaric", description: "A steadfast warrior from the northern mountains" },
      { name: "Elindra", description: "A mystical enchantress with ancient bloodlines" },
      { name: "Thorne", description: "A skilled hunter known for silent precision" },
      { name: "Seraphina", description: "A blessed healer with divine connections" },
      { name: "Darian", description: "A cunning rogue with a mysterious past" },
      { name: "Lyra", description: "A bard whose songs can inspire armies" },
      { name: "Gareth", description: "A noble knight sworn to protect the innocent" },
      { name: "Isolde", description: "A nature-bound druid with animal companions" },
      { name: "Vaelon", description: "A scholarly mage dedicated to ancient knowledge" },
      { name: "Kitra", description: "A fierce ranger with unparalleled tracking skills" }
    ];
    
    // Select a subset of fallback names based on requested count
    const selectedNames = [];
    for (let i = 0; i < Math.min(count, fallbackNames.length); i++) {
      selectedNames.push(fallbackNames[i]);
    }
    
    return selectedNames;
  }

  /**
   * Handle fallback for background generation
   */
  private handleBackgroundGenerationFallback(
    params: { name: string; race: string; class: string; alignment: string },
    errorContext: LLMErrorContext,
    errorType: LLMErrorType
  ): string {
    // Create a generic background based on the character parameters
    return `${params.name} is a ${params.alignment} ${params.race} ${params.class} who has led an adventurous life. 
    Born in a small settlement, ${params.name} trained diligently to master the skills of a ${params.class}. 
    After facing numerous challenges and overcoming significant obstacles, ${params.name} decided to seek 
    greater adventures and make a name in the world. With a strong sense of ${this.getValueForAlignment(params.alignment)}, 
    ${params.name} continues to pursue worthy goals while developing greater mastery of ${params.class} abilities.`;
  }

  /**
   * Helper to get alignment-appropriate values
   */
  private getValueForAlignment(alignment: string): string {
    alignment = alignment.toLowerCase();
    if (alignment.includes('good')) return 'justice and compassion';
    if (alignment.includes('evil')) return 'power and ambition';
    if (alignment.includes('lawful')) return 'order and tradition';
    if (alignment.includes('chaotic')) return 'freedom and individuality';
    return 'balance and pragmatism'; // neutral default
  }
} 