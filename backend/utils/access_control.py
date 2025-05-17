from typing import Optional, Dict, Any
import time

def can_character_access_building(character_id: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
    if not metadata:
        return False
    if metadata.get('owner') == character_id:
        return True
    if character_id in metadata.get('residents', []):
        return True
    access_permissions = metadata.get('accessPermissions', {})
    if character_id in access_permissions:
        perm = access_permissions[character_id]
        if not perm.get('expiresAt') or perm['expiresAt'] > int(time.time() * 1000):
            return True
    # Check for valid key
    keys = metadata.get('keys', {})
    for key in keys.values():
        if key.get('holderId') == character_id and (not key.get('expiresAt') or key['expiresAt'] > int(time.time() * 1000)):
            return True
    return False

def can_character_access_room(character_id: str, room: Dict[str, Any], building_metadata: Optional[Dict[str, Any]] = None) -> bool:
    access_permissions = room.get('accessPermissions', {})
    if character_id in access_permissions:
        perm = access_permissions[character_id]
        if not perm.get('expiresAt') or perm['expiresAt'] > int(time.time() * 1000):
            return True
    if character_id in room.get('residents', []):
        return True
    # Fallback to building-level
    return can_character_access_building(character_id, building_metadata)

def can_character_access_door(character_id: str, door: Dict[str, Any], room: Optional[Dict[str, Any]] = None, building_metadata: Optional[Dict[str, Any]] = None) -> bool:
    access_permissions = door.get('accessPermissions', {})
    if character_id in access_permissions:
        perm = access_permissions[character_id]
        if not perm.get('expiresAt') or perm['expiresAt'] > int(time.time() * 1000):
            return True
    # If door is locked and requires a key, check if character has the key
    if door.get('isLocked') and door.get('requiredKey') and building_metadata and 'keys' in building_metadata:
        key = building_metadata['keys'].get(door['requiredKey'])
        if key and key.get('holderId') == character_id and (not key.get('expiresAt') or key['expiresAt'] > int(time.time() * 1000)):
            return True
    # Fallback to room/building-level
    if room and can_character_access_room(character_id, room, building_metadata):
        return True
    return False 