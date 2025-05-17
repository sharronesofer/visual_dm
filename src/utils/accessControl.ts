import { Building, BuildingMetadata, Room } from '../core/interfaces/types/buildings';
import { Door } from '../core/interfaces/types/building';

/**
 * Check if a character has access to a building based on metadata permissions.
 */
export function canCharacterAccessBuilding(
    characterId: string,
    metadata?: BuildingMetadata
): boolean {
    if (!metadata) return false;
    if (metadata.owner === characterId) return true;
    if (metadata.residents?.includes(characterId)) return true;
    if (metadata.accessPermissions?.[characterId]) {
        const perm = metadata.accessPermissions[characterId];
        if (!perm.expiresAt || perm.expiresAt > Date.now()) return true;
    }
    // Check for valid key
    if (metadata.keys) {
        for (const keyId in metadata.keys) {
            const key = metadata.keys[keyId];
            if (key.holderId === characterId && (!key.expiresAt || key.expiresAt > Date.now())) {
                return true;
            }
        }
    }
    return false;
}

/**
 * Check if a character has access to a room (room-level permissions override building-level).
 */
export function canCharacterAccessRoom(
    characterId: string,
    room: Room,
    buildingMetadata?: BuildingMetadata
): boolean {
    if (room.accessPermissions?.[characterId]) {
        const perm = room.accessPermissions[characterId];
        if (!perm.expiresAt || perm.expiresAt > Date.now()) return true;
    }
    if (room.residents?.includes(characterId)) return true;
    // Fallback to building-level
    return canCharacterAccessBuilding(characterId, buildingMetadata);
}

/**
 * Check if a character can open a door (door-level permissions override room/building-level).
 */
export function canCharacterAccessDoor(
    characterId: string,
    door: Door,
    room?: Room,
    buildingMetadata?: BuildingMetadata
): boolean {
    if (door.accessPermissions?.[characterId]) {
        const perm = door.accessPermissions[characterId];
        if (!perm.expiresAt || perm.expiresAt > Date.now()) return true;
    }
    // If door is locked and requires a key, check if character has the key
    if (door.isLocked && door.requiredKey && buildingMetadata?.keys) {
        const key = buildingMetadata.keys[door.requiredKey];
        if (key && key.holderId === characterId && (!key.expiresAt || key.expiresAt > Date.now())) {
            return true;
        }
    }
    // Fallback to room/building-level
    if (room && canCharacterAccessRoom(characterId, room, buildingMetadata)) return true;
    return false;
} 