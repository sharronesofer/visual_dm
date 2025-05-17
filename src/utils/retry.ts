/**
 * Retry utility with exponential backoff and jitter for async operations.
 */
export interface RetryOptions {
    maxAttempts?: number;
    initialDelayMs?: number;
    maxDelayMs?: number;
    factor?: number;
    jitter?: boolean;
    onRetry?: (attempt: number, error: unknown) => void;
}

/**
 * Retry an async function with exponential backoff and optional jitter.
 * Throws the last error if all attempts fail.
 */
export async function retryAsync<T>(
    fn: () => Promise<T>,
    options: RetryOptions = {}
): Promise<T> {
    const {
        maxAttempts = 5,
        initialDelayMs = 100,
        maxDelayMs = 5000,
        factor = 2,
        jitter = true,
        onRetry,
    } = options;
    let attempt = 0;
    let delay = initialDelayMs;
    let lastError: unknown;
    while (attempt < maxAttempts) {
        try {
            return await fn();
        } catch (err) {
            lastError = err;
            attempt++;
            if (onRetry) onRetry(attempt, err);
            if (attempt >= maxAttempts) break;
            let sleep = delay;
            if (jitter) {
                sleep = Math.floor(Math.random() * delay);
            }
            // eslint-disable-next-line no-console
            console.warn(`[retry] attempt ${attempt} failed, retrying in ${sleep}ms`, err);
            await new Promise((resolve) => setTimeout(resolve, sleep));
            delay = Math.min(delay * factor, maxDelayMs);
        }
    }
    throw lastError;
} 