/**
 * Async utilities used across the application
 */

/**
 * Creates a promise that resolves after a specified delay
 */
export const delay = (ms: number): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms));
};

/**
 * Creates a debounced version of a function
 */
export function debounce<T extends (...args: any[]) => any>(
  fn: T,
  ms: number
): (...args: Parameters<T>) => Promise<ReturnType<T>> {
  let timeoutId: NodeJS.Timeout;
  let pendingPromise: Promise<ReturnType<T>> | null = null;
  let pendingResolve: ((value: ReturnType<T>) => void) | null = null;

  return (...args: Parameters<T>) => {
    if (!pendingPromise) {
      pendingPromise = new Promise(resolve => {
        pendingResolve = resolve as (value: ReturnType<T>) => void;
      });
    }

    clearTimeout(timeoutId);
    timeoutId = setTimeout(async () => {
      const result = await fn(...args);
      if (pendingResolve) {
        pendingResolve(result);
        pendingPromise = null;
        pendingResolve = null;
      }
    }, ms);

    return pendingPromise;
  };
}

/**
 * Creates a throttled version of a function
 */
export function throttle<T extends (...args: any[]) => any>(
  fn: T,
  ms: number
): (...args: Parameters<T>) => Promise<ReturnType<T>> {
  let timeoutId: NodeJS.Timeout | null = null;
  let lastRun = 0;
  let pendingPromise: Promise<ReturnType<T>> | null = null;
  let pendingResolve: ((value: ReturnType<T>) => void) | null = null;

  return (...args: Parameters<T>) => {
    const now = Date.now();

    if (!pendingPromise) {
      pendingPromise = new Promise(resolve => {
        pendingResolve = resolve as (value: ReturnType<T>) => void;
      });
    }

    if (!timeoutId && now - lastRun >= ms) {
      lastRun = now;
      fn(...args).then((result: ReturnType<T>) => {
        if (pendingResolve) {
          pendingResolve(result);
          pendingPromise = null;
          pendingResolve = null;
        }
      });
    } else {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
      timeoutId = setTimeout(
        async () => {
          lastRun = Date.now();
          const result = await fn(...args);
          timeoutId = null;
          if (pendingResolve) {
            pendingResolve(result);
            pendingPromise = null;
            pendingResolve = null;
          }
        },
        Math.max(0, ms - (now - lastRun))
      );
    }

    return pendingPromise;
  };
}

/**
 * Creates a memoized version of an async function
 */
export function memoizeAsync<T extends (...args: any[]) => Promise<any>>(
  fn: T,
  options: {
    maxSize?: number;
    maxAge?: number;
    keyFn?: (...args: Parameters<T>) => string;
  } = {}
): T {
  const {
    maxSize = 100,
    maxAge = 5 * 60 * 1000, // 5 minutes
    keyFn = (...args) => JSON.stringify(args),
  } = options;

  const cache = new Map<string, { value: ReturnType<T>; timestamp: number }>();

  return (async (...args: Parameters<T>) => {
    const key = keyFn(...args);
    const now = Date.now();
    const cached = cache.get(key);

    if (cached && now - cached.timestamp < maxAge) {
      return cached.value;
    }

    const value = await fn(...args);
    cache.set(key, { value, timestamp: now });

    if (cache.size > maxSize) {
      // Remove oldest entries
      const entries = Array.from(cache.entries());
      entries.sort((a, b) => a[1].timestamp - b[1].timestamp);
      const toDelete = entries.slice(0, entries.length - maxSize);
      toDelete.forEach(([key]) => cache.delete(key));
    }

    return value;
  }) as T;
}

/**
 * Creates a retry wrapper for an async function
 */
export async function retry<T>(
  fn: () => Promise<T>,
  options: {
    maxAttempts?: number;
    delay?: number;
    backoff?: number;
    shouldRetry?: (error: any) => boolean;
  } = {}
): Promise<T> {
  const {
    maxAttempts = 3,
    delay: initialDelay = 1000,
    backoff = 2,
    shouldRetry = () => true,
  } = options;

  let lastError: any;
  let attempt = 0;
  let delay = initialDelay;

  while (attempt < maxAttempts) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      attempt++;

      if (attempt === maxAttempts || !shouldRetry(error)) {
        throw error;
      }

      await new Promise(resolve => setTimeout(resolve, delay));
      delay *= backoff;
    }
  }

  throw lastError;
}

/**
 * Creates a queue for processing async tasks sequentially
 */
export class AsyncQueue {
  private queue: (() => Promise<any>)[] = [];
  private processing = false;

  /**
   * Adds a task to the queue
   */
  async enqueue<T>(task: () => Promise<T>): Promise<T> {
    return new Promise((resolve, reject) => {
      this.queue.push(async () => {
        try {
          const result = await task();
          resolve(result);
        } catch (error) {
          reject(error);
        }
      });

      if (!this.processing) {
        this.processQueue();
      }
    });
  }

  /**
   * Processes tasks in the queue
   */
  private async processQueue() {
    if (this.processing || this.queue.length === 0) {
      return;
    }

    this.processing = true;

    while (this.queue.length > 0) {
      const task = this.queue.shift();
      if (task) {
        await task();
      }
    }

    this.processing = false;
  }

  /**
   * Gets the current queue size
   */
  size(): number {
    return this.queue.length;
  }

  /**
   * Clears all pending tasks
   */
  clear(): void {
    this.queue = [];
  }
}
