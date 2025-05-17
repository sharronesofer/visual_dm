#This module compiles a comprehensive narrative context bundle for GPT-powered Dungeon Master interactions. It pulls motifs, region arcs, tension levels, memory logs, and faction affiliations from Firebase and internal engines.
#It fully integrates with narrative, motif, firebase, memory, npc, faction, and chaos systems.

from firebase_admin import db
from app.memory.memory_utils import get_recent_interactions
from app.motifs.motif_engine_class import MotifEngine
from app.regions.tension_utils import get_tension
from app.core.utils.gpt.client import GPTClient, call
from functools import lru_cache
from datetime import datetime, timedelta
from app.dm_engine.dm_utils import MOTIF_THEME_NAMES
from typing import Dict, Any, List, Optional
from app.core.models.character import Character
from app.core.models.world import Region
from app.core.models.quest import Quest
from app.core.utils.event_utils import EventUtils
from app.core.utils.world_tick_utils import WorldTickUtils
import logging

_context_cache = {}
_CONTEXT_TTL = timedelta(seconds=30)  # Cache for 30 seconds

logger = logging.getLogger(__name__)

class DMHelperUtils:
    """Utility class for DM operations."""
    
    def __init__(self):
        """Initialize the DM helper utilities."""
        self.event_utils = EventUtils()
        self.world_tick_utils = WorldTickUtils()

    def generate_encounter(
        self,
        characters: List[Character],
        region: Region,
        difficulty: str = 'normal'
    ) -> Dict[str, Any]:
        """Generate an encounter for the given characters in a region.
        
        Args:
            characters: List of characters to generate encounter for
            region: The region where the encounter occurs
            difficulty: The difficulty level of the encounter
            
        Returns:
            Dict containing encounter details
        """
        try:
            # Calculate average party level
            avg_level = sum(char.level for char in characters) / len(characters)
            
            # Generate encounter based on region and difficulty
            encounter = {
                'type': self._get_encounter_type(region),
                'level': int(avg_level),
                'difficulty': difficulty,
                'region': region.name,
                'participants': [char.name for char in characters],
                'description': self._generate_encounter_description(region, difficulty),
                'rewards': self._calculate_rewards(avg_level, difficulty)
            }
            
            logger.debug(f"Generated encounter: {encounter}")
            return encounter
            
        except Exception as e:
            logger.error(f"Error generating encounter: {str(e)}")
            return {}

    def assign_quest(
        self,
        characters: List[Character],
        region: Region,
        quest_type: str = 'hunt'
    ) -> Optional[Quest]:
        """Assign a quest to characters in a region.
        
        Args:
            characters: List of characters to assign quest to
            region: The region where the quest takes place
            quest_type: The type of quest to generate
            
        Returns:
            Quest object if successful, None otherwise
        """
        try:
            # Calculate average party level
            avg_level = sum(char.level for char in characters) / len(characters)
            
            # Generate quest
            quest = self.event_utils.generate_quest(
                level=int(avg_level),
                quest_type=quest_type,
                difficulty=self._get_quest_difficulty(region)
            )
            
            if quest:
                # Assign quest to characters
                for char in characters:
                    char.active_quests.append(quest)
                    
                logger.debug(f"Assigned quest to characters: {quest}")
                return quest
                
        except Exception as e:
            logger.error(f"Error assigning quest: {str(e)}")
            
        return None

    def process_world_tick(self, regions: List[Region]) -> List[Dict[str, Any]]:
        """Process a world tick for all regions.
        
        Args:
            regions: List of regions to process
            
        Returns:
            List of events generated during the tick
        """
        return self.world_tick_utils.process_tick(regions)

    def _get_encounter_type(self, region: Region) -> str:
        """Get the type of encounter to generate for a region.
        
        Args:
            region: The region to get encounter type for
            
        Returns:
            str: The encounter type
        """
        # Weight different encounter types based on region properties
        weights = {
            'combat': 0.4,
            'social': region.population_density / 1000,
            'exploration': 0.3,
            'mystical': region.magic_level / 100
        }
        
        # Normalize weights
        total = sum(weights.values())
        weights = {k: v/total for k, v in weights.items()}
        
        # Choose encounter type based on weights
        import random
        return random.choices(list(weights.keys()), weights=list(weights.values()))[0]

    def _generate_encounter_description(
        self,
        region: Region,
        difficulty: str
    ) -> str:
        """Generate a description for an encounter.
        
        Args:
            region: The region where the encounter occurs
            difficulty: The difficulty level of the encounter
            
        Returns:
            str: The encounter description
        """
        # Generate description based on region and difficulty
        descriptions = {
            'combat': f"A {difficulty} combat encounter in the {region.name} region.",
            'social': f"A {difficulty} social encounter in the {region.name} region.",
            'exploration': f"A {difficulty} exploration encounter in the {region.name} region.",
            'mystical': f"A {difficulty} mystical encounter in the {region.name} region."
        }
        
        return descriptions.get(self._get_encounter_type(region), "Unknown encounter type")

    def _calculate_rewards(self, level: float, difficulty: str) -> Dict[str, Any]:
        """Calculate rewards for an encounter.
        
        Args:
            level: The average party level
            difficulty: The difficulty level of the encounter
            
        Returns:
            Dict containing reward details
        """
        # Calculate rewards based on level and difficulty
        difficulty_multipliers = {
            'easy': 0.5,
            'normal': 1.0,
            'hard': 1.5,
            'deadly': 2.0
        }
        
        multiplier = difficulty_multipliers.get(difficulty, 1.0)
        base_reward = level * 100
        
        return {
            'gold': int(base_reward * multiplier),
            'experience': int(base_reward * multiplier * 10),
            'items': self._generate_loot(level, difficulty)
        }

    def _get_quest_difficulty(self, region: Region) -> str:
        """Get the appropriate quest difficulty for a region.
        
        Args:
            region: The region to get difficulty for
            
        Returns:
            str: The quest difficulty
        """
        # Determine difficulty based on region properties
        if region.unrest_level > 0.8:
            return 'hard'
        elif region.unrest_level > 0.5:
            return 'normal'
        else:
            return 'easy'

    def _generate_loot(
        self,
        level: float,
        difficulty: str
    ) -> List[Dict[str, Any]]:
        """Generate loot for an encounter.
        
        Args:
            level: The average party level
            difficulty: The difficulty level of the encounter
            
        Returns:
            List of loot items
        """
        # Generate loot based on level and difficulty
        difficulty_multipliers = {
            'easy': 0.5,
            'normal': 1.0,
            'hard': 1.5,
            'deadly': 2.0
        }
        
        multiplier = difficulty_multipliers.get(difficulty, 1.0)
        num_items = int(level * multiplier)
        
        items = []
        for _ in range(num_items):
            items.append({
                'name': f"Item {_ + 1}",
                'value': int(level * 10 * multiplier),
                'rarity': self._get_item_rarity(level, difficulty)
            })
            
        return items

    def _get_item_rarity(self, level: float, difficulty: str) -> str:
        """Get the rarity of an item based on level and difficulty.
        
        Args:
            level: The average party level
            difficulty: The difficulty level of the encounter
            
        Returns:
            str: The item rarity
        """
        # Determine rarity based on level and difficulty
        if level > 15 and difficulty in ['hard', 'deadly']:
            return 'legendary'
        elif level > 10 and difficulty in ['normal', 'hard']:
            return 'rare'
        elif level > 5 and difficulty in ['easy', 'normal']:
            return 'uncommon'
        else:
            return 'common'

