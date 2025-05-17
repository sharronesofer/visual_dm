import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { EventEmitter } from 'events';

export interface GPTConfig {
    model: string;
    temperature?: number;
    maxTokens?: number;
    stop?: string[];
    [key: string]: any;
}

export interface GPTResponse {
    text: string;
    usage?: {
        prompt_tokens: number;
        completion_tokens: number;
        total_tokens: number;
    };
    raw?: any;
    error?: string;
}

export interface GPTClientOptions {
    apiKey: string;
    apiUrl?: string;
    rateLimit?: number;
    timeoutMs?: number;
    maxRetries?: number;
    backoffBaseMs?: number;
}

export interface GPTUsageStats {
    totalTokens: number;
    rollingTokens: number;
    windowMs: number;
    lastReset: number;
}

/**
 * GPTClient: Handles GPT/OpenAI API requests, prompt/context management, and emotion context formatting for LLMs.
 * Emits events for request, error, and fallback. Provides static helpers for prompt injection.
 */
export class GPTClient extends EventEmitter {
    private apiKey: string;
    private apiUrl: string;
    private axios: AxiosInstance;
    private rateLimit: number;
    private requests: number[] = [];
    private timeoutMs: number;
    private maxRetries: number;
    private backoffBaseMs: number;
    private usageStats: GPTUsageStats;
    private usageWindowMs = 60000;

    constructor({ apiKey, apiUrl = 'https://api.openai.com/v1/chat/completions', rateLimit = 60, timeoutMs = 10000, maxRetries = 3, backoffBaseMs = 500 }: GPTClientOptions) {
        super();
        this.apiKey = apiKey;
        this.apiUrl = apiUrl;
        this.rateLimit = rateLimit;
        this.timeoutMs = timeoutMs;
        this.maxRetries = maxRetries;
        this.backoffBaseMs = backoffBaseMs;
        this.axios = axios.create({
            baseURL: this.apiUrl,
            timeout: this.timeoutMs,
            headers: {
                'Authorization': `Bearer ${this.apiKey}`,
                'Content-Type': 'application/json',
            },
        });
        this.usageStats = { totalTokens: 0, rollingTokens: 0, windowMs: this.usageWindowMs, lastReset: Date.now() };
    }

    /**
     * Generates a GPT completion given a prompt and context.
     * Emits 'request', 'error', and 'fallback' events.
     */
    async generateCompletion(prompt: string, context: string[], config: GPTConfig): Promise<GPTResponse> {
        await this.enforceRateLimit();
        const messages = [
            ...context.map((c) => ({ role: 'system', content: c })),
            { role: 'user', content: prompt },
        ];
        const payload = {
            ...config,
            messages,
            temperature: config.temperature ?? 0.7,
            max_tokens: config.maxTokens ?? 512,
            stop: config.stop,
        };
        this.emit('request', { prompt, context, config: payload });
        try {
            const response = await this.axios.post('', payload);
            const choice = response.data.choices?.[0]?.message?.content || '';
            this.updateUsage(response.data.usage?.total_tokens);
            return {
                text: choice,
                usage: response.data.usage,
                raw: response.data,
            };
        } catch (error: any) {
            this.emit('error', error);
            // Fallback logic: retry with exponential backoff up to maxRetries
            for (let attempt = 1; attempt <= this.maxRetries; attempt++) {
                await this.sleep(2 ** attempt * this.backoffBaseMs);
                try {
                    const response = await this.axios.post('', payload);
                    const choice = response.data.choices?.[0]?.message?.content || '';
                    this.updateUsage(response.data.usage?.total_tokens);
                    return {
                        text: choice,
                        usage: response.data.usage,
                        raw: response.data,
                    };
                } catch (err: any) {
                    if (attempt === this.maxRetries) {
                        this.emit('fallback', err);
                        return { text: '', error: err.message, raw: err.response?.data };
                    }
                }
            }
            return { text: '', error: error.message, raw: error.response?.data };
        }
    }

    /**
     * Enforces the rate limit by delaying if necessary.
     */
    private async enforceRateLimit() {
        const now = Date.now();
        this.requests = this.requests.filter((t) => now - t < 60000);
        if (this.requests.length >= this.rateLimit) {
            const wait = 60000 - (now - this.requests[0]);
            await this.sleep(wait);
        }
        this.requests.push(now);
    }

    /**
     * Updates token usage statistics.
     */
    private updateUsage(tokens?: number) {
        const now = Date.now();
        if (now - this.usageStats.lastReset > this.usageWindowMs) {
            this.usageStats.rollingTokens = 0;
            this.usageStats.lastReset = now;
        }
        if (tokens) {
            this.usageStats.totalTokens += tokens;
            this.usageStats.rollingTokens += tokens;
        }
    }

    /**
     * Returns current usage statistics.
     */
    getUsageStats(): GPTUsageStats {
        return { ...this.usageStats };
    }

    /**
     * Utility to sleep for ms milliseconds.
     */
    private sleep(ms: number) {
        return new Promise((resolve) => setTimeout(resolve, ms));
    }

    /**
     * Counts tokens in a string (approximate, for OpenAI models).
     */
    static countTokens(text: string): number {
        // Simple approximation: 1 token ≈ 4 characters (for English)
        return Math.ceil(text.length / 4);
    }

    /**
     * Formats emotion context for prompt injection.
     * @param emotions Array of emotion objects with name, intensity, and optional description
     * @returns String for prompt injection, e.g., 'Current emotions: joy (intensity: 0.8), anger (intensity: 0.5)'
     */
    static formatEmotionContextForPrompt(emotions: Array<{ name: string, intensity: number, description?: string }>): string {
        if (!emotions.length) return 'No emotions are currently active.';
        return 'Current emotions: ' + emotions.map(e => `${e.name} (intensity: ${e.intensity}${e.description ? ', ' + e.description : ''})`).join(', ');
    }
} 