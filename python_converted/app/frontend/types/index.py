from typing import Any, Dict, Union


class MediaAsset:
    id: str
    filename: str
    mimeType: str
    type: Union['image', 'video', 'audio', 'document']
    size: float
    width?: float
    height?: float
    duration?: float
    thumbnailUrl: Union[str, None]
    createdAt?: str
    updatedAt?: str
    metadata?: Dict[str, unknown> 