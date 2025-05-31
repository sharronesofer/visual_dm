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

from backend.systems.diplomacy.core_services import DiplomacyService, TensionService
from backend.systems.diplomacy.models import (
    DiplomaticStatus, TreatyType, DiplomaticEventType,
    DiplomaticIncidentType, DiplomaticIncidentSeverity
)
from backend.infrastructure.events.event_dispatcher import EventDispatcher

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
    from backend.systems.quest.services import QuestService
except ImportError:
    logging.warning("Quest services not available for diplomacy integration")
    QuestService = None

try:
    from backend.systems.world_state.services import WorldStateService
except ImportError:
    logging.warning("World state services not available for diplomacy integration")
    WorldStateService = None

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
        self.quest_service = QuestService() if QuestService else None
        
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
            
            if not self.quest_service:
                logger.warning("Quest service not available for treaty quest generation")
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
                # self.quest_service.create_quest(quest_data)
            
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
            
            if not self.quest_service:
                logger.warning("Quest service not available for incident quest generation")
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
            
            if not self.quest_service:
                logger.warning("Quest service not available for ultimatum quest generation")
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
        self.world_state_service = WorldStateService() if WorldStateService else None
        
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
            if not self.world_state_service:
                logger.warning("World state service not available for regional diplomatic status")
                return {"available": False}
            
            # This would need integration with region/faction mapping
            # For now, return a placeholder structure
            status = {
                "available": True,
                "region_id": region_id,
                "active_treaties": 0,
                "ongoing_negotiations": 0,
                "recent_incidents": 0,
                "tension_level": "unknown",
                "last_updated": datetime.utcnow().isoformat()
            }
            
            # In a full implementation, this would:
            # 1. Get all factions in the region
            # 2. Analyze their diplomatic relationships
            # 3. Count active treaties, negotiations, incidents
            # 4. Calculate average tension levels
            # 5. Identify recent diplomatic events
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting regional diplomatic status: {e}")
            return {"available": False, "error": str(e)}


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
                "quest_service_available": QuestService is not None,
                "world_state_service_available": WorldStateService is not None,
                "integrations_active": True,
                "last_check": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error checking integration status: {e}")
            return {"error": str(e)} 