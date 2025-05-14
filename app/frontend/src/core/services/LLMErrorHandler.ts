import { ApiError } from '../interfaces/types/api';
import { LoggerService } from './LoggerService';

export enum LLMErrorType {
  TIMEOUT = 'timeout',
  CONTENT_POLICY = 'content_policy',
  RATE_LIMIT = 'rate_limit',
  MALFORMED_RESPONSE = 'malformed_response',
  SERVER_ERROR = 'server_error',
  NETWORK_ERROR = 'network_error',
  UNKNOWN = 'unknown'
}

export interface LLMErrorContext {
  prompt?: string;
  model?: string;
  timestamp: number;
  conversationId?: string;
  characterId?: string;
  gameState?: any;
  errorDetails?: any;
}

export interface RetryStrategy {
  maxRetries: number;
  backoffFactor: number;
  initialDelayMs: number;
  jitter: boolean;
  alternativePrompts?: string[];
}

export interface LLMErrorConfig {
  logLevel: 'debug' | 'info' | 'warn' | 'error';
  retryStrategy: RetryStrategy;
  fallbackLibrary: Record<string, string[]>;
  monitoringEnabled: boolean;
}

export class LLMErrorHandler {
  private static instance: LLMErrorHandler;
  private logger: LoggerService;
  private config: LLMErrorConfig;
  private fallbacks: Record<string, string[]>;
  private errorCounts: Record<string, number> = {};
  
  private constructor() {
    this.logger = LoggerService.getInstance();
    this.config = this.getDefaultConfig();
    this.fallbacks = this.loadFallbackLibrary();
  }

  public static getInstance(): LLMErrorHandler {
    if (!LLMErrorHandler.instance) {
      LLMErrorHandler.instance = new LLMErrorHandler();
    }
    return LLMErrorHandler.instance;
  }

  /**
   * Identify the type of error from API error or exception
   */
  public identifyErrorType(error: Error | ApiError): LLMErrorType {
    const errorMessage = error.message?.toLowerCase() || '';
    
    if (errorMessage.includes('timeout') || errorMessage.includes('timed out')) {
      return LLMErrorType.TIMEOUT;
    }
    
    if (errorMessage.includes('content policy') || errorMessage.includes('content filter') || 
        errorMessage.includes('content violation') || errorMessage.includes('content flagged')) {
      return LLMErrorType.CONTENT_POLICY;
    }
    
    if (errorMessage.includes('rate limit') || errorMessage.includes('too many requests')) {
      return LLMErrorType.RATE_LIMIT;
    }
    
    if (errorMessage.includes('malformed') || errorMessage.includes('invalid json') || 
        errorMessage.includes('parse error')) {
      return LLMErrorType.MALFORMED_RESPONSE;
    }

    if (errorMessage.includes('5') && errorMessage.includes('status')) {
      return LLMErrorType.SERVER_ERROR;
    }

    if (errorMessage.includes('network') || errorMessage.includes('connection')) {
      return LLMErrorType.NETWORK_ERROR;
    }
    
    return LLMErrorType.UNKNOWN;
  }

  /**
   * Log the LLM error with appropriate information
   */
  public logError(errorType: LLMErrorType, context: LLMErrorContext): void {
    // Increment error count for monitoring
    this.errorCounts[errorType] = (this.errorCounts[errorType] || 0) + 1;
    
    // Log with appropriate level based on error type and config
    const logLevel = this.getLogLevelForErrorType(errorType);
    const timestamp = new Date().toISOString();
    
    // Create structured log message
    const logMessage = {
      timestamp,
      errorType,
      context: {
        ...context,
        prompt: context.prompt ? this.truncatePrompt(context.prompt) : undefined
      },
      errorCount: this.errorCounts[errorType]
    };
    
    this.logger.log(logLevel, 'LLM Error', logMessage);
    
    // Monitoring alert for high error rates
    if (this.config.monitoringEnabled && this.errorCounts[errorType] % 10 === 0) {
      this.logger.warn('LLM Error Rate Alert', {
        errorType,
        count: this.errorCounts[errorType],
        timeWindow: '1 hour'
      });
    }
  }

  /**
   * Get appropriate fallback response based on context and error type
   */
  public getFallbackResponse(errorType: LLMErrorType, context: LLMErrorContext): string {
    const contextType = this.determineContextType(context);
    
    // Get appropriate fallbacks based on context type
    const fallbacks = this.fallbacks[contextType] || this.fallbacks['default'];
    
    // Select a random fallback from the appropriate list
    const index = Math.floor(Math.random() * fallbacks.length);
    return fallbacks[index];
  }

  /**
   * Calculate delay for retry with exponential backoff
   */
  public getRetryDelay(retryCount: number): number {
    const { initialDelayMs, backoffFactor, jitter } = this.config.retryStrategy;
    let delay = initialDelayMs * Math.pow(backoffFactor, retryCount);
    
    // Add jitter to prevent thundering herd problem
    if (jitter) {
      const jitterAmount = delay * 0.3; // 30% jitter
      delay = delay - jitterAmount + (Math.random() * jitterAmount * 2);
    }
    
    return delay;
  }

