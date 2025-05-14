from typing import Any, Dict


class GPTServiceOptions:
    maxRetries?: float
    timeoutMs?: float
class GPTServiceWrapper {
  private static instance: \'GPTServiceWrapper\'
  private gptService: GPTService
  private errorHandler: LLMErrorHandler
  private defaultOptions: \'GPTServiceOptions\' = {
    maxRetries: 3,
    timeoutMs: 10000
  }
  private constructor() {
    this.gptService = GPTService.getInstance()
    this.errorHandler = LLMErrorHandler.getInstance()
  }
  public static getInstance(): \'GPTServiceWrapper\' {
    if (!GPTServiceWrapper.instance) {
      GPTServiceWrapper.instance = new GPTServiceWrapper()
    }
    return GPTServiceWrapper.instance
  }
  /**
   * Generate names with error handling and retries
   */
  public async generateNames(params: Dict[str, Any], options?: GPTServiceOptions): Promise<any> {
    const mergedOptions = { ...this.defaultOptions, ...options }
    let retryCount = 0
    let lastError: Error | null = null
    const errorContext: LLMErrorContext = {
      timestamp: Date.now(),
      prompt: `Generate ${params.count || 5} fantasy character names for ${params.race} ${params.class} with ${params.alignment} alignment`,
      gameState: Dict[str, Any]
    }
    while (retryCount <= mergedOptions.maxRetries!) {
      try {
        const timeoutPromise = new Promise<never>((_, reject) => {
          setTimeout(() => reject(new Error('GPT request timed out')), mergedOptions.timeoutMs)
        })
        const result = await Promise.race([
          this.gptService.generateNames(params),
          timeoutPromise
        ])
        return result
      } catch (error) {
        lastError = error as Error
        const errorType = this.errorHandler.identifyErrorType(lastError)
        this.errorHandler.logError(errorType, errorContext)
        const delayMs = this.errorHandler.getRetryDelay(retryCount)
        if (retryCount < mergedOptions.maxRetries!) {
          await new Promise(resolve => setTimeout(resolve, delayMs))
          retryCount++
          if (errorType === LLMErrorType.CONTENT_POLICY) {
            params.alignment = 'neutral'
          }
        } else {
          return this.handleNameGenerationFallback(params, errorContext, errorType)
        }
      }
    }
    throw lastError 
  }
  /**
   * Generate background with error handling and retries
   */
  public async generateBackground(params: Dict[str, Any], options?: GPTServiceOptions): Promise<string> {
    const mergedOptions = { ...this.defaultOptions, ...options }
    let retryCount = 0
    let lastError: Error | null = null
    const prompt = `Create a background story for a ${params.alignment} ${params.race} ${params.class} named ${params.name}`
    const errorContext: LLMErrorContext = {
      timestamp: Date.now(),
      prompt,
      gameState: Dict[str, Any]
    }
    while (retryCount <= mergedOptions.maxRetries!) {
      try {
        const timeoutPromise = new Promise<never>((_, reject) => {
          setTimeout(() => reject(new Error('GPT request timed out')), mergedOptions.timeoutMs)
        })
        const result = await Promise.race([
          this.gptService.generateBackground(params),
          timeoutPromise
        ])
        return result
      } catch (error) {
        lastError = error as Error
        const errorType = this.errorHandler.identifyErrorType(lastError)
        this.errorHandler.logError(errorType, errorContext)
        const delayMs = this.errorHandler.getRetryDelay(retryCount)
        if (retryCount < mergedOptions.maxRetries!) {
          await new Promise(resolve => setTimeout(resolve, delayMs))
          retryCount++
          if (errorType === LLMErrorType.CONTENT_POLICY) {
            params.alignment = 'neutral'
          }
        } else {
          return this.handleBackgroundGenerationFallback(params, errorContext, errorType)
        }
      }
    }
    throw lastError 
  }
  /**
   * Direct access to GPT API with error handling and retries
   * This can be used for any custom prompts, including dialogue
   */
  public async generateText(prompt: str, 
                          options: Dict[str, Any] & GPTServiceOptions = {}): Promise<string> {
    const { maxTokens = 100, temperature = 0.7, contextType = 'default', characterId, gameState, ...retryOptions } = options
    const mergedOptions = { ...this.defaultOptions, ...retryOptions }
    let retryCount = 0
    let lastError: Error | null = null
    let currentPrompt = prompt
    const errorContext: LLMErrorContext = {
      timestamp: Date.now(),
      prompt,
      characterId,
      gameState: Dict[str, Any]
    }
    while (retryCount <= mergedOptions.maxRetries!) {
      try {
        const timeoutPromise = new Promise<never>((_, reject) => {
          setTimeout(() => reject(new Error('GPT request timed out')), mergedOptions.timeoutMs)
        })
        const response = await Promise.race([
          this.makeGptRequest(currentPrompt, maxTokens, temperature),
          timeoutPromise
        ])
        if (response.error) {
          throw new Error(response.error.message)
        }
        return response.data.choices[0].text.trim()
      } catch (error) {
        lastError = error as Error
        const errorType = this.errorHandler.identifyErrorType(lastError)
        this.errorHandler.logError(errorType, errorContext)
        const delayMs = this.errorHandler.getRetryDelay(retryCount)
        if (retryCount < mergedOptions.maxRetries!) {
          await new Promise(resolve => setTimeout(resolve, delayMs))
          currentPrompt = this.errorHandler.getAlternativePrompt(prompt, errorType, retryCount + 1)
          retryCount++
        } else {
          return this.errorHandler.getFallbackResponse(errorType, errorContext)
        }
      }
    }
    throw lastError 
  }
  /**
   * Private method to make GPT API requests
   */
  private async makeGptRequest(prompt: str, maxTokens: float, temperature: float): Promise<ApiResponse> {
    return this.gptService['apiService'].post('/api/gpt/generate', {
      prompt,
      max_tokens: maxTokens,
      temperature
    })
  }
  /**
   * Handle fallback for name generation
   */
  private handleNameGenerationFallback(
    params: Dict[str, Any],
    errorContext: LLMErrorContext,
    errorType: LLMErrorType
  ): { name: str; description: str }[] {
    const count = params.count || 5
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
    ]
    const selectedNames = []
    for (let i = 0; i < Math.min(count, fallbackNames.length); i++) {
      selectedNames.push(fallbackNames[i])
    }
    return selectedNames
  }
  /**
   * Handle fallback for background generation
   */
  private handleBackgroundGenerationFallback(
    params: Dict[str, Any],
    errorContext: LLMErrorContext,
    errorType: LLMErrorType
  ): str {
    return `${params.name} is a ${params.alignment} ${params.race} ${params.class} who has led an adventurous life. 
    Born in a small settlement, ${params.name} trained diligently to master the skills of a ${params.class}. 
    After facing numerous challenges and overcoming significant obstacles, ${params.name} decided to seek 
    greater adventures and make a name in the world. With a strong sense of ${this.getValueForAlignment(params.alignment)}, 
    ${params.name} continues to pursue worthy goals while developing greater mastery of ${params.class} abilities.`
  }
  /**
   * Helper to get alignment-appropriate values
   */
  private getValueForAlignment(alignment: str): str {
    alignment = alignment.toLowerCase()
    if (alignment.includes('good')) return 'justice and compassion'
    if (alignment.includes('evil')) return 'power and ambition'
    if (alignment.includes('lawful')) return 'order and tradition'
    if (alignment.includes('chaotic')) return 'freedom and individuality'
    return 'balance and pragmatism' 
  }
} 