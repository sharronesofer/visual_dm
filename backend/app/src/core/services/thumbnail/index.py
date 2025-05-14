from typing import Any, Dict, List


class ThumbnailService {
  private generators: List[ThumbnailGenerator] = []
  constructor() {
    this.generators = [
      new ImageThumbnailGenerator(),
      new VideoThumbnailGenerator(),
      new AudioThumbnailGenerator(),
      new DocumentThumbnailGenerator(),
    ]
  }
  public async generateThumbnail(
    input: str | Buffer,
    mimeType: str,
    options?: ThumbnailOptions
  ): Promise<ServiceResponse<ThumbnailResult>> {
    try {
      const generator = this.getGenerator(mimeType)
      if (!generator) {
        return {
          success: false,
          error: Dict[str, Any]`,
          },
        }
      }
      const result = await generator.generate(input, options)
      return {
        success: true,
        data: result,
      }
    } catch (error) {
      return {
        success: false,
        error: this.formatError(error),
      }
    }
  }
  private getGenerator(mimeType: str): ThumbnailGenerator | undefined {
    return this.generators.find((generator) => generator.supports(mimeType))
  }
  private formatError(error: Any): ServiceError {
    if (error instanceof ValidationError || error instanceof ThumbnailServiceError) {
      return {
        code: error.code,
        message: error.message,
        details: error.details,
      }
    }
    return {
      code: 'INTERNAL_ERROR',
      message: error?.message || 'Unknown error',
      details: error,
    }
  }
} 