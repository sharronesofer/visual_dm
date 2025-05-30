"""
Core module for DM functionality, providing consolidated services for narrative,
context building, GPT integration, and combat narration.
"""

from firebase_admin import db
from datetime import datetime, timedelta
from functools import lru_cache
import logging
import difflib
from app.memory.memory_utils import get_recent_interactions
from app.motifs.motif_engine_class import MotifEngine
from app.regions.tension_utils import get_tension
from app.utils.gpt_class import GPTClient
from app.npc.npc_relationships_utils import get_relationship_tier

# ===== Constants =====

# Motif theme mapping for narrative context
MOTIF_THEME_NAMES = {
    1: "paranoia", 2: "vengeance", 3: "greed", 4: "honor", 5: "betrayal",
    6: "forgiveness", 7: "redemption", 8: "despair", 9: "loyalty", 10: "loss",
    11: "ambition", 12: "fear", 13: "doubt", 14: "madness", 15: "grief",
    16: "curiosity", 17: "justice", 18: "hope", 19: "peace", 20: "conflict",
    21: "obsession", 22: "shame", 23: "revenge", 24: "sacrifice", 25: "duty",
    26: "resilience", 27: "nostalgia", 28: "melancholy", 29: "conspiracy", 30: "transcendence",
    31: "divine will", 32: "chaos", 33: "restoration", 34: "temptation", 35: "survival",
    36: "decay", 37: "awakening", 38: "regret", 39: "discipline", 40: "freedom",
    41: "tradition", 42: "innovation", 43: "identity", 44: "reckoning", 45: "fate",
    46: "entropy", 47: "repression", 48: "miracles", 49: "isolation", 50: "secrets"
}

# ===== Context Management =====

# Context cache with TTL for efficiency
_context_cache = {}
_CONTEXT_TTL = timedelta(seconds=30)  # Cache for 30 seconds

def gather_dm_context(character_id: str, npc_id: str = None) -> dict:
    """
    Returns a context bundle for GPT-powered DM interaction.
    Uses memoization to avoid redundant Firebase queries within a short TTL window.
    """
    now = datetime.utcnow()
    cache_key = f"{character_id}:{npc_id}"
    
    # Check for valid cache hit
    if cache_key in _context_cache:
        cached = _context_cache[cache_key]
        if now - cached["timestamp"] < _CONTEXT_TTL:
            return cached["data"]

    context = {}

    # Player motifs
    player_motifs = []
    player_data = db.reference(f"/players/{character_id}").get()
    if not player_data:
        player_data = {"region_id": "capital_hub"}  # fallback for new characters

    region_id = player_data.get("region_id", "unknown_region")

    try:
        engine = MotifEngine(character_id)
        for m in engine.get_active_motifs():
            player_motifs.append(f"{m['theme']} (weight {m['weight']})")
    except Exception as e:
        logging.error(f"Error fetching player motifs: {str(e)}")

    # Region tension
    try:
        tension = get_tension(region_id)
    except Exception as e:
        logging.error(f"Error fetching region tension: {str(e)}")
        tension = {"level": 0, "label": "unknown"}

    # Region arc (optional, last milestone only)
    arc = db.reference(f"/regions/{region_id}/arc").get()
    arc_info = {
        "title": arc.get("title") if arc else None,
        "theme": arc.get("theme") if arc else None,
        "latest_milestone": arc.get("milestones", [])[-1] if arc and arc.get("milestones") else None
    }

    # Chaos check (optional narrative flag)
    chaos_log = db.reference("/global_state/world_log").get() or {}
    recent_chaos = [
        e for e in chaos_log.values()
        if e.get("type") == "narrative_chaos" and
           (now.timestamp() - datetime.fromisoformat(e["timestamp"]).timestamp()) < 3600
    ]
    context["recent_chaos_event"] = recent_chaos[-1] if recent_chaos else None

    # NPC-specific context
    npc_motifs = []
    rumors = []
    faction_loyalties = []
    memory = []
    
    if npc_id:
        # NPC motifs
        try:
            engine = MotifEngine(npc_id)
            for m in engine.get_active_motifs():
                npc_motifs.append(f"{m['theme']} (weight {m['weight']})")
        except Exception as e:
            logging.error(f"Error fetching NPC motifs: {str(e)}")

        # NPC rumors
        rumor_log = db.reference(f"/npc_memory/{npc_id}/rag_log").get() or []
        rumors = [entry.get("interaction") for entry in rumor_log[-3:]]

        # NPC faction loyalty (summary)
        affiliations = db.reference(f"/npcs/{npc_id}/faction_affiliations").get() or []
        for entry in affiliations:
            if abs(entry.get("loyalty", 0)) >= 2:
                faction = fetch_faction_name(entry["id"])
                faction_loyalties.append({
                    "name": faction["name"],
                    "loyalty": entry["loyalty"]
                })

        # Memory context between player and NPC
        memory = get_recent_interactions(npc_id, character_id, limit=3)
        
        # Relationship context
        relationship = gather_relationship_context(npc_id, character_id)
        if relationship:
            context["relationship"] = relationship
            
        # Faction context
        faction_context = gather_faction_context(npc_id, character_id)
        if faction_context:
            context["faction_context"] = faction_context

    # Return final context bundle
    context.update({
        "player_motifs": player_motifs,
        "npc_motifs": npc_motifs,
        "region_tension": tension,
        "region_arc": arc_info,
        "npc_faction_loyalties": faction_loyalties,
        "recent_memory": memory,
        "npc_rumors": rumors
    })

    # Cache it
    _context_cache[cache_key] = {"timestamp": now, "data": context}

    return context

