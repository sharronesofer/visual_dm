import { EventEmitter } from 'events';
import { ProcessingJob, ProcessingJobStatus } from '../types/MediaProcessing';
import { ServiceError } from '../base/types';
import { QueueConfig } from '../config/ConfigManager';

export class JobQueue extends EventEmitter {
  private queue: ProcessingJob[] = [];
  private processing: Set<string> = new Set();
  private config: QueueConfig;

  constructor() {
    super();
    this.config = {
      maxConcurrent: 5,
      maxQueueSize: 100,
      retryAttempts: 3,
      retryDelay: 1000
    };
  }

  public configure(config: Partial<QueueConfig>): void {
    this.config = { ...this.config, ...config };
  }

  public async initialize(): Promise<void> {
    // Initialize queue system, connections, etc.
  }

  public async enqueue(job: ProcessingJob): Promise<void> {
    if (this.queue.length >= this.config.maxQueueSize) {
      throw new ServiceError(
        'QueueError',
        'Queue is full',
        { queueSize: this.queue.length, maxSize: this.config.maxQueueSize }
      );
    }

    this.queue.push(job);
    this.emit('jobQueued', job);

    // Try to process jobs if we're not at max concurrent
    await this.processNextJobs();
  }

  public async dequeue(jobId: string): Promise<void> {
    const index = this.queue.findIndex(job => job.id === jobId);
    if (index !== -1) {
      const job = this.queue[index];
      this.queue.splice(index, 1);
      this.emit('jobDequeued', job);
    }
  }

  public getQueueLength(): number {
    return this.queue.length;
  }

  public getProcessingCount(): number {
    return this.processing.size;
  }

  public isProcessing(jobId: string): boolean {
    return this.processing.has(jobId);
  }

  public async clear(): Promise<void> {
    this.queue = [];
    this.emit('queueCleared');
  }

  private async processNextJobs(): Promise<void> {
    while (
      this.queue.length > 0 &&
      this.processing.size < this.config.maxConcurrent
    ) {
      const job = this.queue.shift();
      if (job) {
        await this.processJob(job);
      }
    }
  }

  private async processJob(job: ProcessingJob): Promise<void> {
    this.processing.add(job.id);
    this.emit('jobStarted', job);

    let attempts = 0;
    let lastError: Error | undefined;

    while (attempts < this.config.retryAttempts) {
      try {
        job.status = ProcessingJobStatus.PROCESSING;
        this.emit('jobProcessing', job);

        // Simulate job processing (replace with actual processing logic)
        await new Promise(resolve => setTimeout(resolve, 1000));

        job.status = ProcessingJobStatus.COMPLETED;
        this.emit('jobCompleted', job);
        this.processing.delete(job.id);

        // Try to process next jobs
        await this.processNextJobs();
        return;
      } catch (error) {
        attempts++;
        lastError = error as Error;

        if (attempts < this.config.retryAttempts) {
          // Wait before retrying
          await new Promise(resolve =>
            setTimeout(resolve, this.config.retryDelay * attempts)
          );
          this.emit('jobRetrying', { job, attempt: attempts, error });
        }
      }
    }

    // All retry attempts failed
    job.status = ProcessingJobStatus.FAILED;
    job.error = lastError;
    this.emit('jobFailed', { job, error: lastError });
    this.processing.delete(job.id);

    // Try to process next jobs
    await this.processNextJobs();
  }
} 