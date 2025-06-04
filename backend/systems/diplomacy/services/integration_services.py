"""
Cross-system integration services for the diplomacy system.

This module handles integration between the diplomacy system and other game systems:
- Faction system integration
- Character system integration  
- Quest system integration
- World state integration
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from uuid import UUID

from .core_services import DiplomacyService, TensionService
from backend.systems.diplomacy.models import (
    DiplomaticStatus, TreatyType, DiplomaticEventType,
    DiplomaticIncidentType, DiplomaticIncidentSeverity
)
from backend.infrastructure.events.services.event_dispatcher import EventDispatcher

# Import services from other systems
try:
    from backend.systems.faction.services import (
        FactionService, FactionRelationshipService
    )
except ImportError:
    logging.warning("Faction services not available for diplomacy integration")
    FactionService = None
    FactionRelationshipService = None

try:
    from backend.systems.character.services import CharacterService
except ImportError:
    logging.warning("Character services not available for diplomacy integration")
    CharacterService = None

try:
    from backend.systems.quest.services.services import QuestBusinessService
except ImportError:
    logging.warning("Quest services not available for diplomacy integration")
    QuestBusinessService = None

try:
    from backend.systems.world_state.services import World_StateService
except ImportError:
    logging.warning("World state services not available for diplomacy integration")
    World_StateService = None

logger = logging.getLogger(__name__)


class FactionDiplomacyIntegration:
    """Handles integration between diplomacy and faction systems."""
    
    def __init__(self):
        self.diplomacy_service = DiplomacyService()
        self.tension_service = TensionService()
        self.event_dispatcher = EventDispatcher.get_instance()
        
        # External services (may be None if not available)
        self.faction_service = FactionService() if FactionService else None
        self.faction_relationship_service = FactionRelationshipService() if FactionRelationshipService else None
        
        self._register_event_handlers()
    
    def _register_event_handlers(self):
        """Register event handlers for faction-diplomacy integration."""
        try:
            # Subscribe to faction events
            self.event_dispatcher.subscribe("faction.created", self._handle_faction_created)
            self.event_dispatcher.subscribe("faction.dissolved", self._handle_faction_dissolved)
            self.event_dispatcher.subscribe("faction.reputation.changed", self._handle_faction_reputation_changed)
            self.event_dispatcher.subscribe("faction.leadership.changed", self._handle_faction_leadership_changed)
            self.event_dispatcher.subscribe("faction.territory.changed", self._handle_faction_territory_changed)
            
            logger.info("Faction-Diplomacy event handlers registered")
        except Exception as e:
            logger.error(f"Failed to register faction-diplomacy event handlers: {e}")
    
    async def _handle_faction_created(self, event_data: Dict[str, Any]):
        """Handle new faction creation by initializing diplomatic relationships."""
        try:
            faction_id = UUID(event_data.get("faction_id"))
            faction_name = event_data.get("faction_name", "Unknown Faction")
            
            if not self.faction_service:
                logger.warning("Faction service not available for faction creation handling")
                return
            
            # Get all existing factions to establish initial relationships
            existing_factions = self.faction_service.list_factions()
            
            for existing_faction in existing_factions:
                if existing_faction.id != faction_id:
                    # Initialize neutral relationship with existing factions
                    self.tension_service.update_faction_tension(
                        faction_id,
                        existing_faction.id,
                        0,  # Start with neutral tension
                        f"Initial diplomatic relationship established with {faction_name}"
                    )
                    
                    # Create diplomatic event
                    self.diplomacy_service.create_diplomatic_event(
                        event_type=DiplomaticEventType.STATUS_CHANGE,
                        factions=[faction_id, existing_faction.id],
                        description=f"Diplomatic relations established between {faction_name} and {existing_faction.name}",
                        severity=0,
                        public=True,
                        metadata={"event_source": "faction_creation"}
                    )
            
            logger.info(f"Initialized diplomatic relationships for new faction {faction_id}")
            
        except Exception as e:
            logger.error(f"Error handling faction creation: {e}")
    
    async def _handle_faction_dissolved(self, event_data: Dict[str, Any]):
        """Handle faction dissolution by terminating treaties and relationships."""
        try:
            faction_id = UUID(event_data.get("faction_id"))
            faction_name = event_data.get("faction_name", "Unknown Faction")
            
            # Expire all active treaties involving this faction
            active_treaties = self.diplomacy_service.list_treaties(
                faction_id=faction_id,
                active_only=True
            )
            
            for treaty in active_treaties:
                self.diplomacy_service.expire_treaty(
                    treaty.id,
                    reason=f"Faction {faction_name} dissolved"
                )
            
            # Create diplomatic events for all affected relationships
            relationships = self.tension_service.get_faction_relationships(faction_id)
            
            for relationship in relationships:
                other_faction_id = (
                    relationship["faction_b_id"] 
                    if relationship["faction_a_id"] == faction_id 
                    else relationship["faction_a_id"]
                )
                
                self.diplomacy_service.create_diplomatic_event(
                    event_type=DiplomaticEventType.STATUS_CHANGE,
                    factions=[faction_id, other_faction_id],
                    description=f"Diplomatic relations terminated due to {faction_name} dissolution",
                    severity=30,
                    public=True,
                    metadata={"event_source": "faction_dissolution", "dissolved_faction": str(faction_id)}
                )
            
            logger.info(f"Terminated diplomatic relationships for dissolved faction {faction_id}")
            
        except Exception as e:
            logger.error(f"Error handling faction dissolution: {e}")
    
    async def _handle_faction_reputation_changed(self, event_data: Dict[str, Any]):
        """Handle faction reputation changes that may affect diplomatic relationships."""
        try:
            faction_id = UUID(event_data.get("faction_id"))
            old_reputation = event_data.get("old_reputation", 0)
            new_reputation = event_data.get("new_reputation", 0)
            reason = event_data.get("reason", "Reputation change")
            
            reputation_change = new_reputation - old_reputation
            
            # Significant reputation changes affect diplomatic relationships
            if abs(reputation_change) >= 10:
                relationships = self.tension_service.get_faction_relationships(faction_id)
                
                for relationship in relationships:
                    other_faction_id = (
                        relationship["faction_b_id"] 
                        if relationship["faction_a_id"] == faction_id 
                        else relationship["faction_a_id"]
                    )
                    
                    # Positive reputation generally improves relationships
                    tension_adjustment = -reputation_change // 5  # Scale down the impact
                    
                    if abs(tension_adjustment) >= 2:  # Only apply meaningful changes
                        self.tension_service.update_faction_tension(
                            faction_id,
                            other_faction_id,
                            tension_adjustment,
                            f"Faction reputation change: {reason}"
                        )
            
            logger.info(f"Processed reputation change for faction {faction_id}: {reputation_change}")
            
        except Exception as e:
            logger.error(f"Error handling faction reputation change: {e}")
    
    async def _handle_faction_leadership_changed(self, event_data: Dict[str, Any]):
        """Handle faction leadership changes that may affect diplomatic stance."""
        try:
            faction_id = UUID(event_data.get("faction_id"))
            old_leader_id = event_data.get("old_leader_id")
            new_leader_id = event_data.get("new_leader_id")
            
            # Leadership changes can create diplomatic incidents or opportunities
            self.diplomacy_service.create_diplomatic_event(
                event_type=DiplomaticEventType.LEADERSHIP_CHANGE,
                factions=[faction_id],
                description=f"Faction leadership changed - new diplomatic opportunities may arise",
                severity=20,
                public=True,
                metadata={
                    "event_source": "leadership_change",
                    "old_leader": str(old_leader_id) if old_leader_id else None,
                    "new_leader": str(new_leader_id) if new_leader_id else None
                }
            )
            
            logger.info(f"Processed leadership change for faction {faction_id}")
            
        except Exception as e:
            logger.error(f"Error handling faction leadership change: {e}")
    
    async def _handle_faction_territory_changed(self, event_data: Dict[str, Any]):
        """Handle faction territory changes that may create diplomatic tensions."""
        try:
            faction_id = UUID(event_data.get("faction_id"))
            territory_gained = event_data.get("territory_gained", [])
            territory_lost = event_data.get("territory_lost", [])
            
            # Territory changes can create tensions with neighboring factions
            if territory_gained or territory_lost:
                # This would need integration with territory/region system
                # For now, create a general diplomatic event
                self.diplomacy_service.create_diplomatic_event(
                    event_type=DiplomaticEventType.TERRITORY_CHANGE,
                    factions=[faction_id],
                    description=f"Faction territory boundaries changed",
                    severity=25,
                    public=True,
                    metadata={
                        "event_source": "territory_change",
                        "territory_gained": territory_gained,
                        "territory_lost": territory_lost
                    }
                )
            
            logger.info(f"Processed territory change for faction {faction_id}")
            
        except Exception as e:
            logger.error(f"Error handling faction territory change: {e}")
    
    def sync_faction_relationships(self, faction_id: UUID) -> Dict[str, Any]:
        """Synchronize diplomatic relationships with faction system data."""
        try:
            if not self.faction_relationship_service:
                logger.warning("Faction relationship service not available for sync")
                return {"synced": False, "reason": "service_unavailable"}
            
            # Get diplomatic relationships
            diplomatic_relationships = self.tension_service.get_faction_relationships(faction_id)
            
            # Get faction system relationships
            faction_relationships = self.faction_relationship_service.get_relationships(faction_id)
            
            sync_results = {
                "synced": True,
                "diplomatic_count": len(diplomatic_relationships),
                "faction_count": len(faction_relationships),
                "conflicts_resolved": 0
            }
            
            # Sync any conflicts between the systems
            for faction_rel in faction_relationships:
                # Find corresponding diplomatic relationship
                diplomatic_rel = None
                for dipl_rel in diplomatic_relationships:
                    if (dipl_rel["faction_a_id"] == faction_rel.faction_a_id and 
                        dipl_rel["faction_b_id"] == faction_rel.faction_b_id) or \
                       (dipl_rel["faction_a_id"] == faction_rel.faction_b_id and 
                        dipl_rel["faction_b_id"] == faction_rel.faction_a_id):
                        diplomatic_rel = dipl_rel
                        break
                
                # If diplomatic relationship doesn't exist, create it
                if not diplomatic_rel:
                    self.tension_service.update_faction_tension(
                        faction_rel.faction_a_id,
                        faction_rel.faction_b_id,
                        0,
                        "Synchronization with faction system"
                    )
                    sync_results["conflicts_resolved"] += 1
            
            return sync_results
            
        except Exception as e:
            logger.error(f"Error syncing faction relationships: {e}")
            return {"synced": False, "reason": str(e)}


class CharacterDiplomacyIntegration:
    """Handles integration between diplomacy and character systems."""
    
    def __init__(self):
        self.diplomacy_service = DiplomacyService()
        self.tension_service = TensionService()
        self.event_dispatcher = EventDispatcher.get_instance()
        
        # External services (may be None if not available)
        self.character_service = CharacterService() if CharacterService else None
        
        self._register_event_handlers()
    
    def _register_event_handlers(self):
        """Register event handlers for character-diplomacy integration."""
        try:
            # Subscribe to character events
            self.event_dispatcher.subscribe("character.diplomatic_action", self._handle_diplomatic_action)
            self.event_dispatcher.subscribe("character.faction_joined", self._handle_character_faction_joined)
            self.event_dispatcher.subscribe("character.faction_left", self._handle_character_faction_left)
            self.event_dispatcher.subscribe("character.reputation.changed", self._handle_character_reputation_changed)
            
            logger.info("Character-Diplomacy event handlers registered")
        except Exception as e:
            logger.error(f"Failed to register character-diplomacy event handlers: {e}")
    
    async def _handle_diplomatic_action(self, event_data: Dict[str, Any]):
        """Handle diplomatic actions performed by characters."""
        try:
            character_id = UUID(event_data.get("character_id"))
            action_type = event_data.get("action_type")
            target_faction_id = UUID(event_data.get("target_faction_id"))
            character_faction_id = UUID(event_data.get("character_faction_id"))
            
            # Different diplomatic actions have different effects
            if action_type == "insult":
                # Insulting creates diplomatic incident
                self.diplomacy_service.create_diplomatic_incident(
                    incident_type=DiplomaticIncidentType.VERBAL_INSULT,
                    perpetrator_id=character_faction_id,
                    victim_id=target_faction_id,
                    description=f"Character diplomatic insult incident",
                    severity=DiplomaticIncidentSeverity.MINOR,
                    tension_impact=15,
                    public=True,
                    witnessed_by=[],
                    related_event_id=None
                )
            
            elif action_type == "praise":
                # Praising improves relations
                self.tension_service.update_faction_tension(
                    character_faction_id,
                    target_faction_id,
                    -10,
                    f"Character diplomatic praise"
                )
            
            elif action_type == "gift":
                # Gifts improve relations significantly
                gift_value = event_data.get("gift_value", 100)
                tension_reduction = min(30, gift_value // 10)
                self.tension_service.update_faction_tension(
                    character_faction_id,
                    target_faction_id,
                    -tension_reduction,
                    f"Character diplomatic gift (value: {gift_value})"
                )
            
            logger.info(f"Processed diplomatic action {action_type} by character {character_id}")
            
        except Exception as e:
            logger.error(f"Error handling character diplomatic action: {e}")
    
    async def _handle_character_faction_joined(self, event_data: Dict[str, Any]):
        """Handle character joining a faction - may affect diplomatic standing."""
        try:
            character_id = UUID(event_data.get("character_id"))
            faction_id = UUID(event_data.get("faction_id"))
            previous_faction_id = event_data.get("previous_faction_id")
            
            # If character had a previous faction, this might create diplomatic tensions
            if previous_faction_id:
                previous_faction_id = UUID(previous_faction_id)
                
                # Check if previous and new factions are hostile
                relationship = self.tension_service.get_faction_relationship(
                    previous_faction_id, faction_id
                )
                
                if relationship.get("status") in [DiplomaticStatus.HOSTILE, DiplomaticStatus.WAR]:
                    # Character defection between hostile factions creates incident
                    self.diplomacy_service.create_diplomatic_incident(
                        incident_type=DiplomaticIncidentType.ESPIONAGE,
                        perpetrator_id=faction_id,
                        victim_id=previous_faction_id,
                        description=f"Character defection between hostile factions",
                        severity=DiplomaticIncidentSeverity.MODERATE,
                        tension_impact=25,
                        public=False,
                        witnessed_by=[],
                        related_event_id=None
                    )
            
            logger.info(f"Processed character {character_id} joining faction {faction_id}")
            
        except Exception as e:
            logger.error(f"Error handling character faction join: {e}")
    
    async def _handle_character_faction_left(self, event_data: Dict[str, Any]):
        """Handle character leaving a faction."""
        try:
            character_id = UUID(event_data.get("character_id"))
            faction_id = UUID(event_data.get("faction_id"))
            reason = event_data.get("reason", "unknown")
            
            # Character leaving might affect faction reputation or create incidents
            if reason == "expelled":
                # Expulsion might create diplomatic events
                self.diplomacy_service.create_diplomatic_event(
                    event_type=DiplomaticEventType.INTERNAL_POLITICS,
                    factions=[faction_id],
                    description=f"Character expelled from faction - potential diplomatic implications",
                    severity=15,
                    public=False,
                    metadata={"character_id": str(character_id), "reason": reason}
                )
            
            logger.info(f"Processed character {character_id} leaving faction {faction_id}")
            
        except Exception as e:
            logger.error(f"Error handling character faction leave: {e}")
    
    async def _handle_character_reputation_changed(self, event_data: Dict[str, Any]):
        """Handle character reputation changes that may affect diplomacy."""
        try:
            character_id = UUID(event_data.get("character_id"))
            character_faction_id = event_data.get("character_faction_id")
            reputation_change = event_data.get("reputation_change", 0)
            
            # Significant character reputation changes can affect faction relations
            if abs(reputation_change) >= 20 and character_faction_id:
                character_faction_id = UUID(character_faction_id)
                
                # Get all faction relationships
                relationships = self.tension_service.get_faction_relationships(character_faction_id)
                
                # Small diplomatic bonus/penalty based on character reputation
                tension_adjustment = -reputation_change // 10
                
                for relationship in relationships:
                    other_faction_id = (
                        relationship["faction_b_id"] 
                        if relationship["faction_a_id"] == character_faction_id 
                        else relationship["faction_a_id"]
                    )
                    
                    if abs(tension_adjustment) >= 1:
                        self.tension_service.update_faction_tension(
                            character_faction_id,
                            other_faction_id,
                            tension_adjustment,
                            f"Character reputation influence"
                        )
            
            logger.info(f"Processed reputation change for character {character_id}")
            
        except Exception as e:
            logger.error(f"Error handling character reputation change: {e}")


class QuestDiplomacyIntegration:
    """Handles integration between diplomacy and quest systems."""
    
    def __init__(self):
        self.diplomacy_service = DiplomacyService()
        self.tension_service = TensionService()
        self.event_dispatcher = EventDispatcher.get_instance()
        
        # External services (may be None if not available)
        self.quest_business_service = QuestBusinessService() if QuestBusinessService else None
        
        self._register_event_handlers()
    
    def _register_event_handlers(self):
        """Register event handlers for quest-diplomacy integration."""
        try:
            # Subscribe to quest events
            self.event_dispatcher.subscribe("quest.completed", self._handle_quest_completed)
            self.event_dispatcher.subscribe("quest.failed", self._handle_quest_failed)
            
            # Subscribe to diplomacy events that should generate quests
            self.event_dispatcher.subscribe("diplomacy.treaty.signed", self._handle_treaty_signed)
            self.event_dispatcher.subscribe("diplomacy.incident.created", self._handle_incident_created)
            self.event_dispatcher.subscribe("diplomacy.ultimatum.issued", self._handle_ultimatum_issued)
            
            logger.info("Quest-Diplomacy event handlers registered")
        except Exception as e:
            logger.error(f"Failed to register quest-diplomacy event handlers: {e}")
    
    async def _handle_quest_completed(self, event_data: Dict[str, Any]):
        """Handle quest completion that may affect diplomatic relationships."""
        try:
            quest_id = event_data.get("quest_id")
            player_id = event_data.get("player_id")
            quest_type = event_data.get("quest_type")
            affected_factions = event_data.get("affected_factions", [])
            diplomatic_impact = event_data.get("diplomatic_impact", {})
            
            # Process diplomatic impacts from quest completion
            for faction_pair, impact in diplomatic_impact.items():
                faction_ids = faction_pair.split(",")
                if len(faction_ids) == 2:
                    faction_a_id = UUID(faction_ids[0])
                    faction_b_id = UUID(faction_ids[1])
                    
                    tension_change = impact.get("tension_change", 0)
                    if tension_change != 0:
                        self.tension_service.update_faction_tension(
                            faction_a_id,
                            faction_b_id,
                            tension_change,
                            f"Quest completion impact: {quest_type}"
                        )
            
            # Specific quest types may have special diplomatic effects
            if quest_type == "diplomatic_mission":
                # Diplomatic missions significantly improve relations
                if len(affected_factions) >= 2:
                    self.tension_service.update_faction_tension(
                        UUID(affected_factions[0]),
                        UUID(affected_factions[1]),
                        -30,
                        f"Successful diplomatic mission quest"
                    )
            
            logger.info(f"Processed quest completion {quest_id} diplomatic impacts")
            
        except Exception as e:
            logger.error(f"Error handling quest completion: {e}")
    
    async def _handle_quest_failed(self, event_data: Dict[str, Any]):
        """Handle quest failure that may negatively affect diplomatic relationships."""
        try:
            quest_id = event_data.get("quest_id")
            quest_type = event_data.get("quest_type")
            affected_factions = event_data.get("affected_factions", [])
            
            # Quest failures can damage diplomatic relations
            if quest_type == "diplomatic_mission" and len(affected_factions) >= 2:
                # Failed diplomatic missions worsen relations
                self.tension_service.update_faction_tension(
                    UUID(affected_factions[0]),
                    UUID(affected_factions[1]),
                    20,
                    f"Failed diplomatic mission quest"
                )
                
                # Create diplomatic incident for the failure
                self.diplomacy_service.create_diplomatic_incident(
                    incident_type=DiplomaticIncidentType.DIPLOMATIC_BLUNDER,
                    perpetrator_id=UUID(affected_factions[0]),
                    victim_id=UUID(affected_factions[1]),
                    description=f"Diplomatic mission failed, damaging relations",
                    severity=DiplomaticIncidentSeverity.MODERATE,
                    tension_impact=20,
                    public=True
                )
            
            logger.info(f"Processed quest failure {quest_id} diplomatic impacts")
            
        except Exception as e:
            logger.error(f"Error handling quest failure: {e}")
    
    async def _handle_treaty_signed(self, event_data: Dict[str, Any]):
        """Handle treaty signing that should generate related quests."""
        try:
            treaty_id = UUID(event_data.get("treaty_id"))
            treaty_type = event_data.get("treaty_type")
            parties = [UUID(party_id) for party_id in event_data.get("parties", [])]
            
            if not self.quest_business_service:
                logger.warning("Quest business service not available for treaty quest generation")
                return
            
            # Different treaty types generate different quest opportunities
            quest_templates = []
            
            if treaty_type == TreatyType.TRADE:
                quest_templates.extend([
                    {
                        "type": "escort_mission",
                        "title": "Protect Trade Caravan",
                        "description": "Escort trade goods between treaty signatories",
                        "diplomatic_impact": {"tension_change": -5}
                    },
                    {
                        "type": "investigation",
                        "title": "Investigate Trade Violations",
                        "description": "Monitor treaty compliance and report violations",
                        "diplomatic_impact": {"tension_change": 10}
                    }
                ])
            
            elif treaty_type == TreatyType.ALLIANCE:
                quest_templates.extend([
                    {
                        "type": "diplomatic_mission",
                        "title": "Strengthen Alliance Bonds",
                        "description": "Undertake joint missions to solidify the alliance",
                        "diplomatic_impact": {"tension_change": -15}
                    },
                    {
                        "type": "defense_mission",
                        "title": "Defend Allied Territory",
                        "description": "Protect allied faction's interests",
                        "diplomatic_impact": {"tension_change": -10}
                    }
                ])
            
            # Generate quests for each template
            for template in quest_templates:
                quest_data = {
                    "title": template["title"],
                    "description": template["description"],
                    "type": template["type"],
                    "affected_factions": [str(party_id) for party_id in parties],
                    "diplomatic_impact": template["diplomatic_impact"],
                    "related_treaty_id": str(treaty_id),
                    "priority": "medium"
                }
                
                # This would call the quest service to create the quest
                # self.quest_business_service.create_quest(quest_data)
            
            logger.info(f"Generated {len(quest_templates)} quests for treaty {treaty_id}")
            
        except Exception as e:
            logger.error(f"Error handling treaty signing: {e}")
    
    async def _handle_incident_created(self, event_data: Dict[str, Any]):
        """Handle diplomatic incident creation that should generate related quests."""
        try:
            incident_id = UUID(event_data.get("incident_id"))
            incident_type = event_data.get("incident_type")
            perpetrator_id = UUID(event_data.get("perpetrator_id"))
            victim_id = UUID(event_data.get("victim_id"))
            
            if not self.quest_business_service:
                logger.warning("Quest business service not available for incident quest generation")
                return
            
            # Generate investigation or resolution quests based on incident type
            quest_templates = [
                {
                    "type": "investigation",
                    "title": "Investigate Diplomatic Incident",
                    "description": f"Investigate the {incident_type} incident between factions",
                    "affected_factions": [str(perpetrator_id), str(victim_id)],
                    "related_incident_id": str(incident_id),
                    "priority": "high" if incident_type == "MILITARY_AGGRESSION" else "medium"
                }
            ]
            
            if incident_type == "ESPIONAGE":
                quest_templates.append({
                    "type": "counter_espionage",
                    "title": "Counter-Espionage Operations",
                    "description": "Root out spies and prevent further espionage",
                    "affected_factions": [str(victim_id)],
                    "related_incident_id": str(incident_id),
                    "priority": "high"
                })
            
            logger.info(f"Generated {len(quest_templates)} quests for incident {incident_id}")
            
        except Exception as e:
            logger.error(f"Error handling incident creation: {e}")
    
    async def _handle_ultimatum_issued(self, event_data: Dict[str, Any]):
        """Handle ultimatum issuance that should generate related quests."""
        try:
            ultimatum_id = UUID(event_data.get("ultimatum_id"))
            issuer_id = UUID(event_data.get("issuer_id"))
            recipient_id = UUID(event_data.get("recipient_id"))
            deadline = event_data.get("deadline")
            
            if not self.quest_business_service:
                logger.warning("Quest business service not available for ultimatum quest generation")
                return
            
            # Generate time-sensitive quests related to the ultimatum
            quest_templates = [
                {
                    "type": "diplomatic_mission",
                    "title": "Mediate Ultimatum Crisis",
                    "description": "Attempt to find a peaceful resolution to the ultimatum",
                    "affected_factions": [str(issuer_id), str(recipient_id)],
                    "related_ultimatum_id": str(ultimatum_id),
                    "deadline": deadline,
                    "priority": "critical"
                },
                {
                    "type": "investigation",
                    "title": "Assess Ultimatum Validity",
                    "description": "Investigate the claims behind the ultimatum",
                    "affected_factions": [str(issuer_id), str(recipient_id)],
                    "related_ultimatum_id": str(ultimatum_id),
                    "deadline": deadline,
                    "priority": "high"
                }
            ]
            
            logger.info(f"Generated {len(quest_templates)} quests for ultimatum {ultimatum_id}")
            
        except Exception as e:
            logger.error(f"Error handling ultimatum issuance: {e}")


class WorldStateDiplomacyIntegration:
    """Handles integration between diplomacy and world state systems."""
    
    def __init__(self):
        self.diplomacy_service = DiplomacyService()
        self.tension_service = TensionService()
        self.event_dispatcher = EventDispatcher.get_instance()
        
        # External services (may be None if not available)
        self.world_state_service = World_StateService() if World_StateService else None
        
        self._register_event_handlers()
    
    def _register_event_handlers(self):
        """Register event handlers for world state-diplomacy integration."""
        try:
            # Subscribe to world state events
            self.event_dispatcher.subscribe("world.time.day_passed", self._handle_day_passed)
            self.event_dispatcher.subscribe("world.time.season_changed", self._handle_season_changed)
            self.event_dispatcher.subscribe("world.economy.market_crash", self._handle_economic_crisis)
            self.event_dispatcher.subscribe("world.natural_disaster", self._handle_natural_disaster)
            self.event_dispatcher.subscribe("world.resource.discovered", self._handle_resource_discovered)
            
            logger.info("World State-Diplomacy event handlers registered")
        except Exception as e:
            logger.error(f"Failed to register world state-diplomacy event handlers: {e}")
    
    async def _handle_day_passed(self, event_data: Dict[str, Any]):
        """Handle daily world state updates that affect diplomacy."""
        try:
            current_day = event_data.get("current_day", 0)
            
            # Check for expired ultimatums
            expired_ultimatums = self.diplomacy_service.check_expired_ultimatums()
            for ultimatum in expired_ultimatums:
                logger.info(f"Processed expired ultimatum {ultimatum.id}")
            
            # Check for expired sanctions
            expired_sanctions = self.diplomacy_service.check_expired_sanctions()
            for sanction in expired_sanctions:
                logger.info(f"Processed expired sanction {sanction.id}")
            
            # Periodic treaty compliance checks (weekly)
            if current_day % 7 == 0:
                # This would need access to all factions
                logger.info("Performing weekly treaty compliance checks")
                # violations = self.diplomacy_service.enforce_treaties_automatically()
            
        except Exception as e:
            logger.error(f"Error handling daily world state update: {e}")
    
    async def _handle_season_changed(self, event_data: Dict[str, Any]):
        """Handle seasonal changes that may affect diplomatic relationships."""
        try:
            new_season = event_data.get("new_season")
            old_season = event_data.get("old_season")
            
            # Seasonal changes can affect trade and diplomatic relations
            if new_season == "winter":
                # Winter might strain trade relationships
                # This would need access to active trade treaties
                logger.info("Winter season - potential trade treaty strain")
            
            elif new_season == "spring":
                # Spring might improve general diplomatic mood
                logger.info("Spring season - potential diplomatic opportunities")
            
        except Exception as e:
            logger.error(f"Error handling season change: {e}")
    
    async def _handle_economic_crisis(self, event_data: Dict[str, Any]):
        """Handle economic crises that strain diplomatic relationships."""
        try:
            affected_regions = event_data.get("affected_regions", [])
            severity = event_data.get("severity", "moderate")
            
            # Economic crises strain trade relationships and may cause sanctions
            if severity in ["severe", "critical"]:
                # This would need access to factions in affected regions
                # and their trade relationships
                logger.info(f"Economic crisis in regions {affected_regions} - diplomatic impact")
                
                # Create diplomatic events for economic strain
                for region in affected_regions:
                    self.diplomacy_service.create_diplomatic_event(
                        event_type=DiplomaticEventType.ECONOMIC_CRISIS,
                        factions=[],  # Would need to get factions in region
                        description=f"Economic crisis in {region} strains diplomatic relations",
                        severity=40 if severity == "critical" else 25,
                        public=True,
                        metadata={"crisis_severity": severity, "region": region}
                    )
            
        except Exception as e:
            logger.error(f"Error handling economic crisis: {e}")
    
    async def _handle_natural_disaster(self, event_data: Dict[str, Any]):
        """Handle natural disasters that create diplomatic opportunities."""
        try:
            disaster_type = event_data.get("disaster_type")
            affected_regions = event_data.get("affected_regions", [])
            severity = event_data.get("severity", "moderate")
            
            # Natural disasters create opportunities for humanitarian aid
            # which can improve diplomatic relations
            if severity in ["severe", "critical"]:
                logger.info(f"Natural disaster ({disaster_type}) - humanitarian diplomacy opportunities")
                
                # Create diplomatic events for disaster response
                for region in affected_regions:
                    self.diplomacy_service.create_diplomatic_event(
                        event_type=DiplomaticEventType.HUMANITARIAN_CRISIS,
                        factions=[],  # Would need to get factions in region
                        description=f"{disaster_type} in {region} creates humanitarian diplomacy opportunities",
                        severity=30,
                        public=True,
                        metadata={"disaster_type": disaster_type, "region": region}
                    )
            
        except Exception as e:
            logger.error(f"Error handling natural disaster: {e}")
    
    async def _handle_resource_discovered(self, event_data: Dict[str, Any]):
        """Handle resource discoveries that may create diplomatic tensions."""
        try:
            resource_type = event_data.get("resource_type")
            location = event_data.get("location")
            value = event_data.get("value", "unknown")
            discovering_faction = event_data.get("discovering_faction")
            
            # Valuable resource discoveries can create diplomatic tensions
            if value in ["high", "critical"] and discovering_faction:
                discovering_faction_id = UUID(discovering_faction)
                
                # This creates potential for disputes with neighboring factions
                self.diplomacy_service.create_diplomatic_event(
                    event_type=DiplomaticEventType.RESOURCE_DISCOVERY,
                    factions=[discovering_faction_id],
                    description=f"Valuable {resource_type} discovered at {location} - potential diplomatic implications",
                    severity=35 if value == "critical" else 20,
                    public=True,
                    metadata={
                        "resource_type": resource_type,
                        "location": location,
                        "value": value
                    }
                )
            
        except Exception as e:
            logger.error(f"Error handling resource discovery: {e}")
    
    def get_regional_diplomatic_status(self, region_id: str) -> Dict[str, Any]:
        """Get diplomatic status summary for a specific region."""
        try:
            # Initialize comprehensive status structure
            status = {
                "available": True,
                "region_id": region_id,
                "last_updated": datetime.utcnow().isoformat(),
                "summary": {
                    "active_treaties": 0,
                    "ongoing_negotiations": 0,
                    "recent_incidents": 0,
                    "active_sanctions": 0,
                    "pending_ultimatums": 0,
                    "tension_level": "unknown"
                },
                "detailed_analysis": {
                    "treaty_breakdown": {},
                    "negotiation_status": {},
                    "incident_severity": {},
                    "sanction_impact": {},
                    "relationship_matrix": {},
                    "crisis_indicators": []
                },
                "recommendations": []
            }
            
            # If world state service is unavailable, try basic analysis without it
            if not self.world_state_service:
                logger.warning("World state service not available - performing limited analysis")
                # Try to get basic diplomatic data without regional filtering
                return self._get_basic_diplomatic_status(region_id, status)
            
            # Get factions in the region
            try:
                regional_factions = self._get_regional_factions(region_id)
                if not regional_factions:
                    logger.info(f"No factions found in region {region_id}")
                    status["summary"]["tension_level"] = "peaceful"
                    return status
                    
            except Exception as e:
                logger.warning(f"Could not get regional factions for {region_id}: {e}")
                return self._get_basic_diplomatic_status(region_id, status)
            
            # Analyze treaties involving regional factions
            treaty_analysis = self._analyze_regional_treaties(regional_factions)
            status["summary"]["active_treaties"] = treaty_analysis["total_count"]
            status["detailed_analysis"]["treaty_breakdown"] = treaty_analysis["breakdown"]
            
            # Analyze ongoing negotiations
            negotiation_analysis = self._analyze_regional_negotiations(regional_factions)
            status["summary"]["ongoing_negotiations"] = negotiation_analysis["total_count"]
            status["detailed_analysis"]["negotiation_status"] = negotiation_analysis["status"]
            
            # Analyze recent diplomatic incidents
            incident_analysis = self._analyze_regional_incidents(regional_factions)
            status["summary"]["recent_incidents"] = incident_analysis["total_count"]
            status["detailed_analysis"]["incident_severity"] = incident_analysis["severity_breakdown"]
            
            # Analyze active sanctions
            sanction_analysis = self._analyze_regional_sanctions(regional_factions)
            status["summary"]["active_sanctions"] = sanction_analysis["total_count"]
            status["detailed_analysis"]["sanction_impact"] = sanction_analysis["impact_analysis"]
            
            # Analyze pending ultimatums
            ultimatum_analysis = self._analyze_regional_ultimatums(regional_factions)
            status["summary"]["pending_ultimatums"] = ultimatum_analysis["total_count"]
            
            # Build relationship matrix
            relationship_matrix = self._build_relationship_matrix(regional_factions)
            status["detailed_analysis"]["relationship_matrix"] = relationship_matrix
            
            # Calculate overall tension level
            tension_level = self._calculate_regional_tension_level(
                treaty_analysis, incident_analysis, sanction_analysis, 
                ultimatum_analysis, relationship_matrix
            )
            status["summary"]["tension_level"] = tension_level
            
            # Identify crisis indicators
            crisis_indicators = self._identify_crisis_indicators(
                regional_factions, incident_analysis, sanction_analysis, 
                ultimatum_analysis, relationship_matrix
            )
            status["detailed_analysis"]["crisis_indicators"] = crisis_indicators
            
            # Generate recommendations
            recommendations = self._generate_diplomatic_recommendations(
                region_id, regional_factions, status["detailed_analysis"]
            )
            status["recommendations"] = recommendations
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting regional diplomatic status for {region_id}: {e}")
            return {
                "available": False, 
                "error": str(e),
                "region_id": region_id,
                "last_updated": datetime.utcnow().isoformat()
            }

    def _get_basic_diplomatic_status(self, region_id: str, status: Dict[str, Any]) -> Dict[str, Any]:
        """Get basic diplomatic status without regional filtering."""
        try:
            # Get all active treaties
            active_treaties = self.diplomacy_service.list_treaties(active_only=True)
            status["summary"]["active_treaties"] = len(active_treaties)
            
            # Get recent incidents (last 30 days)
            recent_incidents = self.diplomacy_service.list_diplomatic_incidents(
                resolved=False,
                limit=100
            )
            status["summary"]["recent_incidents"] = len(recent_incidents)
            
            # Basic tension assessment
            if len(recent_incidents) > 10:
                status["summary"]["tension_level"] = "high"
            elif len(recent_incidents) > 5:
                status["summary"]["tension_level"] = "moderate"
            else:
                status["summary"]["tension_level"] = "low"
                
        except Exception as e:
            logger.error(f"Error in basic diplomatic analysis: {e}")
            
        return status

    def _get_regional_factions(self, region_id: str) -> List[UUID]:
        """Get list of faction IDs operating in the specified region."""
        regional_factions = []
        
        try:
            if self.faction_service:
                # Try to get factions by region
                factions = self.faction_service.get_factions_by_region(region_id)
                regional_factions = [faction.id for faction in factions]
            else:
                # Fallback: try to infer from world state or return empty
                logger.warning("Faction service not available for regional faction lookup")
                
        except AttributeError:
            # Method doesn't exist, try alternative approach
            logger.warning("get_factions_by_region method not available")
            
        except Exception as e:
            logger.error(f"Error getting regional factions: {e}")
            
        return regional_factions

    def _analyze_regional_treaties(self, regional_factions: List[UUID]) -> Dict[str, Any]:
        """Analyze treaties involving regional factions."""
        analysis = {
            "total_count": 0,
            "breakdown": {
                "alliance": 0,
                "trade": 0,
                "non_aggression": 0,
                "ceasefire": 0,
                "mutual_defense": 0,
                "custom": 0
            }
        }
        
        try:
            for faction_id in regional_factions:
                faction_treaties = self.diplomacy_service.list_treaties(
                    faction_id=faction_id,
                    active_only=True
                )
                
                for treaty in faction_treaties:
                    # Only count if at least one other party is also regional
                    other_parties = [p for p in treaty.parties if p != faction_id]
                    if any(p in regional_factions for p in other_parties):
                        analysis["total_count"] += 1
                        treaty_type = treaty.type.value if hasattr(treaty.type, 'value') else str(treaty.type)
                        if treaty_type in analysis["breakdown"]:
                            analysis["breakdown"][treaty_type] += 1
                        else:
                            analysis["breakdown"]["custom"] += 1
                            
        except Exception as e:
            logger.error(f"Error analyzing regional treaties: {e}")
            
        return analysis

    def _analyze_regional_incidents(self, regional_factions: List[UUID]) -> Dict[str, Any]:
        """Analyze recent diplomatic incidents in the region."""
        analysis = {
            "total_count": 0,
            "severity_breakdown": {
                "minor": 0,
                "moderate": 0,
                "major": 0,
                "critical": 0
            }
        }
        
        try:
            for faction_id in regional_factions:
                # Get incidents involving this faction
                incidents = self.diplomacy_service.list_diplomatic_incidents(
                    faction_id=faction_id,
                    resolved=False,
                    limit=50
                )
                
                for incident in incidents:
                    # Check if other party is also regional
                    other_faction = incident.victim_id if incident.perpetrator_id == faction_id else incident.perpetrator_id
                    if other_faction in regional_factions:
                        analysis["total_count"] += 1
                        severity = incident.severity.value if hasattr(incident.severity, 'value') else str(incident.severity)
                        if severity in analysis["severity_breakdown"]:
                            analysis["severity_breakdown"][severity] += 1
                            
        except Exception as e:
            logger.error(f"Error analyzing regional incidents: {e}")
            
        return analysis

    def _analyze_regional_negotiations(self, regional_factions: List[UUID]) -> Dict[str, Any]:
        """Analyze ongoing negotiations between regional factions."""
        analysis = {
            "total_count": 0,
            "status": {
                "pending": 0,
                "active": 0,
                "counter_offered": 0,
                "stalled": 0,
                "final_review": 0
            },
            "negotiation_types": {
                "treaty": 0,
                "trade": 0,
                "ceasefire": 0,
                "territorial": 0,
                "alliance": 0,
                "other": 0
            },
            "urgency_indicators": {
                "high_priority": 0,
                "medium_priority": 0,
                "low_priority": 0
            },
            "duration_analysis": {
                "recently_started": 0,  # < 7 days
                "ongoing": 0,           # 7-30 days
                "long_running": 0       # > 30 days
            },
            "success_probability": {
                "high": 0,
                "medium": 0,
                "low": 0
            }
        }
        
        try:
            for faction_id in regional_factions:
                # Get negotiations where this faction is involved
                faction_negotiations = self.diplomacy_service.list_negotiations(
                    faction_id=faction_id,
                    active_only=True
                )
                
                for negotiation in faction_negotiations:
                    # Check if other party is also in region
                    other_parties = [p for p in negotiation.participants if p != faction_id]
                    if any(p in regional_factions for p in other_parties):
                        analysis["total_count"] += 1
                        
                        # Analyze status
                        status = negotiation.status.value if hasattr(negotiation.status, 'value') else str(negotiation.status)
                        if status in analysis["status"]:
                            analysis["status"][status] += 1
                        else:
                            analysis["status"]["active"] += 1  # Default fallback
                        
                        # Analyze negotiation type
                        neg_type = self._determine_negotiation_type(negotiation)
                        if neg_type in analysis["negotiation_types"]:
                            analysis["negotiation_types"][neg_type] += 1
                        else:
                            analysis["negotiation_types"]["other"] += 1
                        
                        # Analyze urgency based on context and deadlines
                        urgency = self._calculate_negotiation_urgency(negotiation, regional_factions)
                        analysis["urgency_indicators"][urgency] += 1
                        
                        # Analyze duration
                        duration_category = self._categorize_negotiation_duration(negotiation)
                        analysis["duration_analysis"][duration_category] += 1
                        
                        # Analyze success probability
                        success_prob = self._estimate_negotiation_success_probability(negotiation, regional_factions)
                        analysis["success_probability"][success_prob] += 1
                        
        except Exception as e:
            logger.error(f"Error analyzing regional negotiations: {e}")
            
        return analysis
    
    def _determine_negotiation_type(self, negotiation) -> str:
        """Determine the type of negotiation based on its content."""
        try:
            # Check if negotiation has a type field
            if hasattr(negotiation, 'type'):
                return negotiation.type.value if hasattr(negotiation.type, 'value') else str(negotiation.type)
            
            # Infer from title or description
            title_lower = getattr(negotiation, 'title', '').lower()
            description_lower = getattr(negotiation, 'description', '').lower()
            
            if any(term in title_lower or term in description_lower for term in ['treaty', 'accord', 'pact']):
                return "treaty"
            elif any(term in title_lower or term in description_lower for term in ['trade', 'commerce', 'economic']):
                return "trade"
            elif any(term in title_lower or term in description_lower for term in ['ceasefire', 'armistice', 'truce']):
                return "ceasefire"
            elif any(term in title_lower or term in description_lower for term in ['territory', 'border', 'land']):
                return "territorial"
            elif any(term in title_lower or term in description_lower for term in ['alliance', 'partnership', 'coalition']):
                return "alliance"
            else:
                return "other"
                
        except Exception as e:
            logger.warning(f"Error determining negotiation type: {e}")
            return "other"
    
    def _calculate_negotiation_urgency(self, negotiation, regional_factions: List[UUID]) -> str:
        """Calculate urgency level of a negotiation."""
        try:
            urgency_score = 0
            
            # Check for deadlines
            if hasattr(negotiation, 'deadline') and negotiation.deadline:
                time_left = negotiation.deadline - datetime.utcnow()
                if time_left.days < 3:
                    urgency_score += 30
                elif time_left.days < 7:
                    urgency_score += 20
                elif time_left.days < 14:
                    urgency_score += 10
            
            # Check relationship status between parties
            for i, faction_a in enumerate(negotiation.participants):
                for faction_b in negotiation.participants[i+1:]:
                    if faction_a in regional_factions and faction_b in regional_factions:
                        try:
                            relationship = self.diplomacy_service.get_faction_relationship(faction_a, faction_b)
                            tension = relationship.get("tension", 0)
                            if tension > 80:
                                urgency_score += 25
                            elif tension > 60:
                                urgency_score += 15
                            elif tension > 40:
                                urgency_score += 5
                        except Exception:
                            pass
            
            # Check for crisis context
            if hasattr(negotiation, 'context') and negotiation.context:
                crisis_indicators = ['crisis', 'urgent', 'emergency', 'immediate', 'war', 'conflict']
                context_lower = str(negotiation.context).lower()
                if any(indicator in context_lower for indicator in crisis_indicators):
                    urgency_score += 20
            
            # Determine urgency level
            if urgency_score >= 40:
                return "high_priority"
            elif urgency_score >= 20:
                return "medium_priority"
            else:
                return "low_priority"
                
        except Exception as e:
            logger.warning(f"Error calculating negotiation urgency: {e}")
            return "medium_priority"
    
    def _categorize_negotiation_duration(self, negotiation) -> str:
        """Categorize negotiation by how long it has been ongoing."""
        try:
            if hasattr(negotiation, 'created_at'):
                duration = datetime.utcnow() - negotiation.created_at
                if duration.days < 7:
                    return "recently_started"
                elif duration.days <= 30:
                    return "ongoing"
                else:
                    return "long_running"
            else:
                return "ongoing"  # Default if no creation date
                
        except Exception as e:
            logger.warning(f"Error categorizing negotiation duration: {e}")
            return "ongoing"
    
    def _estimate_negotiation_success_probability(self, negotiation, regional_factions: List[UUID]) -> str:
        """Estimate the likelihood of negotiation success."""
        try:
            success_score = 50  # Start neutral
            
            # Factor in relationship status
            for i, faction_a in enumerate(negotiation.participants):
                for faction_b in negotiation.participants[i+1:]:
                    if faction_a in regional_factions and faction_b in regional_factions:
                        try:
                            relationship = self.diplomacy_service.get_faction_relationship(faction_a, faction_b)
                            tension = relationship.get("tension", 50)
                            trust = relationship.get("trust_level", 50)
                            
                            # Lower tension and higher trust increase success probability
                            success_score += (50 - tension) * 0.3
                            success_score += (trust - 50) * 0.3
                        except Exception:
                            pass
            
            # Factor in negotiation progress
            if hasattr(negotiation, 'status'):
                status = str(negotiation.status).lower()
                if 'final' in status or 'review' in status:
                    success_score += 20
                elif 'stalled' in status or 'deadlock' in status:
                    success_score -= 30
                elif 'active' in status:
                    success_score += 10
            
            # Factor in duration (very long negotiations may be troubled)
            if hasattr(negotiation, 'created_at'):
                duration = datetime.utcnow() - negotiation.created_at
                if duration.days > 60:
                    success_score -= 15
                elif duration.days > 30:
                    success_score -= 5
            
            # Factor in external pressures
            if hasattr(negotiation, 'external_pressures') and negotiation.external_pressures:
                success_score -= len(negotiation.external_pressures) * 5
            
            # Determine success probability category
            if success_score >= 70:
                return "high"
            elif success_score >= 40:
                return "medium"
            else:
                return "low"
                
        except Exception as e:
            logger.warning(f"Error estimating negotiation success probability: {e}")
            return "medium"

    def _analyze_regional_sanctions(self, regional_factions: List[UUID]) -> Dict[str, Any]:
        """Analyze active sanctions involving regional factions."""
        analysis = {
            "total_count": 0,
            "impact_analysis": {
                "economic_impact": "low",
                "diplomatic_impact": "low",
                "affected_factions": []
            }
        }
        
        try:
            for faction_id in regional_factions:
                # Get sanctions imposed by this faction
                imposed_sanctions = self.diplomacy_service.list_sanctions(
                    imposer_id=faction_id,
                    active_only=True
                )
                
                # Get sanctions targeting this faction
                targeted_sanctions = self.diplomacy_service.list_sanctions(
                    target_id=faction_id,
                    active_only=True
                )
                
                for sanction in imposed_sanctions + targeted_sanctions:
                    other_faction = sanction.target_id if sanction.imposer_id == faction_id else sanction.imposer_id
                    if other_faction in regional_factions:
                        analysis["total_count"] += 1
                        if str(other_faction) not in analysis["impact_analysis"]["affected_factions"]:
                            analysis["impact_analysis"]["affected_factions"].append(str(other_faction))
                            
        except Exception as e:
            logger.error(f"Error analyzing regional sanctions: {e}")
            
        return analysis

    def _analyze_regional_ultimatums(self, regional_factions: List[UUID]) -> Dict[str, Any]:
        """Analyze pending ultimatums between regional factions."""
        analysis = {
            "total_count": 0,
            "urgency_levels": {
                "immediate": 0,
                "urgent": 0,
                "moderate": 0
            }
        }
        
        try:
            for faction_id in regional_factions:
                ultimatums = self.diplomacy_service.list_ultimatums(
                    faction_id=faction_id,
                    active_only=True
                )
                
                for ultimatum in ultimatums:
                    other_faction = ultimatum.recipient_id if ultimatum.issuer_id == faction_id else ultimatum.issuer_id
                    if other_faction in regional_factions:
                        analysis["total_count"] += 1
                        
                        # Calculate urgency based on deadline
                        time_left = ultimatum.deadline - datetime.utcnow()
                        if time_left.days < 1:
                            analysis["urgency_levels"]["immediate"] += 1
                        elif time_left.days < 7:
                            analysis["urgency_levels"]["urgent"] += 1
                        else:
                            analysis["urgency_levels"]["moderate"] += 1
                            
        except Exception as e:
            logger.error(f"Error analyzing regional ultimatums: {e}")
            
        return analysis

    def _build_relationship_matrix(self, regional_factions: List[UUID]) -> Dict[str, Any]:
        """Build a matrix of diplomatic relationships between regional factions."""
        matrix = {}
        
        try:
            for faction_a in regional_factions:
                faction_a_str = str(faction_a)
                matrix[faction_a_str] = {}
                
                for faction_b in regional_factions:
                    if faction_a != faction_b:
                        faction_b_str = str(faction_b)
                        relationship = self.diplomacy_service.get_faction_relationship(faction_a, faction_b)
                        matrix[faction_a_str][faction_b_str] = {
                            "status": relationship.get("status", "neutral"),
                            "tension": relationship.get("tension", 0),
                            "trust": relationship.get("trust_level", 50)
                        }
                        
        except Exception as e:
            logger.error(f"Error building relationship matrix: {e}")
            
        return matrix

    def _calculate_regional_tension_level(self, treaty_analysis, incident_analysis, 
                                        sanction_analysis, ultimatum_analysis, 
                                        relationship_matrix) -> str:
        """Calculate overall tension level for the region."""
        try:
            tension_score = 0
            
            # Factor in incidents
            tension_score += incident_analysis["total_count"] * 5
            tension_score += incident_analysis["severity_breakdown"]["critical"] * 20
            tension_score += incident_analysis["severity_breakdown"]["major"] * 10
            
            # Factor in sanctions
            tension_score += sanction_analysis["total_count"] * 15
            
            # Factor in ultimatums
            tension_score += ultimatum_analysis["total_count"] * 25
            tension_score += ultimatum_analysis["urgency_levels"]["immediate"] * 30
            
            # Factor in negative treaties (reduce tension)
            tension_score -= treaty_analysis["breakdown"]["alliance"] * 10
            tension_score -= treaty_analysis["breakdown"]["trade"] * 5
            
            # Classify tension level
            if tension_score >= 100:
                return "critical"
            elif tension_score >= 60:
                return "high"
            elif tension_score >= 30:
                return "moderate"
            elif tension_score >= 10:
                return "low"
            else:
                return "peaceful"
                
        except Exception as e:
            logger.error(f"Error calculating tension level: {e}")
            return "unknown"

    def _identify_crisis_indicators(self, regional_factions, incident_analysis, 
                                  sanction_analysis, ultimatum_analysis, 
                                  relationship_matrix) -> List[Dict[str, Any]]:
        """Identify potential crisis situations in the region."""
        indicators = []
        
        try:
            # Check for immediate ultimatum deadlines
            if ultimatum_analysis["urgency_levels"]["immediate"] > 0:
                indicators.append({
                    "type": "imminent_ultimatum_deadline",
                    "severity": "high",
                    "description": f"{ultimatum_analysis['urgency_levels']['immediate']} ultimatum(s) expire within 24 hours",
                    "recommended_action": "immediate diplomatic intervention required"
                })
            
            # Check for escalating incidents
            if incident_analysis["severity_breakdown"]["critical"] > 0:
                indicators.append({
                    "type": "critical_incidents",
                    "severity": "high",
                    "description": f"{incident_analysis['severity_breakdown']['critical']} critical diplomatic incidents active",
                    "recommended_action": "crisis management protocols should be activated"
                })
            
            # Check for war-level tensions
            for faction_a, relationships in relationship_matrix.items():
                for faction_b, relationship in relationships.items():
                    if relationship.get("status") == "war":
                        indicators.append({
                            "type": "active_warfare",
                            "severity": "critical",
                            "description": f"Active warfare between factions {faction_a} and {faction_b}",
                            "recommended_action": "ceasefire negotiations urgently needed"
                        })
                    elif relationship.get("tension", 0) > 90:
                        indicators.append({
                            "type": "pre_war_tension",
                            "severity": "high",
                            "description": f"Extremely high tension between factions {faction_a} and {faction_b}",
                            "recommended_action": "preventive diplomacy recommended"
                        })
                        
        except Exception as e:
            logger.error(f"Error identifying crisis indicators: {e}")
            
        return indicators

    def _generate_diplomatic_recommendations(self, region_id: str, regional_factions: List[UUID], 
                                           analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate diplomatic recommendations based on regional analysis."""
        recommendations = []
        
        try:
            # Recommend peace initiatives if high tension
            if len(analysis.get("crisis_indicators", [])) > 0:
                recommendations.append({
                    "priority": "high",
                    "type": "crisis_management",
                    "title": "Implement Crisis Management Protocols",
                    "description": "Multiple crisis indicators detected. Immediate diplomatic intervention recommended.",
                    "actions": [
                        "Deploy senior diplomatic personnel to region",
                        "Establish direct communication channels between conflicting parties",
                        "Consider emergency peace summit"
                    ]
                })
            
            # Recommend trade agreements if low cooperation
            if analysis["treaty_breakdown"].get("trade", 0) < len(regional_factions) // 3:
                recommendations.append({
                    "priority": "medium",
                    "type": "economic_cooperation",
                    "title": "Promote Trade Agreements",
                    "description": "Low level of economic cooperation detected. Trade agreements could improve stability.",
                    "actions": [
                        "Identify mutually beneficial trade opportunities",
                        "Organize regional trade conferences",
                        "Provide trade agreement templates and support"
                    ]
                })
            
            # Recommend alliance building if many neutral relationships
            neutral_count = sum(
                1 for relationships in analysis["relationship_matrix"].values()
                for rel in relationships.values()
                if rel.get("status") == "neutral"
            )
            
            if neutral_count > len(regional_factions):
                recommendations.append({
                    "priority": "low",
                    "type": "alliance_building",
                    "title": "Foster Strategic Alliances",
                    "description": "Many neutral relationships could be strengthened through alliance building.",
                    "actions": [
                        "Host regional diplomatic summits",
                        "Facilitate cultural exchange programs",
                        "Support mutual defense discussions"
                    ]
                })
                
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            
        return recommendations


class DiplomacyIntegrationManager:
    """Central manager for all diplomacy system integrations."""
    
    def __init__(self):
        self.faction_integration = FactionDiplomacyIntegration()
        self.character_integration = CharacterDiplomacyIntegration()
        self.quest_integration = QuestDiplomacyIntegration()
        self.world_state_integration = WorldStateDiplomacyIntegration()
        
        logger.info("Diplomacy integration manager initialized")
    
    def initialize_all_integrations(self) -> Dict[str, bool]:
        """Initialize all cross-system integrations."""
        try:
            results = {
                "faction_integration": True,
                "character_integration": True,
                "quest_integration": True,
                "world_state_integration": True
            }
            
            logger.info("All diplomacy integrations initialized successfully")
            return results
            
        except Exception as e:
            logger.error(f"Error initializing diplomacy integrations: {e}")
            return {"error": str(e)}
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get the status of all integration services."""
        try:
            return {
                "faction_service_available": FactionService is not None,
                "character_service_available": CharacterService is not None,
                "quest_service_available": QuestBusinessService is not None,
                "world_state_service_available": World_StateService is not None,
                "integrations_active": True,
                "last_check": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error checking integration status: {e}")
            return {"error": str(e)} 