def fetch_faction_name(fid):
    """Get faction data from Firebase"""
    faction = db.reference(f"/factions/{fid}").get()
    if not faction:
        return {"id": fid, "name": fid, "description": ""}
    return {
        "id": fid,
        "name": faction.get("name", fid),
        "description": faction.get("description", "")
    }

def generate_region_narration_context(region_name):
    """Generate narrative context for a region based on tension and motifs"""
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

def get_tension_flavor_text(region_name):
    """Get flavor text based on a region's tension level"""
    score = db.reference(f"/regional_state/{region_name}/tension_score").get() or 0

    if score >= 15:
        return "The region is steeped in fear and chaos. Even simple requests might lead to dangerous consequences."
    elif score >= 10:
        return "Tension runs high in this area. Locals are on edge. Factions are preparing for something."
    elif score >= 5:
        return "There's unease in the air. People speak in whispers and rumors flow freely."
    else:
        return "The region is relatively calm — for now."

# ===== NPC & Character Services =====

def resolve_names(input_text, npc_list, alias_map=None, relationship_map=None):
    """Resolve NPC names from user input, handling aliases and fuzzy matching"""
    input_text = input_text.strip().lower()

    if alias_map and input_text in alias_map:
        npc_id = alias_map[input_text]
        match = next((n for n in npc_list if n['id'] == npc_id), None)
        if match:
            return {'resolved_name': match['name'], 'npc_id': npc_id, 'match_type': 'alias'}

    if relationship_map and input_text in relationship_map:
        npc_id = relationship_map[input_text]
        match = next((n for n in npc_list if n['id'] == npc_id), None)
        if match:
            return {'resolved_name': match['name'], 'npc_id': npc_id, 'match_type': 'relationship'}

    names = [n['name'].lower() for n in npc_list]
    match = difflib.get_close_matches(input_text, names, n=1, cutoff=0.6)
    if match:
        resolved = next(n for n in npc_list if n['name'].lower() == match[0])
        return {'resolved_name': resolved['name'], 'npc_id': resolved['id'], 'match_type': 'fuzzy'}

    return {'resolved_name': input_text, 'npc_id': None, 'match_type': 'unknown'}

def gather_relationship_context(npc_id, pc_id):
    """Get relationship context between NPC and PC"""
    try:
        tier = get_relationship_tier(npc_id, pc_id)
        return f"{npc_id} considers the player a {tier}."
    except Exception as e:
        logging.error(f"Error fetching relationship context: {str(e)}")
        return ""
    
def gather_faction_context(npc_id, pc_id):
    """Get faction relationships between NPC and PC"""
    try:
        npc_factions = db.reference(f"/npcs/{npc_id}/faction_opinions").get() or {}
        pc_factions = db.reference(f"/pcs/{pc_id}/faction_affiliations").get() or []

        hostile_factions = [
            f for f in pc_factions if npc_factions.get(f, 0) <= -10
        ]

        if hostile_factions:
            return f"{npc_id} harbors hostility toward factions: {hostile_factions}."
        return ""
    except Exception as e:
        logging.error(f"Error fetching faction context: {str(e)}")
        return ""

