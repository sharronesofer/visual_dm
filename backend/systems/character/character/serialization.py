import json
from typing import Dict, Any

SERIALIZATION_VERSION = "1.0"

def serialize_character(character: Any) -> str:
    """
    Serialize a character model to a JSON string, including versioning.
    """
    data = {
        "version": SERIALIZATION_VERSION,
        "character": character.to_dict()
    }
    return json.dumps(data, indent=2)

def deserialize_character(data: str, character_cls: Any) -> Any:
    """
    Deserialize a character model from a JSON string.
    """
    obj = json.loads(data)
    version = obj.get("version", "1.0")
    # Future: handle migrations based on version
    return character_cls.from_dict(obj["character"]) 