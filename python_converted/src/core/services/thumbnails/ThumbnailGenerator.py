from typing import Any, List, Union


class ThumbnailOptions:
    width: float
    height: float
    quality?: float
    format?: str
    timestamp?: float
    page?: float
class ThumbnailResult:
    data: Buffer
    width: float
    height: float
    format: str
    size: float
class ThumbnailGenerator:
    generateThumbnail(input: Union[Buffer, Readable, options: ThumbnailOptions): Awaitable[ServiceResponse<ThumbnailResult>>]
    canHandle(mimeType: str): bool
    getSupportedFormats(): List[str]
    cleanup?(): Awaitable[None> 