# ===== Dialogue Generation =====

def generate_npc_quest_dialogue(npc_name, quest_summary, player_known_status="neutral", show_warning=False):
    """
    Returns GPT-generated dialogue for an NPC who previously posted a quest.
    """
    gpt_client = GPTClient()
    
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

    return gpt_client.call(
        user_prompt=prompt,
        system_prompt="You are a fantasy NPC talking to a player about a quest you posted.",
        max_tokens=150
    )

def generate_npc_quest_reminder(npc_id, player_id=None):
    """
    Builds a GPT call where an NPC reminds or re-pitches their posted quest.
    """
    gpt_client = GPTClient()
    
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
    
    return gpt_client.call(
        user_prompt=prompt,
        system_prompt="You are a fantasy NPC giving quest reminders.",
        max_tokens=150
    )

# ===== Request Classification =====

def classify_request(prompt: str, character_id: str = None) -> str:
    """
    Classifies user prompt into 'mechanical', 'npc', or 'narrative'.
    Logs result for future refinement or RLHF-style correction.
    """
    prompt_lower = prompt.lower()

    if any(word in prompt_lower for word in ["roll", "hit", "attack", "damage", "ac", "initiative"]):
        classification = "mechanical"
    elif any(word in prompt_lower for word in ["say", "ask", "tell", "respond", "talk"]):
        classification = "npc"
    else:
        classification = "narrative"

    # Log to Firebase if character_id is provided
    if character_id:
        log_ref = db.reference(f"/classification_log/{character_id}")
        log_ref.push({
            "timestamp": datetime.utcnow().isoformat(),
            "prompt": prompt,
            "classification": classification,
            "override": None  # Placeholder for feedback later
        })

    return classification

# ===== Combat Narration =====

def narrate_combat_action(actor_name, action_data, outcome):
    """
    Converts a tactical combat action into flavorful prose.
    """
    gpt_client = GPTClient()
    
    prompt = (
        f"{actor_name} used {action_data.get('ability', 'an action')} on {action_data.get('target')}.\n"
        f"The attack {'hit' if outcome.get('hit') else 'missed'} and dealt {outcome.get('damage', 0)} "
        f"{outcome.get('damage_type', 'damage')}.\n"
        f"Target HP after the attack: {outcome.get('target_hp')}.\n\n"
        "Write a vivid, 2–4 sentence cinematic description of this moment."
    )

    return gpt_client.call(
        user_prompt=prompt,
        system_prompt="You are a fantasy combat narrator describing vivid battle scenes.",
        temperature=0.9,
        max_tokens=150
    )

# ===== New DM Core Functionality =====

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from backend.systems.dm.event_integration import EventDispatcher
from backend.systems.dm.memory_system import MemorySystem, Memory
from backend.systems.dm.rumor_system import RumorSystem, Rumor
from backend.systems.dm.motif_system import MotifSystem, Motif
from backend.systems.dm.faction_system import FactionSystem, Faction

logger = logging.getLogger(__name__)

