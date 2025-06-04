"""
Player Character Motif Service

This service manages motifs that follow specific player characters,
tracking their narrative themes and how they influence NPC interactions.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import logging
import random

from backend.infrastructure.systems.motif.models import (
    Motif, MotifCreate, MotifUpdate, MotifFilter,
    MotifScope, MotifLifecycle, MotifCategory, MotifEffect,
    LocationInfo, PlayerCharacterMotif
)
from backend.infrastructure.systems.motif.repositories import MotifRepository

# Import configuration system
from backend.infrastructure.config.motif_config_loader import config

logger = logging.getLogger(__name__)

class PlayerCharacterMotifService:
    """Service for managing Player Character specific motifs."""
    
    def __init__(self, repository: MotifRepository = None):
        """Initialize the service with a repository."""
        self.repository = repository or MotifRepository()
    
    async def create_pc_motif(
        self, 
        player_id: str, 
        motif_data: MotifCreate,
        source_event: str = None,
        influence_range: float = 100.0,
        visibility: str = "hidden"
    ) -> PlayerCharacterMotif:
        """
        Create a new Player Character motif.
        
        Args:
            player_id: The player this motif is attached to
            motif_data: Base motif creation data
            source_event: Description of what event created this motif
            influence_range: How far this motif affects NPCs (in game units)
            visibility: How apparent this motif is to NPCs ("hidden", "subtle", "obvious")
        """
        # Ensure the motif is PC-scoped
        motif_data.scope = MotifScope.PLAYER_CHARACTER
        
        # Set up location info to follow the player
        motif_data.location = LocationInfo(
            player_id=player_id,
            follows_player=True,
            radius=influence_range
        )
        
        # Add source event tracking
        motif_data.source_event = source_event
        motif_data.influence_radius = influence_range
        
        # Create the base motif
        motif = Motif(**motif_data.dict())
        motif.created_at = datetime.utcnow()
        motif.updated_at = motif.created_at
        
        # Add PC-specific evolution rules
        self._add_default_pc_evolution_rules(motif)
        
        # Create PC motif wrapper
        pc_motif = PlayerCharacterMotif(
            player_id=player_id,
            motif=motif,
            acquisition_event=source_event,
            influence_range=influence_range,
            visibility=visibility
        )
        
        # Store in repository
        await self.repository.create_motif(motif)
        
        logger.info(f"Created PC motif '{motif.name}' for player {player_id}")
        return pc_motif
    
    async def get_player_motifs(self, player_id: str) -> List[PlayerCharacterMotif]:
        """Get all motifs associated with a specific player."""
        motifs = await self.repository.get_player_motifs(player_id)
        
        pc_motifs = []
        for motif in motifs:
            # Reconstruct PC motif wrapper
            pc_motif = PlayerCharacterMotif(
                player_id=player_id,
                motif=motif,
                acquisition_event=motif.source_event,
                influence_range=motif.influence_radius,
                visibility=motif.metadata.get("visibility", "hidden")
            )
            pc_motifs.append(pc_motif)
        
        return pc_motifs
    
    async def update_player_location(self, player_id: str, x: float, y: float):
        """Update the location of all PC motifs when a player moves."""
        player_motifs = await self.get_player_motifs(player_id)
        
        for pc_motif in player_motifs:
            if pc_motif.motif.location and pc_motif.motif.location.follows_player:
                # Update motif location to follow player
                pc_motif.motif.location.x = x
                pc_motif.motif.location.y = y
                pc_motif.motif.updated_at = datetime.utcnow()
                
                await self.repository.update_motif(
                    pc_motif.motif.id, 
                    {"location": pc_motif.motif.location.dict()}
                )
    
    async def trigger_pc_motif_from_action(
        self, 
        player_id: str, 
        action_type: str, 
        action_context: Dict[str, Any],
        x: float, 
        y: float
    ) -> Optional[PlayerCharacterMotif]:
        """
        Create or modify PC motifs based on player actions.
        
        Args:
            player_id: Player performing the action
            action_type: Type of action ("heroic_deed", "betrayal", "sacrifice", etc.)
            action_context: Details about the action
            x, y: Location where action occurred
        """
        # Determine motif category based on action type using configuration
        category_mapping = config.get_action_motif_mapping()
        category_str = category_mapping.get(action_type, "ECHO")
        
        # Convert string to enum if needed
        try:
            category = getattr(MotifCategory, category_str) if hasattr(MotifCategory, category_str) else MotifCategory.ECHO
        except AttributeError:
            logger.warning(f"Unknown motif category '{category_str}' for action '{action_type}', using ECHO")
            category = MotifCategory.ECHO
        
        # Check if player already has a similar motif
        existing_motifs = await self.get_player_motifs(player_id)
        similar_motif = None
        
        for pc_motif in existing_motifs:
            if pc_motif.motif.category == category:
                similar_motif = pc_motif
                break
        
        if similar_motif:
            # Reinforce existing motif
            return await self._reinforce_pc_motif(similar_motif, action_context)
        else:
            # Create new motif
            return await self._create_action_motif(
                player_id, category, action_type, action_context, x, y
            )
    
    async def get_pc_motif_context_for_npc(
        self, 
        npc_location: Dict[str, float], 
        player_id: str
    ) -> Dict[str, Any]:
        """
        Get PC motif context that should influence an NPC at a specific location.
        
        Args:
            npc_location: NPC's current location {"x": float, "y": float}
            player_id: Player whose motifs to check
            
        Returns:
            Context dictionary for AI/narrative systems
        """
        player_motifs = await self.get_player_motifs(player_id)
        
        # Filter motifs that are close enough to influence this NPC
        influencing_motifs = []
        npc_x, npc_y = npc_location["x"], npc_location["y"]
        
        for pc_motif in player_motifs:
            if not pc_motif.motif.location:
                continue
                
            # Calculate distance between NPC and motif center
            motif_x = pc_motif.motif.location.x or 0
            motif_y = pc_motif.motif.location.y or 0
            distance = ((npc_x - motif_x) ** 2 + (npc_y - motif_y) ** 2) ** 0.5
            
            # Check if NPC is within influence range
            if distance <= pc_motif.influence_range:
                influencing_motifs.append(pc_motif)
        
        if not influencing_motifs:
            return {"has_pc_motifs": False}
        
        # Generate context based on influencing motifs
        context = {
            "has_pc_motifs": True,
            "motif_count": len(influencing_motifs),
            "primary_pc_theme": influencing_motifs[0].motif.category.value,
            "pc_reputation_elements": [],
            "npc_reaction_guidance": "",
            "motif_details": []
        }
        
        for pc_motif in influencing_motifs:
            motif = pc_motif.motif
            context["pc_reputation_elements"].append(motif.category.value)
            context["motif_details"].append({
                "name": motif.name,
                "category": motif.category.value,
                "intensity": motif.get_effective_intensity(),
                "visibility": pc_motif.visibility,
                "description": motif.description
            })
        
        # Generate NPC reaction guidance
        context["npc_reaction_guidance"] = self._generate_npc_reaction_guidance(
            influencing_motifs
        )
        
        return context
    
    def _add_default_pc_evolution_rules(self, motif: Motif):
        """Add default evolution rules for PC motifs."""
        
        # Rule: Motifs get stronger when reinforced by similar actions
        reinforcement_rule = MotifEvolutionRule(
            trigger_type=MotifEvolutionTrigger.REINFORCEMENT,
            trigger_condition="Player performs actions consistent with this motif",
            intensity_change=1,
            probability=0.8,
            cooldown_hours=6
        )
        
        # Rule: Motifs weaken over time without reinforcement
        decay_rule = MotifEvolutionRule(
            trigger_type=MotifEvolutionTrigger.TIME_PASSAGE,
            trigger_condition="No reinforcing actions for extended period",
            intensity_change=-1,
            probability=0.3,
            cooldown_hours=72  # 3 days
        )
        
        # Rule: Contradictory actions can weaken or transform motifs
        contradiction_rule = MotifEvolutionRule(
            trigger_type=MotifEvolutionTrigger.PLAYER_ACTION,
            trigger_condition="Player performs actions opposing this motif",
            intensity_change=-2,
            probability=0.9,
            cooldown_hours=1
        )
        
        motif.add_evolution_rule(reinforcement_rule)
        motif.add_evolution_rule(decay_rule)
        motif.add_evolution_rule(contradiction_rule)
    
    async def _reinforce_pc_motif(
        self, 
        pc_motif: PlayerCharacterMotif, 
        action_context: Dict[str, Any]
    ) -> PlayerCharacterMotif:
        """Reinforce an existing PC motif with a new action."""
        
        motif = pc_motif.motif
        
        # Apply reinforcement intensity modifier
        reinforcement_strength = action_context.get("intensity", 1.0)
        modifier_id = f"reinforcement_{datetime.utcnow().timestamp()}"
        
        motif.apply_intensity_modifier(
            modifier_id, 
            reinforcement_strength, 
            f"Reinforced by {action_context.get('action_description', 'player action')}"
        )
        
        # Add to evolution history
        motif.evolution_history.append({
            "timestamp": datetime.utcnow(),
            "change_type": "reinforcement",
            "action_context": action_context,
            "intensity_change": reinforcement_strength,
            "new_effective_intensity": motif.get_effective_intensity()
        })
        
        # Update repository
        await self.repository.update_motif(motif.id, motif.dict())
        
        logger.info(f"Reinforced PC motif '{motif.name}' for player {pc_motif.player_id}")
        return pc_motif
    
    async def _create_action_motif(
        self, 
        player_id: str, 
        category: MotifCategory, 
        action_type: str,
        action_context: Dict[str, Any], 
        x: float, 
        y: float
    ) -> PlayerCharacterMotif:
        """Create a new PC motif based on a player action."""
        
        # Generate motif name and description based on action
        motif_names = {
            MotifCategory.HOPE: ["Beacon of Hope", "Champion's Light", "Inspiring Presence"],
            MotifCategory.BETRAYAL: ["Shadow of Betrayal", "Broken Trust", "Deceiver's Mark"],
            MotifCategory.SACRIFICE: ["Noble Sacrifice", "Selfless Devotion", "Hero's Burden"],
            MotifCategory.VENGEANCE: ["Seeker of Justice", "Vengeful Spirit", "Reckoning's Edge"],
            MotifCategory.REVELATION: ["Truth Seeker", "Bearer of Secrets", "Enlightened One"],
            MotifCategory.RUIN: ["Agent of Destruction", "Bringer of Ruin", "Chaos Walker"],
            MotifCategory.PROTECTION: ["Guardian's Shield", "Protector's Vigil", "Sanctuary Keeper"],
            MotifCategory.ASCENSION: ["Rising Leader", "Destined Ruler", "Born Commander"],
            MotifCategory.DECEPTION: ["Master of Lies", "Shadow Weaver", "False Face"],
            MotifCategory.REDEMPTION: ["Path of Redemption", "Second Chance", "Redeemed Soul"]
        }
        
        name = random.choice(motif_names.get(category, ["Unknown Influence"]))
        description = f"A motif born from {action_context.get('action_description', 'a significant action')}"
        
        # Create motif data
        motif_create = MotifCreate(
            name=name,
            description=description,
            category=category,
            scope=MotifScope.PLAYER_CHARACTER,
            intensity=action_context.get("intensity", 3),
            duration_days=action_context.get("duration_days", 30),
            effects=[
                MotifEffect(
                    target=MotifEffectTarget.NPC,
                    intensity=action_context.get("intensity", 3),
                    description=f"NPCs react to the player's reputation for {category.value}",
                    parameters={"reputation_type": category.value}
                )
            ]
        )
        
        # Create the PC motif
        pc_motif = await self.create_pc_motif(
            player_id=player_id,
            motif_data=motif_create,
            source_event=action_type,
            influence_range=action_context.get("influence_range", 100.0),
            visibility=action_context.get("visibility", "subtle")
        )
        
        # Set initial location
        await self.update_player_location(player_id, x, y)
        
        return pc_motif
    
    def _generate_npc_reaction_guidance(
        self, 
        influencing_motifs: List[PlayerCharacterMotif]
    ) -> str:
        """Generate guidance for how NPCs should react to PC motifs."""
        
        if not influencing_motifs:
            return ""
        
        primary_motif = influencing_motifs[0]
        category = primary_motif.motif.category
        intensity = primary_motif.motif.get_effective_intensity()
        visibility = primary_motif.visibility
        
        # Base reactions by category
        reaction_templates = {
            MotifCategory.HOPE: {
                "high": "NPCs feel inspired and hopeful around the player, seeking their guidance",
                "medium": "NPCs are naturally drawn to the player's positive presence",
                "low": "NPCs feel slightly more optimistic when speaking with the player"
            },
            MotifCategory.BETRAYAL: {
                "high": "NPCs are deeply suspicious and mistrustful, speaking guardedly",
                "medium": "NPCs are cautious and hesitant to trust the player",
                "low": "NPCs feel slightly uneasy but can't pinpoint why"
            },
            MotifCategory.SACRIFICE: {
                "high": "NPCs regard the player with deep respect and reverence",
                "medium": "NPCs show admiration for the player's selfless nature",
                "low": "NPCs sense something noble about the player"
            }
            # Add more category templates as needed
        }
        
        # Determine intensity level
        if intensity >= 7:
            intensity_level = "high"
        elif intensity >= 4:
            intensity_level = "medium"
        else:
            intensity_level = "low"
        
        # Get base reaction
        reactions = reaction_templates.get(category, {})
        base_reaction = reactions.get(intensity_level, "NPCs react neutrally to the player")
        
        # Modify based on visibility
        if visibility == "hidden":
            base_reaction += ". The motif's influence is subtle and unconscious."
        elif visibility == "obvious":
            base_reaction += ". NPCs can clearly sense this aspect of the player's reputation."
        
        return base_reaction
    
    async def process_pc_motif_evolution(self, player_id: str) -> List[Dict[str, Any]]:
        """Process evolution for all of a player's motifs."""
        player_motifs = await self.get_player_motifs(player_id)
        evolution_events = []
        
        for pc_motif in player_motifs:
            motif = pc_motif.motif
            
            # Check for applicable evolution rules
            applicable_rules = motif.can_evolve(MotifEvolutionTrigger.TIME_PASSAGE)
            
            for rule in applicable_rules:
                # Roll for probability
                if random.random() <= rule.probability:
                    # Apply evolution
                    changes = {}
                    
                    if rule.intensity_change != 0:
                        old_intensity = motif.intensity
                        new_intensity = max(1, min(10, old_intensity + rule.intensity_change))
                        motif.intensity = new_intensity
                        changes["intensity"] = {"old": old_intensity, "new": new_intensity}
                    
                    if rule.lifecycle_change:
                        old_lifecycle = motif.lifecycle
                        motif.lifecycle = rule.lifecycle_change
                        changes["lifecycle"] = {"old": old_lifecycle, "new": rule.lifecycle_change}
                    
                    if rule.category_change:
                        old_category = motif.category
                        motif.category = rule.category_change
                        changes["category"] = {"old": old_category, "new": rule.category_change}
                    
                    # Update last evolution time
                    motif.last_evolution = datetime.utcnow()
                    motif.updated_at = motif.last_evolution
                    
                    # Record evolution event
                    evolution_event = {
                        "motif_id": motif.id,
                        "motif_name": motif.name,
                        "trigger": rule.trigger_type,
                        "changes": changes,
                        "timestamp": motif.last_evolution
                    }
                    evolution_events.append(evolution_event)
                    
                    # Update in repository
                    await self.repository.update_motif(motif.id, motif.dict())
                    
                    logger.info(f"Evolved PC motif '{motif.name}' for player {player_id}: {changes}")
        
        return evolution_events 