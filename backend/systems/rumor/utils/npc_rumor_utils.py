#This module simulates NPC-to-NPC rumor propagation, belief evolution, and memory exchange using pure business logic. It's central to organic knowledge distribution and narrative diffusion.
#It connects with npc, memory, belief, world_log, region, and relationship systems.

"""
NPC Rumor Business Logic
Handles rumor propagation, decay, and truth scoring for NPCs using pure business logic.
All database operations have been moved to infrastructure layer.
"""

import random
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple, Protocol
from dataclasses import dataclass

# Import centralized rules configuration
try:
    from backend.systems.rules.rules import get_npc_rumor_behavior, get_rumor_config
    _USE_CENTRALIZED_CONFIG = True
except ImportError:
    _USE_CENTRALIZED_CONFIG = False

# Business domain models
@dataclass
class NPCMemoryEntry:
    """Represents a memory entry for an NPC."""
    interaction: str
    timestamp: str
    credibility: Optional[float] = None

@dataclass
class NPCBelief:
    """Represents an NPC's belief about something."""
    belief_summary: str
    accuracy: str  # "accurate", "partial", "false"
    source: str
    trust_level: int
    heard_at: str
    certainty: Optional[float] = None
    shared_on: Optional[str] = None

@dataclass
class NPCData:
    """Represents basic NPC data."""
    npc_id: str
    region_id: Optional[str] = None
    current_poi: Optional[str] = None
    relationships: Optional[Dict[str, Any]] = None

@dataclass
class RumorPropagationResult:
    """Result of rumor propagation between NPCs."""
    shared_rumors: List[str]
    status: str = "success"

@dataclass
class BeliefPropagationResult:
    """Result of belief propagation in a region."""
    propagations: List[Tuple[str, str, str]]  # (sender_id, receiver_id, belief_summary)

# Business protocols for dependency injection
class NPCDataRepository(Protocol):
    """Protocol for NPC data access."""
    
    def get_memory_log(self, npc_id: str) -> List[NPCMemoryEntry]:
        """Get memory log for an NPC."""
        ...
    
    def set_memory_log(self, npc_id: str, memory_log: List[NPCMemoryEntry]) -> None:
        """Set memory log for an NPC."""
        ...
    
    def get_npc_knowledge(self, npc_id: str, section: Optional[str] = None) -> Dict[str, Any]:
        """Get NPC knowledge data."""
        ...
    
    def set_npc_knowledge(self, npc_id: str, data: Dict[str, Any], section: Optional[str] = None) -> None:
        """Set NPC knowledge data."""
        ...
    
    def get_npc_data(self, npc_id: Optional[str] = None) -> Dict[str, NPCData]:
        """Get NPC data."""
        ...
    
    def get_faction_data(self) -> Dict[str, Any]:
        """Get faction data."""
        ...
    
    def get_opinion_matrix(self, npc_a: str, npc_b: Optional[str] = None) -> Any:
        """Get opinion matrix data."""
        ...
    
    def set_opinion_matrix(self, npc_a: str, data: Any, npc_b: Optional[str] = None) -> None:
        """Set opinion matrix data."""
        ...

