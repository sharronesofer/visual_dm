from typing import Protocol, Type, TypeVar, Dict, Any

T = TypeVar('T', bound='Serializable')

class Serializable(Protocol):
    def to_dict(self) -> Dict[str, Any]:
        ...

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        ...

"""
This protocol should be implemented by all scene components (assets, objects, etc.)
that need to be included in scene persistence. It enables versioned, hierarchical
serialization and deserialization for robust save/restore functionality.
""" 