def fetch_faction_name(fid):
    faction = db.reference(f"/factions/{fid}").get()
    if not faction:
        return {"id": fid, "name": fid, "description": ""}
    return {
        "id": fid,
        "name": faction.get("name", fid),
        "description": faction.get("description", "")
    }


def gather_dm_context(character_id: str, npc_id: str = None) -> dict:
    """
    Returns a context bundle for GPT-powered DM interaction.
    Uses memoization to avoid redundant Firebase queries within a short TTL window.
    """
    now = datetime.utcnow()
    cache_key = f"{character_id}:{npc_id}"
    
    # === Check for valid cache hit ===
    if cache_key in _context_cache:
        cached = _context_cache[cache_key]
        if now - cached["timestamp"] < _CONTEXT_TTL:
            return cached["data"]

    context = {}

    # === Player motifs ===
    player_motifs = []
    player_data = db.reference(f"/players/{character_id}").get()
    if not player_data:
        player_data = {"region_id": "capital_hub"}  # fallback for new characters

    region_id = player_data.get("region_id", "unknown_region")

    try:
        engine = MotifEngine(character_id)
        for m in engine.get_active_motifs():
            player_motifs.append(f"{m['theme']} (weight {m['weight']})")
    except Exception:
        pass

    # === Region tension ===
    try:
        tension = get_tension(region_id)
    except Exception:
        tension = {"level": 0, "label": "unknown"}

    # === Region arc (optional, last milestone only) ===
    arc = db.reference(f"/regions/{region_id}/arc").get()
    arc_info = {
        "title": arc.get("title") if arc else None,
        "theme": arc.get("theme") if arc else None,
        "latest_milestone": arc.get("milestones", [])[-1] if arc and arc.get("milestones") else None
    }

    # === Chaos check (optional narrative flag) ===
    chaos_log = db.reference("/global_state/world_log").get() or {}
    recent_chaos = [
        e for e in chaos_log.values()
        if e.get("type") == "narrative_chaos" and
           (now.timestamp() - datetime.fromisoformat(e["timestamp"]).timestamp()) < 3600
    ]
    context["recent_chaos_event"] = recent_chaos[-1] if recent_chaos else None

    # === NPC motifs (if applicable) ===
    npc_motifs = []
    if npc_id:
        try:
            engine = MotifEngine(npc_id)
            for m in engine.get_active_motifs():
                npc_motifs.append(f"{m['theme']} (weight {m['weight']})")
        except Exception:
            pass

    # === NPC rumors ===
    rumors = []
    if npc_id:
        rumor_log = db.reference(f"/npc_memory/{npc_id}/rag_log").get() or []
        rumors = [entry.get("interaction") for entry in rumor_log[-3:]]

    # === NPC faction loyalty (summary) ===
    faction_loyalties = []
    if npc_id:
        affiliations = db.reference(f"/npcs/{npc_id}/faction_affiliations").get() or []
        for entry in affiliations:
            if abs(entry.get("loyalty", 0)) >= 2:
                faction = fetch_faction_name(entry["id"])
                faction_loyalties.append({
                    "name": faction["name"],
                    "loyalty": entry["loyalty"]
                })

    # === Memory context between player and NPC ===
    memory = []
    if npc_id:
        memory = get_recent_interactions(npc_id, character_id, limit=3)

    # === Return final context bundle ===
    context.update({
        "player_motifs": player_motifs,
        "npc_motifs": npc_motifs,
        "region_tension": tension,
        "region_arc": arc_info,
        "npc_faction_loyalties": faction_loyalties,
        "recent_memory": memory,
        "npc_rumors": rumors
    })

    # 💾 Cache it
    _context_cache[cache_key] = {"timestamp": now, "data": context}

    return context

