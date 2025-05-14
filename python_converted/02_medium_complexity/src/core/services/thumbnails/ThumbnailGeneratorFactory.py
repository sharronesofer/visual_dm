from typing import Any



class ThumbnailGeneratorFactory {
  private static instance: \'ThumbnailGeneratorFactory\'
  private generators: Map<string, ThumbnailGenerator>
  private constructor() {
    this.generators = new Map()
    this.initializeGenerators()
  }
  public static getInstance(): \'ThumbnailGeneratorFactory\' {
    if (!ThumbnailGeneratorFactory.instance) {
      ThumbnailGeneratorFactory.instance = new ThumbnailGeneratorFactory()
    }
    return ThumbnailGeneratorFactory.instance
  }
  private initializeGenerators(): void {
    this.generators.set('image/jpeg', new ImageThumbnailGenerator())
    this.generators.set('image/png', new ImageThumbnailGenerator())
    this.generators.set('image/gif', new ImageThumbnailGenerator())
    this.generators.set('image/webp', new ImageThumbnailGenerator())
    this.generators.set('video/mp4', new VideoThumbnailGenerator())
    this.generators.set('video/webm', new VideoThumbnailGenerator())
    this.generators.set('video/ogg', new VideoThumbnailGenerator())
    this.generators.set('application/pdf', new DocumentThumbnailGenerator())
    this.generators.set('application/msword', new DocumentThumbnailGenerator())
    this.generators.set('application/vnd.openxmlformats-officedocument.wordprocessingml.document', new DocumentThumbnailGenerator())
  }
  public getGenerator(mimeType: str): ThumbnailGenerator {
    const generator = this.generators.get(mimeType)
    if (!generator) {
      throw new ServiceError('UnsupportedMediaType', `No thumbnail generator available for MIME type: ${mimeType}`)
    }
    return generator
  }
  public isMimeTypeSupported(mimeType: str): bool {
    return this.generators.has(mimeType)
  }
  public getSupportedMimeTypes(): string[] {
    return Array.from(this.generators.keys())
  }
} 