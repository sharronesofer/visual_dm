"""
NPC Leveling Utilities
Assigns NPC level at creation based on job/role.
See docs/stubs_needs_consolidation_qna.md for requirements.

- Level Assignment: Assigns level at creation based on job/role (city watch, shop owner, royal guard, administrator, etc.).
- Extensibility: Supports new roles and custom level logic; can be expanded for future job types.
- Integration: Used in conflict/revolt simulation to determine faction strength in POIs.
- Event Logging: TODO: Log major level changes or role changes as world events if needed.
"""

NPC_ROLE_LEVELS = {
    "shop_owner": 1,
    "laborer": 1,
    "apprentice": 2,
    "city_watch": 3,
    "guard": 4,
    "administrator": 5,
    "royal_guard": 6,
    "noble": 7,
    "hero": 8,
    "villain": 9,
    "legend": 10
}

def get_npc_level(role: str) -> int:
    """
    Get the default level for an NPC based on their job/role.
    Returns 1 if role is unknown.
    """
    return NPC_ROLE_LEVELS.get(role, 1)


def assign_npc_level(npc_data: dict) -> dict:
    """
    Assign a level to an NPC at creation based on their role.
    Modifies npc_data in place and returns it.
    """
    role = npc_data.get("role", "laborer")
    npc_data["level"] = get_npc_level(role)
    return npc_data 