def generate_npc_quest_dialogue(npc_name, quest_summary, player_known_status="neutral", show_warning=False):
    """
    Returns GPT-generated dialogue for an NPC who previously posted a quest.
    """

    prompt = f"""You're roleplaying {npc_name}, a fantasy world NPC who recently posted a quest to a town bulletin board.
The player has come to speak to you about the following quest:

'{quest_summary}'

"""

    if show_warning:
        prompt += """You believe the player might not be strong enough for this. You're worried, and your tone should reflect that. 
Speak cautiously, but let them accept the quest if they insist. 
Do NOT mention 'level' or game mechanics. Just narratively imply danger.\n"""
    else:
        prompt += """You're neutral about the player's ability. Just re-explain the quest in your own words and offer it normally.\n"""

    return call(prompt, system_prompt="You are a fantasy NPC talking to a player about a quest you posted.")

def get_tension_flavor_text(region_name):
    score = db.reference(f"/regional_state/{region_name}/tension_score").get() or 0

    if score >= 15:
        return "The region is steeped in fear and chaos. Even simple requests might lead to dangerous consequences."
    elif score >= 10:
        return "Tension runs high in this area. Locals are on edge. Factions are preparing for something."
    elif score >= 5:
        return "There's unease in the air. People speak in whispers and rumors flow freely."
    else:
        return "The region is relatively calm — for now."