# Business service class
class NPCRumorBusinessService:
    """Pure business logic for NPC rumor operations."""
    
    def __init__(self, repository: NPCDataRepository):
        self.repository = repository
    
    def get_behavior_config(self, key: str, default: Any = None) -> Any:
        """Get NPC behavior configuration value."""
        if _USE_CENTRALIZED_CONFIG:
            return get_npc_rumor_behavior(key)
        else:
            # Legacy fallback values
            defaults = {
                "max_rumors_per_npc": 20,
                "trust_threshold_for_sharing": 3,
                "belief_accuracy_trust_scaling": 0.2,
                "rumor_distortion_chance": 0.05,
                "fabrication_chance": 0.01,
                "faction_bias_increment": 1
            }
            return defaults.get(key, default)
    
    def propagate_rumor_between_npcs(self, npc_a_id: str, npc_b_id: str) -> RumorPropagationResult:
        """
        Propagate 1–2 rumors between two NPCs, updating their memory logs.
        Uses centralized configuration for behavior parameters.
        """
        def sample_memories(memories: List[NPCMemoryEntry], count: int = 2) -> List[NPCMemoryEntry]:
            return random.sample(memories, min(len(memories), count))

        shared = []
        a_memory = self.repository.get_memory_log(npc_a_id)
        b_memory = self.repository.get_memory_log(npc_b_id)
        
        a_to_b = sample_memories(a_memory)
        b_to_a = sample_memories(b_memory)
        
        timestamp = datetime.utcnow().isoformat()
        
        # Create new memory entries for B from A's memories
        new_b_entries = [
            NPCMemoryEntry(interaction=m.interaction, timestamp=timestamp)
            for m in a_to_b
        ]
        
        # Create new memory entries for A from B's memories
        new_a_entries = [
            NPCMemoryEntry(interaction=m.interaction, timestamp=timestamp)
            for m in b_to_a
        ]
        
        # Update memory logs
        existing_b = self.repository.get_memory_log(npc_b_id)
        existing_a = self.repository.get_memory_log(npc_a_id)
        
        existing_b_texts = set(m.interaction for m in existing_b)
        existing_a_texts = set(m.interaction for m in existing_a)
        
        for entry in new_b_entries:
            if entry.interaction not in existing_b_texts:
                existing_b.append(entry)
        
        for entry in new_a_entries:
            if entry.interaction not in existing_a_texts:
                existing_a.append(entry)
        
        self.repository.set_memory_log(npc_b_id, existing_b)
        self.repository.set_memory_log(npc_a_id, existing_a)
        
        shared.extend([m.interaction for m in a_to_b])
        shared.extend([m.interaction for m in b_to_a])
        
        return RumorPropagationResult(shared_rumors=shared)
    
    def decay_npc_rumors(self, npc_id: str, max_rumors: Optional[int] = None) -> List[NPCMemoryEntry]:
        """
        Decay and prune rumors for an NPC over time. Remove oldest/least credible rumors.
        Uses centralized configuration for max rumors per NPC.
        """
        if max_rumors is None:
            max_rumors = self.get_behavior_config("max_rumors_per_npc", 20)
        
        rumors = self.repository.get_memory_log(npc_id)
        
        # Remove oldest if more than max_rumors
        if len(rumors) > max_rumors:
            rumors = rumors[-max_rumors:]
        
        # Decay credibility if present
        for rumor in rumors:
            if rumor.credibility is not None:
                rumor.credibility = max(0, rumor.credibility - 1)
        
        self.repository.set_memory_log(npc_id, rumors)
        return rumors
    
    def score_npc_rumor_truth(self, rumor: dict, ground_truth: dict) -> float:
        """
        Score the truth of a rumor using fuzzy logic (direct comparison).
        """
        score = 0.0
        for k, v in rumor.items():
            if k in ground_truth and ground_truth[k] == v:
                score += 1.0
        return score / max(1, len(rumor))
    
    def generate_npc_belief(self, npc_name: str, event_data: Dict[str, Any]) -> NPCBelief:
        """
        Generate a belief summary for an NPC about an event, with accuracy based on trust.
        Uses centralized configuration for trust scaling.
        """
        trust_scaling = self.get_behavior_config("belief_accuracy_trust_scaling", 0.2)
        trust_level = random.randint(1, 5)
        roll = random.random()
        original_summary = event_data.get("summary", "some event happened")
        
        if roll < trust_level / 5:
            accuracy = "accurate"
            belief_summary = original_summary
        elif roll < 0.8:
            accuracy = "partial"
            belief_summary = self._distort_summary(original_summary)
        else:
            accuracy = "false"
            belief_summary = self._fabricate_alternate(event_data)
        
        return NPCBelief(
            belief_summary=belief_summary,
            accuracy=accuracy,
            source="world_log",
            trust_level=trust_level,
            heard_at=event_data.get("poi", "unknown")
        )
    
    def _fabricate_alternate(self, event_data: Dict[str, Any]) -> str:
        """Create a fabricated alternative version of an event."""
        return f"Someone claims {event_data.get('summary', 'something strange')} — but it sounds suspicious."

    def _distort_summary(self, summary: str) -> str:
        """Apply simple distortion to a summary."""
        return summary.replace("was", "may have been").replace("at", "somewhere near")
    
    def propagate_beliefs(self, region_id: str) -> BeliefPropagationResult:
        """
        Propagate beliefs (rumors) among NPCs in a region, based on trust and proximity.
        Uses centralized configuration for trust thresholds.
        """
        trust_threshold = self.get_behavior_config("trust_threshold_for_sharing", 3)
        all_npcs = self.repository.get_npc_data()
        by_poi = {}
        
        for npc_id, npc_data in all_npcs.items():
            if npc_data.region_id != region_id:
                continue
            poi = npc_data.current_poi
            if poi:
                by_poi.setdefault(poi, []).append((npc_id, npc_data))
        
        results = []
        for poi, npc_group in by_poi.items():
            for sender_id, sender_data in npc_group:
                sender_beliefs = self.repository.get_npc_knowledge(sender_id, "beliefs")
                if not sender_beliefs:
                    continue
                belief_key = random.choice(list(sender_beliefs.keys()))
                belief_record = sender_beliefs[belief_key]
                
                for receiver_id, receiver_data in npc_group:
                    if receiver_id == sender_id:
                        continue
                        
                    trust = self.repository.get_opinion_matrix(receiver_id, sender_id)
                    if isinstance(trust, dict):
                        trust = trust.get("trust", 0)
                    
                    if trust < trust_threshold or random.random() > trust / 10:
                        continue
                    
                    # Update receiver's beliefs
                    receiver_beliefs = self.repository.get_npc_knowledge(receiver_id, "beliefs")
                    receiver_beliefs[belief_key] = belief_record
                    self.repository.set_npc_knowledge(receiver_id, receiver_beliefs, "beliefs")
                    
                    results.append((sender_id, receiver_id, belief_record.get("belief_summary", "")))
        
        return BeliefPropagationResult(propagations=results)
    
    def share_between_npcs(self, npc_a: str, npc_b: str, strength_threshold: Optional[int] = None) -> Dict[str, Any]:
        """
        Share knowledge between NPCs based on trust levels.
        Uses centralized configuration for trust thresholds.
        """
        if strength_threshold is None:
            strength_threshold = self.get_behavior_config("trust_threshold_for_sharing", 3)
        
        trust = self.repository.get_opinion_matrix(npc_a, npc_b)
        if trust < strength_threshold:
            return {"status": "too_low_trust", "shared": []}

        a_knowledge = self.repository.get_npc_knowledge(npc_a)
        b_knowledge = self.repository.get_npc_knowledge(npc_b)
        shared = []

        for topic, belief in a_knowledge.items():
            if topic in b_knowledge:
                existing_certainty = b_knowledge[topic].get("certainty", 0.5)
                incoming_certainty = belief.get("certainty", 0.5) * 0.8
                if incoming_certainty <= existing_certainty:
                    continue
            if random.random() < 0.5:
                certainty = belief.get("certainty", round(random.uniform(0.3, 0.9), 2))
                b_knowledge[topic] = {
                    "belief": belief.get("belief"),
                    "source": npc_a,
                    "shared_on": datetime.utcnow().isoformat(),
                    "certainty": round(certainty * 0.8, 2)
                }
                shared.append(topic)

        if shared:
            self.repository.set_npc_knowledge(npc_b, b_knowledge)

        return {"status": "shared", "shared": shared}
    
    def drift_faction_from_rumors(self, npc_id: str, rumor_text: str) -> None:
        """
        If a rumor mentions a known faction, increase bias slightly toward that faction.
        Uses centralized configuration for bias increment amount.
        """
        bias_increment = self.get_behavior_config("faction_bias_increment", 1)
        factions = self.repository.get_faction_data()
        matched = []

        for fid, fdata in factions.items():
            name = fdata.get("name", "").lower()
            if name and name in rumor_text.lower():
                matched.append(fid)

        if not matched:
            return

        data = self.repository.get_opinion_matrix(npc_id, npc_id)
        if not isinstance(data, dict):
            data = {"faction_bias": {}}
        
        for fid in matched:
            if "faction_bias" not in data:
                data["faction_bias"] = {}
            data["faction_bias"][fid] = data["faction_bias"].get(fid, 0) + bias_increment

        self.repository.set_opinion_matrix(npc_id, data, npc_id)
    
    def distort_rumors_if_needed(self) -> List[Dict[str, Any]]:
        """
        Occasionally distort rumors as they spread through the NPC network.
        Uses centralized configuration for distortion chance.
        """
        distortion_chance = self.get_behavior_config("rumor_distortion_chance", 0.05)
        npc_root = self.repository.get_npc_data()
        distortions = []

        for npc_id, npc_data in npc_root.items():
            rumors = self.repository.get_npc_knowledge(npc_id, "rumors")
            if not rumors:
                continue
                
            mutated = False
            new_rumors = []

            for rumor in rumors:
                if isinstance(rumor, dict):
                    text = rumor.get("text")
                else:
                    text = rumor

                if text and random.random() < distortion_chance:
                    # Simple distortion (replace with GPT call in production)
                    new_version = self._distort_summary(text)
                    new_rumors.append(new_version)
                    distortions.append({"npc": npc_id, "original": text, "distorted": new_version})
                    mutated = True
                else:
                    new_rumors.append(text)

            if mutated:
                self.repository.set_npc_knowledge(npc_id, new_rumors, "rumors")

        return distortions
    
    def fabricate_false_rumors(self) -> List[Dict[str, Any]]:
        """
        Occasionally have NPCs fabricate completely false rumors.
        Uses centralized configuration for fabrication chance.
        """
        fabrication_chance = self.get_behavior_config("fabrication_chance", 0.01)
        new_fakes = []

        # This function would need significant adaptation for the actual database structure
        # For now, providing the structure that would work with proper database integration
        
        return new_fakes

# Legacy function wrappers for backward compatibility
def get_behavior_config(key: str, default: Any = None) -> Any:
    """Legacy wrapper for behavior configuration."""
    service = NPCRumorBusinessService(None)  # type: ignore
    return service.get_behavior_config(key, default)

def fabricate_alternate(event_data: Dict[str, Any]) -> str:
    """Legacy wrapper for fabricate alternate."""
    service = NPCRumorBusinessService(None)  # type: ignore
    return service._fabricate_alternate(event_data)

def distort_summary(summary: str) -> str:
    """Legacy wrapper for distort summary."""
    service = NPCRumorBusinessService(None)  # type: ignore
    return service._distort_summary(summary)
