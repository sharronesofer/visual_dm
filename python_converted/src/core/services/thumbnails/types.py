from typing import Any, List, Union


ThumbnailFormat = Union['jpeg', 'png', 'webp']
ThumbnailInput = Union[Buffer, Readable, str]
class ThumbnailOptions:
    width: float
    height: float
    quality?: float
    format?: ThumbnailFormat
    preserveAspectRatio?: bool
    timestamp?: float
    page?: float
class ThumbnailResult:
    data: Buffer
    width: float
    height: float
    format: ThumbnailFormat
    size: float
function isBuffer(input: ThumbnailInput): input is Buffer {
  return Buffer.isBuffer(input)
}
function isReadable(input: ThumbnailInput): input is Readable {
  return input instanceof Readable
}
function isFilePath(input: ThumbnailInput): input is string {
  return typeof input === 'string'
}
class ThumbnailGenerator:
    generateThumbnail(input: ThumbnailInput, options: ThumbnailOptions): Awaitable[ServiceResponse<ThumbnailResult>>
    canHandle(mimeType: str): bool
    getSupportedFormats(): List[ThumbnailFormat]
    cleanup?(): Awaitable[None> 