def generate_region_narration_context(region_name):
    ref = db.reference(f"/regional_state/{region_name}")
    region = ref.get() or {}
    context_lines = []

    # Tension
    tension = region.get("tension_score", 0)
    if tension >= 15:
        context_lines.append("Tension in the region is critically high. Chaos is imminent.")
    elif tension >= 10:
        context_lines.append("Tension runs high. People are uneasy and rumors spread quickly.")
    elif tension >= 5:
        context_lines.append("The region is restless. Whispers and suspicion are common.")
    else:
        context_lines.append("The region is relatively calm and orderly.")

    # Motifs
    motif_data = region.get("motif_pool", {}).get("active_motifs", [])
    motif_ids = [m.get("theme") for m in motif_data]
    names = [MOTIF_THEME_NAMES.get(mid, f"Unknown({mid})") for mid in motif_ids]
    if names:
        context_lines.append(f"Active regional motifs: {names}")

    return "\n".join(context_lines)


def generate_npc_quest_reminder(npc_id, player_id=None):
    """
    Builds a GPT call where an NPC reminds or re-pitches their posted quest.
    """
    posted = db.reference(f"/npcs/{npc_id}/posted_quests").get() or []
    if not posted:
        return ""

    # Get most recent posted quest
    latest_quest_id = posted[-1]
    quest = None

    # Look in player's questlog to see if it's active
    if player_id:
        log = db.reference(f"/players/{player_id}/questlog").get() or []
        for q in log:
            if q.get("id") == latest_quest_id:
                quest = q
                break

    if not quest:
        # Look up globally
        all_quests = db.reference("/quests/generated").get() or {}
        quest = all_quests.get(latest_quest_id)

    if not quest:
        return ""

    summary = quest.get("summary", "I need help with something...")

    prompt = f"""You are roleplaying {npc_id}, a fantasy NPC who recently posted a quest.
The quest summary is: '{summary}'.

You are talking to the player now. Remind them about the quest and ask if they're still interested.
If they've already taken it, express appreciation or give a brief update or warning.
Keep it in-world. Do not reference game mechanics or levels."""
    
    return call(prompt, system_prompt="You are a fantasy NPC giving quest reminders.")

def generate_dm_response(character: Character, region: Region, quest: Optional[Quest] = None) -> Dict[str, Any]:
    """Generate a DM response based on character, region, and quest context"""
    response = {
        "description": "",
        "options": [],
        "consequences": []
    }
    
    # Generate description based on context
    if quest:
        response["description"] = f"As you continue your quest '{quest.name}', you find yourself in {region.name}..."
    else:
        response["description"] = f"You find yourself in {region.name}..."
    
    # Generate options based on character abilities and region features
    options = []
    if character.has_feat("Stealth"):
        options.append({
            "text": "Attempt to sneak past the guards",
            "difficulty": "Medium",
            "consequence": "Avoid combat"
        })
    
    if character.has_feat("Diplomacy"):
        options.append({
            "text": "Try to negotiate with the guards",
            "difficulty": "Hard",
            "consequence": "Gain information"
        })
    
    response["options"] = options
    
    return response

def apply_dm_decision(character: Character, decision: Dict[str, Any]) -> Dict[str, Any]:
    """Apply the consequences of a DM decision"""
    result = {
        "success": False,
        "effects": [],
        "message": ""
    }
    
    # Apply effects based on decision
    if decision.get("type") == "combat":
        result["message"] = "Combat initiated!"
        result["effects"].append({
            "type": "combat",
            "enemies": decision.get("enemies", [])
        })
    elif decision.get("type") == "skill_check":
        result["message"] = "Skill check required!"
        result["effects"].append({
            "type": "skill_check",
            "skill": decision.get("skill"),
            "difficulty": decision.get("difficulty")
        })
    
    return result
