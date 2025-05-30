from typing import Any, List



class JobQueue extends EventEmitter {
  private queue: List[ProcessingJob] = []
  private processing: Set<string> = new Set()
  private config: QueueConfig
  constructor() {
    super()
    this.config = {
      maxConcurrent: 5,
      maxQueueSize: 100,
      retryAttempts: 3,
      retryDelay: 1000
    }
  }
  public configure(config: Partial<QueueConfig>): void {
    this.config = { ...this.config, ...config }
  }
  public async initialize(): Promise<void> {
  }
  public async enqueue(job: ProcessingJob): Promise<void> {
    if (this.queue.length >= this.config.maxQueueSize) {
      throw new ServiceError(
        'QueueError',
        'Queue is full',
        { queueSize: this.queue.length, maxSize: this.config.maxQueueSize }
      )
    }
    this.queue.push(job)
    this.emit('jobQueued', job)
    await this.processNextJobs()
  }
  public async dequeue(jobId: str): Promise<void> {
    const index = this.queue.findIndex(job => job.id === jobId)
    if (index !== -1) {
      const job = this.queue[index]
      this.queue.splice(index, 1)
      this.emit('jobDequeued', job)
    }
  }
  public getQueueLength(): float {
    return this.queue.length
  }
  public getProcessingCount(): float {
    return this.processing.size
  }
  public isProcessing(jobId: str): bool {
    return this.processing.has(jobId)
  }
  public async clear(): Promise<void> {
    this.queue = []
    this.emit('queueCleared')
  }
  private async processNextJobs(): Promise<void> {
    while (
      this.queue.length > 0 &&
      this.processing.size < this.config.maxConcurrent
    ) {
      const job = this.queue.shift()
      if (job) {
        await this.processJob(job)
      }
    }
  }
  private async processJob(job: ProcessingJob): Promise<void> {
    this.processing.add(job.id)
    this.emit('jobStarted', job)
    let attempts = 0
    let lastError: Error | undefined
    while (attempts < this.config.retryAttempts) {
      try {
        job.status = ProcessingJobStatus.PROCESSING
        this.emit('jobProcessing', job)
        await new Promise(resolve => setTimeout(resolve, 1000))
        job.status = ProcessingJobStatus.COMPLETED
        this.emit('jobCompleted', job)
        this.processing.delete(job.id)
        await this.processNextJobs()
        return
      } catch (error) {
        attempts++
        lastError = error as Error
        if (attempts < this.config.retryAttempts) {
          await new Promise(resolve =>
            setTimeout(resolve, this.config.retryDelay * attempts)
          )
          this.emit('jobRetrying', { job, attempt: attempts, error })
        }
      }
    }
    job.status = ProcessingJobStatus.FAILED
    job.error = lastError
    this.emit('jobFailed', { job, error: lastError })
    this.processing.delete(job.id)
    await this.processNextJobs()
  }
} 