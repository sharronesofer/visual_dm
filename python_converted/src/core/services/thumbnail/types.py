from typing import Any, Union


class ThumbnailOptions:
    width?: float
    height?: float
    quality?: float
    format?: Union['jpeg', 'png', 'webp']
    maintainAspectRatio?: bool
    timestamp?: float
    page?: float
class ThumbnailResult:
    buffer: Buffer
    width: float
    height: float
    format: str
    size: float
class ThumbnailGenerator:
    generate(input: Union[str, Buffer, options?: ThumbnailOptions): Awaitable[ThumbnailResult>]
    supports(mimeType: str): bool
type ServiceResponse<T> =
  | { success: true; data: T }
  | { success: false; error: \'ServiceError\' }
class ServiceError:
    code: str
    message: str
    details?: Any 