  /**
   * Get alternative prompt for retry based on the error type and retry count
   */
  public getAlternativePrompt(originalPrompt: string, errorType: LLMErrorType, retryCount: number): string {
    const alternatives = this.config.retryStrategy.alternativePrompts;
    
    if (!alternatives || alternatives.length === 0) {
      // No alternatives available, simplify the prompt
      return this.simplifyPrompt(originalPrompt, retryCount);
    }
    
    // Use a predefined alternative if available for the retry count
    if (retryCount <= alternatives.length) {
      return alternatives[retryCount - 1];
    }
    
    // Otherwise simplify the prompt
    return this.simplifyPrompt(originalPrompt, retryCount);
  }

  /**
   * Simplify a prompt for retry by reducing its complexity
   */
  private simplifyPrompt(prompt: string, retryCount: number): string {
    // Basic simplification strategy - reduce length on each retry
    const maxLength = Math.max(100, prompt.length - (retryCount * 100));
    if (prompt.length > maxLength) {
      return prompt.substring(0, maxLength) + '...';
    }
    
    return prompt;
  }

  /**
   * Truncate prompt for logging to avoid excessive log sizes
   */
  private truncatePrompt(prompt: string): string {
    const maxLength = 200;
    if (prompt.length > maxLength) {
      return prompt.substring(0, maxLength) + '...';
    }
    return prompt;
  }

  /**
   * Determine the conversational context type from error context
   */
  private determineContextType(context: LLMErrorContext): string {
    // Extract context type from gameState or conversationId if available
    if (context.gameState?.interactionType) {
      return context.gameState.interactionType;
    }
    
    // Default context types based on prompt keywords
    const prompt = context.prompt?.toLowerCase() || '';
    
    if (prompt.includes('negotiate') || prompt.includes('deal') || prompt.includes('offer')) {
      return 'negotiation';
    }
    
    if (prompt.includes('fight') || prompt.includes('battle') || prompt.includes('combat')) {
      return 'combat';
    }
    
    if (prompt.includes('teach') || prompt.includes('learn') || prompt.includes('skill')) {
      return 'mentoring';
    }
    
    if (prompt.includes('quest') || prompt.includes('mission') || prompt.includes('task')) {
      return 'quest';
    }
    
    return 'default';
  }

  /**
   * Determine the log level based on error type
   */
  private getLogLevelForErrorType(errorType: LLMErrorType): 'debug' | 'info' | 'warn' | 'error' {
    switch (errorType) {
      case LLMErrorType.CONTENT_POLICY:
        return 'warn';
      case LLMErrorType.TIMEOUT:
      case LLMErrorType.RATE_LIMIT:
        return 'info';
      case LLMErrorType.SERVER_ERROR:
      case LLMErrorType.NETWORK_ERROR:
        return 'error';
      default:
        return this.config.logLevel;
    }
  }

  /**
   * Load the fallback response library
   */
  private loadFallbackLibrary(): Record<string, string[]> {
    // In a real implementation, this could load from a file or database
    return {
      'default': [
        "Hmm, let me think about that...",
        "I need a moment to gather my thoughts.",
        "That's an interesting question.",
        "Let me consider that for a moment.",
        "I'm not quite sure how to respond to that right now."
      ],
      'negotiation': [
        "I'll need to consider your offer carefully.",
        "Let me think about the terms you're proposing.",
        "I want to make sure this deal is fair for both of us.",
        "That's an interesting proposal. Let me think it through.",
        "I need to weigh the benefits of this arrangement."
      ],
      'combat': [
        "Let's focus on the battle at hand.",
        "We need to stay alert in this fight.",
        "Keep your guard up!",
        "Watch your surroundings carefully.",
        "We need a strategy for this confrontation."
      ],
      'mentoring': [
        "Let's approach this topic step by step.",
        "The key concept here is worth understanding fully.",
        "Take your time to absorb this information.",
        "This is an important lesson to learn.",
        "Let me find the best way to explain this."
      ],
      'quest': [
        "This quest requires careful planning.",
        "Let's consider our objectives for this mission.",
        "There may be multiple ways to approach this task.",
        "We should prepare thoroughly before proceeding.",
        "The success of this quest depends on our approach."
      ]
    };
  }

  /**
   * Get default configuration for error handling
   */
  private getDefaultConfig(): LLMErrorConfig {
    return {
      logLevel: 'info',
      retryStrategy: {
        maxRetries: 3,
        backoffFactor: 2,
        initialDelayMs: 1000,
        jitter: true,
        alternativePrompts: []
      },
      fallbackLibrary: {},
      monitoringEnabled: true
    };
  }

  /**
   * Update error handler configuration
   */
  public updateConfig(config: Partial<LLMErrorConfig>): void {
    this.config = {
      ...this.config,
      ...config,
      retryStrategy: {
        ...this.config.retryStrategy,
        ...(config.retryStrategy || {})
      }
    };
    
    if (config.fallbackLibrary) {
      this.fallbacks = {
        ...this.fallbacks,
        ...config.fallbackLibrary
      };
    }
  }

  /**
   * Reset error counts (useful for testing or after monitoring period)
   */
  public resetErrorCounts(): void {
    this.errorCounts = {};
  }
} 