class DungeonMaster:
    """
    Main DM class that orchestrates the narrative generation and world management.
    
    This is the primary interface for the DM system, providing methods to generate
    content, manage world state, and interact with all subsystems.
    """
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """Get the singleton instance of the DungeonMaster."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """Initialize the DungeonMaster."""
        if DungeonMaster._instance is not None:
            raise Exception("This class is a singleton. Use get_instance() instead.")
        
        DungeonMaster._instance = self
        
        # Initialize core systems
        self.event_dispatcher = EventDispatcher.get_instance()
        self.memory_system = MemorySystem.get_instance()
        self.rumor_system = RumorSystem.get_instance()
        self.motif_system = MotifSystem.get_instance()
        self.faction_system = FactionSystem.get_instance()
        
        # Register event handlers
        self._register_event_handlers()
        
        logger.info("DungeonMaster initialized")
    
    def _register_event_handlers(self):
        """Register event handlers for cross-system integration."""
        # Memory-related events
        self.event_dispatcher.subscribe("memory.created", self._on_memory_created)
        self.event_dispatcher.subscribe("memory.reinforced", self._on_memory_reinforced)
        
        # Rumor-related events
        self.event_dispatcher.subscribe("rumor.created", self._on_rumor_created)
        self.event_dispatcher.subscribe("rumor.spread", self._on_rumor_spread)
        
        # Motif-related events
        self.event_dispatcher.subscribe("motif.created", self._on_motif_created)
        self.event_dispatcher.subscribe("motif.occurrence", self._on_motif_occurrence)
        
        # Faction-related events
        self.event_dispatcher.subscribe("faction.relationship_changed", self._on_faction_relationship_changed)
    
    # ===== Memory System Integration =====
    
    def create_memory(self, entity_id: str, content: str, importance: float = 0.5,
                     is_core: bool = False, tags: List[str] = None,
                     associated_entities: List[str] = None,
                     metadata: Dict[str, Any] = None) -> Memory:
        """
        Create a new memory for an entity.
        
        Args:
            entity_id: ID of the entity who has this memory
            content: Text content of the memory
            importance: How important this memory is (0.0 to 1.0)
            is_core: Whether this is a core/defining memory
            tags: List of tags for categorizing the memory
            associated_entities: IDs of other entities involved
            metadata: Additional data for the memory
            
        Returns:
            The created Memory object
        """
        return self.memory_system.create_memory(
            entity_id=entity_id,
            content=content,
            importance=importance,
            is_core=is_core,
            tags=tags,
            associated_entities=associated_entities,
            metadata=metadata
        )
    
    def reinforce_memory(self, memory_id: str, reinforcement_strength: float = 0.5) -> float:
        """
        Reinforce an existing memory to make it stronger.
        
        Args:
            memory_id: ID of the memory to reinforce
            reinforcement_strength: Strength of reinforcement (0.0 to 1.0)
            
        Returns:
            New relevance score
        """
        return self.memory_system.reinforce_memory(
            memory_id=memory_id,
            reinforcement_strength=reinforcement_strength
        )
    
    def get_memories(self, entity_id: str, query: str = None, min_relevance: float = 0.0,
                    limit: int = 10, include_expired: bool = False,
                    tags: List[str] = None) -> List[Dict[str, Any]]:
        """
        Get memories for an entity, optionally filtered.
        
        Args:
            entity_id: ID of the entity
            query: Optional search query
            min_relevance: Minimum relevance score
            limit: Maximum number of memories to return
            include_expired: Whether to include expired memories
            tags: Optional list of tags to filter by
            
        Returns:
            List of memory objects
        """
        return self.memory_system.get_memories(
            entity_id=entity_id,
            query=query,
            min_relevance=min_relevance,
            limit=limit,
            include_expired=include_expired,
            tags=tags
        )
    
    def get_memory_context(self, entity_id: str, query: str = None, 
                          limit: int = 5) -> str:
        """
        Get a narrative context string from memories.
        
        Args:
            entity_id: ID of the entity
            query: Optional search query to find relevant memories
            limit: Maximum number of memories to include
            
        Returns:
            Formatted string of memory context
        """
        return self.memory_system.get_memory_context(
            entity_id=entity_id,
            query=query,
            limit=limit
        )
    
    # ===== Rumor System Integration =====
    
    def create_rumor(self, content: str, rumor_type: str, source_entity_id: str,
                    truth_value: float = 1.0, severity: int = 1,
                    region_id: Optional[str] = None, tags: List[str] = None,
                    metadata: Dict[str, Any] = None) -> Rumor:
        """
        Create a new rumor.
        
        Args:
            content: The rumor content
            rumor_type: Type of rumor
            source_entity_id: ID of the entity creating the rumor
            truth_value: How true the rumor is (0.0 to 1.0)
            severity: How severe/important the rumor is (1 to 5)
            region_id: Optional region ID
            tags: Optional tags for the rumor
            metadata: Optional metadata for the rumor
            
        Returns:
            The created Rumor object
        """
        return self.rumor_system.create_rumor(
            content=content,
            rumor_type=rumor_type,
            source_entity_id=source_entity_id,
            truth_value=truth_value,
            severity=severity,
            region_id=region_id,
            tags=tags,
            metadata=metadata
        )
    
    def spread_rumor(self, rumor_id: str, source_entity_id: str,
                    target_entity_ids: List[str], apply_mutation: bool = True) -> Dict[str, Any]:
        """
        Spread a rumor to one or more entities.
        
        Args:
            rumor_id: The ID of the rumor
            source_entity_id: ID of the entity spreading the rumor
            target_entity_ids: IDs of the entities receiving the rumor
            apply_mutation: Whether to apply mutation
            
        Returns:
            Dict of target_entity_id -> RumorSpread
        """
        return self.rumor_system.spread_rumor(
            rumor_id=rumor_id,
            source_entity_id=source_entity_id,
            target_entity_ids=target_entity_ids,
            apply_mutation=apply_mutation
        )
    
    def get_entity_rumors(self, entity_id: str, include_expired: bool = False) -> List[Dict[str, Any]]:
        """
        Get all rumors known to an entity.
        
        Args:
            entity_id: The ID of the entity
            include_expired: Whether to include expired rumors
            
        Returns:
            List of rumor details, including spread info
        """
        return self.rumor_system.get_entity_rumors(
            entity_id=entity_id,
            include_expired=include_expired
        )
    
    def get_regional_rumors(self, region_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the most believed rumors in a region.
        
        Args:
            region_id: The ID of the region
            limit: Maximum number of rumors to return
            
        Returns:
            List of rumor details with aggregate believability
        """
        return self.rumor_system.get_regional_rumors(
            region_id=region_id,
            limit=limit
        )
    
    def get_rumor_context(self, entity_id: str = None, region_id: str = None,
                         max_rumors: int = 5) -> str:
        """
        Generate narrative context for rumors, either for an entity or a region.
        
        Args:
            entity_id: The ID of the entity (optional)
            region_id: The ID of the region (optional)
            max_rumors: Maximum number of rumors to include
            
        Returns:
            String of rumor context for narrative
        """
        return self.rumor_system.get_rumor_context(
            entity_id=entity_id,
            region_id=region_id,
            max_rumors=max_rumors
        )
    
    # ===== Motif System Integration =====
    
    def create_motif(self, name: str, description: str, category: str,
                    intensity: float = 1.0, associated_emotions: List[str] = None,
                    narrative_patterns: List[str] = None, tags: List[str] = None,
                    opposing_motifs: List[str] = None, complementary_motifs: List[str] = None,
                    metadata: Dict[str, Any] = None) -> Motif:
        """
        Create a new motif.
        
        Args:
            name: Unique name for the motif
            description: Description of what this motif represents
            category: Category of the motif
            intensity: Base intensity (0.1 to 2.0)
            associated_emotions: List of emotions associated with this motif
            narrative_patterns: Example narrative expressions of this motif
            tags: Search tags for the motif
            opposing_motifs: IDs of motifs that oppose this one
            complementary_motifs: IDs of motifs that strengthen this one
            metadata: Additional data for the motif
            
        Returns:
            The created Motif object
        """
        return self.motif_system.create_motif(
            name=name,
            description=description,
            category=category,
            intensity=intensity,
            associated_emotions=associated_emotions,
            narrative_patterns=narrative_patterns,
            tags=tags,
            opposing_motifs=opposing_motifs,
            complementary_motifs=complementary_motifs,
            metadata=metadata
        )
    
    def record_motif_occurrence(self, motif_id: str, narrative_text: str,
                              entity_id: Optional[str] = None, region_id: Optional[str] = None,
                              event_id: Optional[str] = None, strength: float = 1.0):
        """
        Record an occurrence of a motif.
        
        Args:
            motif_id: ID of the motif
            narrative_text: Text description of how the motif appears in narrative
            entity_id: Optional entity associated with this occurrence
            region_id: Optional region associated with this occurrence
            event_id: Optional event ID associated with this occurrence
            strength: Strength of this occurrence (0.0 to 2.0)
            
        Returns:
            The created MotifOccurrence object
        """
        return self.motif_system.record_occurrence(
            motif_id=motif_id,
            narrative_text=narrative_text,
            entity_id=entity_id,
            region_id=region_id,
            event_id=event_id,
            strength=strength
        )
    
    def suggest_motifs_for_context(self, entity_id: Optional[str] = None, 
                                 region_id: Optional[str] = None,
                                 limit: int = 3) -> List[Dict[str, Any]]:
        """
        Suggest motifs appropriate for a narrative context.
        
        Args:
            entity_id: Optional entity ID for context
            region_id: Optional region ID for context
            limit: Maximum number of suggestions
            
        Returns:
            List of suggested motifs with narrative patterns
        """
        return self.motif_system.suggest_motifs_for_context(
            entity_id=entity_id,
            region_id=region_id,
            limit=limit
        )
    
    def get_motif_narrative_context(self, entity_id: Optional[str] = None,
                                  region_id: Optional[str] = None,
                                  max_motifs: int = 3) -> str:
        """
        Generate narrative context describing motifs for an entity or region.
        
        Args:
            entity_id: Optional entity ID
            region_id: Optional region ID
            max_motifs: Maximum motifs to include
            
        Returns:
            String of narrative context
        """
        return self.motif_system.get_motif_narrative_context(
            entity_id=entity_id,
            region_id=region_id,
            max_motifs=max_motifs
        )
    
    # ===== Faction System Integration =====
    
    def create_faction(self, name: str, description: str, faction_type: str,
                      power_level: int = 5, secrecy: int = 1, stability: float = 0.5,
                      territory: List[str] = None, leadership: List[Dict[str, Any]] = None,
                      colors: List[str] = None, symbol: Optional[str] = None,
                      values: List[str] = None, tags: List[str] = None,
                      metadata: Dict[str, Any] = None) -> Faction:
        """
        Create a new faction.
        
        Args:
            name: Unique name for the faction
            description: Description of the faction
            faction_type: Type of faction
            power_level: Power level (1 to 10)
            secrecy: How secretive the faction is (1 to 10)
            stability: How stable the faction is (0.0 to 1.0)
            territory: List of region IDs where the faction has presence
            leadership: Key leaders/members of the faction
            colors: Symbolic colors of the faction
            symbol: Description of faction symbol/crest
            values: Core values/principles of the faction
            tags: Search tags for the faction
            metadata: Additional data for the faction
            
        Returns:
            The created Faction object
        """
        return self.faction_system.create_faction(
            name=name,
            description=description,
            faction_type=faction_type,
            power_level=power_level,
            secrecy=secrecy,
            stability=stability,
            territory=territory,
            leadership=leadership,
            colors=colors,
            symbol=symbol,
            values=values,
            tags=tags,
            metadata=metadata
        )
    
    def set_faction_relationship(self, faction_id: str, target_faction_id: str,
                               reputation: float, influence: float = None,
                               is_public: bool = True):
        """
        Set or update the relationship between two factions.
        
        Args:
            faction_id: ID of the source faction
            target_faction_id: ID of the target faction
            reputation: How the source views the target (-1.0 to 1.0)
            influence: How much influence source has over target (0.0 to 1.0)
            is_public: Whether this relationship is publicly known
            
        Returns:
            The created/updated FactionRelationship object
        """
        return self.faction_system.set_relationship(
            faction_id=faction_id,
            target_faction_id=target_faction_id,
            reputation=reputation,
            influence=influence,
            is_public=is_public
        )
    
    def get_faction_conflicts(self) -> List[Dict[str, Any]]:
        """
        Identify active conflicts between factions.
        
        Returns:
            List of faction conflicts with details
        """
        return self.faction_system.get_faction_conflicts()
    
    def get_faction_narrative_context(self, faction_id: str = None, region_id: str = None,
                                    include_hidden: bool = False,
                                    max_factions: int = 3) -> str:
        """
        Generate narrative context for factions, either for a specific faction or region.
        
        Args:
            faction_id: Optional faction ID to focus on
            region_id: Optional region ID to focus on
            include_hidden: Whether to include hidden details
            max_factions: Maximum number of factions to include
            
        Returns:
            String of faction narrative context
        """
        return self.faction_system.get_faction_narrative_context(
            faction_id=faction_id,
            region_id=region_id,
            include_hidden=include_hidden,
            max_factions=max_factions
        )
    
    # ===== Integrated Narrative Context =====
    
    def get_full_narrative_context(self, entity_id: Optional[str] = None,
                                 region_id: Optional[str] = None,
                                 include_hidden: bool = False) -> str:
        """
        Generate a comprehensive narrative context combining all relevant systems.
        
        Args:
            entity_id: Optional entity ID to focus on
            region_id: Optional region ID to focus on
            include_hidden: Whether to include hidden information
            
        Returns:
            Comprehensive narrative context string
        """
        context_parts = []
        
        # Add memory context for entity
        if entity_id:
            memory_context = self.memory_system.get_memory_context(entity_id)
            if memory_context:
                context_parts.append("## Memory Context")
                context_parts.append(memory_context)
        
        # Add rumor context
        rumor_context = self.rumor_system.get_rumor_context(entity_id, region_id)
        if rumor_context:
            context_parts.append("## Rumor Context")
            context_parts.append(rumor_context)
        
        # Add motif context
        motif_context = self.motif_system.get_motif_narrative_context(entity_id, region_id)
        if motif_context:
            context_parts.append("## Thematic Context")
            context_parts.append(motif_context)
        
        # Add faction context
        faction_context = self.faction_system.get_faction_narrative_context(
            faction_id=None,  # We're focusing on region/entity
            region_id=region_id,
            include_hidden=include_hidden
        )
        if faction_context:
            context_parts.append("## Political Context")
            context_parts.append(faction_context)
        
        # Combine all contexts
        if context_parts:
            return "\n\n".join(context_parts)
        else:
            return "No contextual information available."
    
    # ===== Event Handlers =====
    
    def _on_memory_created(self, event):
        """Handler for memory.created events."""
        logger.debug(f"Memory created: {event.memory_id}")
        # Future: Could trigger motif detection based on memory content
    
    def _on_memory_reinforced(self, event):
        """Handler for memory.reinforced events."""
        logger.debug(f"Memory reinforced: {event.memory_id}")
        # Future: Could affect related systems when important memories are reinforced
    
    def _on_rumor_created(self, event):
        """Handler for rumor.created events."""
        logger.debug(f"Rumor created: {event.rumor_id}")
        # Future: Could create memories for the source entity about creating the rumor
    
    def _on_rumor_spread(self, event):
        """Handler for rumor.spread events."""
        logger.debug(f"Rumor spread: {event.rumor_id} to {len(event.target_entity_ids)} entities")
        # Create memories for entities that received the rumor
        for target_id in event.target_entity_ids:
            rumor_data = event.rumor_data
            source_id = event.source_entity_id
            
            # Create memory of hearing the rumor
            try:
                self.memory_system.create_memory(
                    entity_id=target_id,
                    content=f"Heard from {source_id} that {rumor_data['content']}",
                    importance=min(1.0, rumor_data.get('severity', 1) * 0.2),
                    tags=["rumor", rumor_data.get('rumor_type', 'unknown')],
                    associated_entities=[source_id],
                    metadata={"rumor_id": event.rumor_id, "mutated": event.mutated}
                )
            except Exception as e:
                logger.error(f"Error creating memory for rumor: {e}")
    
    def _on_motif_created(self, event):
        """Handler for motif.created events."""
        logger.debug(f"Motif created: {event.motif_id} - {event.motif_name}")
        # Future: Could trigger related motifs to be created or opposing motifs
    
    def _on_motif_occurrence(self, event):
        """Handler for motif.occurrence events."""
        logger.debug(f"Motif occurrence: {event.motif_id} - {event.motif_name}")
        # Future: Could influence faction goals or rumors related to the motif
    
    def _on_faction_relationship_changed(self, event):
        """Handler for faction.relationship_changed events."""
        logger.debug(f"Faction relationship changed: {event.faction_id} -> {event.target_faction_id}")
        
        # If it's a significant change and public, create rumors
        if event.is_public and abs(event.reputation) > 0.7:
            try:
                faction = self.faction_system.get_faction(event.faction_id)
                target = self.faction_system.get_faction(event.target_faction_id)
                
                if not faction or not target:
                    return
                
                # Determine rumor type based on relationship
                if event.reputation > 0:
                    rumor_type = "political"
                    content = f"The {faction.name} and {target.name} have formed a strong alliance."
                else:
                    rumor_type = "conflict"
                    content = f"The {faction.name} and {target.name} are now in open conflict."
                
                # Create the rumor
                rumor = self.rumor_system.create_rumor(
                    content=content,
                    rumor_type=rumor_type,
                    source_entity_id="system",  # System-generated rumor
                    truth_value=1.0,  # It's true
                    severity=min(5, int(abs(event.reputation) * 5)),
                    tags=["faction", "relationship"],
                    metadata={
                        "faction_id": event.faction_id,
                        "target_faction_id": event.target_faction_id,
                        "reputation": event.reputation
                    }
                )
                
                logger.debug(f"Created rumor about faction relationship: {rumor.id}")
            except Exception as e:
                logger.error(f"Error creating rumor for faction relationship: {e}")


# Initialize the DM
dm = DungeonMaster.get_instance() 